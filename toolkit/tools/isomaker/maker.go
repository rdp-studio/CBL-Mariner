// Copyright Microsoft Corporation.
// Licensed under the MIT License.

package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"

	"github.com/cavaliercoder/go-cpio"
	"github.com/klauspost/pgzip"
	"microsoft.com/pkggen/imagegen/configuration"
	"microsoft.com/pkggen/internal/file"
	"microsoft.com/pkggen/internal/jsonutils"
	"microsoft.com/pkggen/internal/logger"
	"microsoft.com/pkggen/internal/shell"
)

const (
	efiBootImgPathRelativeToIsoRoot = "boot/grub2/efiboot.img"
	initrdEFIBootDirectoryPath      = "boot/efi/EFI/BOOT"
	isoRootArchDependentDirPath     = "assets/isomaker/iso_root_arch-dependent_files"
)

// IsoMaker builds ISO images and populates them with packages and files required by the installer.
type IsoMaker struct {
	unattendedInstall  bool                 // Flag deciding if the installer should run in unattended mode.
	config             configuration.Config // Configuration for the built ISO image and its installer.
	configSubDirNumber int                  // Current number for the subdirectories storing files mentioned in the config.
	baseDirPath        string               // Base directory for config's relative paths.
	buildDirPath       string               // Path to the temporary build directory.
	configFilePath     string               // Path to the configuration JSON.
	efiBootImgPath     string               // Path to the efiboot.img file needed to boot the ISO installer.
	fetchedRepoDirPath string               // Path to the directory containing an RPM repository with all packages required by the ISO installer.
	initrdPath         string               // Path to ISO's initrd file.
	outputDirPath      string               // Path to the output ISO directory.
	releaseVersion     string               // Current Mariner release version.
	resourcesDirPath   string               // Path to the 'resources' directory.
	imageNameTag       string               // Optional user-supplied tag appended to the generated ISO's name.

	isoMakerCleanUpTasks []func() // List of clean-up tasks to perform at the end of the ISO generation process.
}

// NewIsoMaker returns a new ISO maker.
func NewIsoMaker(unattendedInstall bool, baseDirPath, buildDirPath, releaseVersion, resourcesDirPath, configFilePath, initrdPath, isoRepoDirPath, outputDir, imageNameTag string) *IsoMaker {
	if baseDirPath == "" {
		baseDirPath = filepath.Dir(configFilePath)
	}
	if imageNameTag != "" {
		imageNameTag = "-" + imageNameTag
	}

	return &IsoMaker{
		unattendedInstall:  unattendedInstall,
		baseDirPath:        baseDirPath,
		buildDirPath:       buildDirPath,
		initrdPath:         initrdPath,
		releaseVersion:     releaseVersion,
		resourcesDirPath:   resourcesDirPath,
		configFilePath:     configFilePath,
		fetchedRepoDirPath: isoRepoDirPath,
		outputDirPath:      outputDir,
		imageNameTag:       imageNameTag,
	}
}

// Make builds the ISO image to 'buildDirPath' with the packages included in the config JSON.
func (im *IsoMaker) Make() {
	defer im.isoMakerCleanUp()

	im.readAndVerifyConfig()

	im.initializePaths()

	im.prepareWorkDirectory()

	im.createIsoRpmsRepo()

	im.prepareIsoBootLoaderFilesAndFolders()

	im.buildIsoImage()
}

func (im *IsoMaker) buildIsoImage() {
	isoImageFilePath := im.buildIsoImageFilePath()

	logger.Log.Infof("Generating ISO image under '%s'.", isoImageFilePath)

	// For detailed parameter explanation see: https://linux.die.net/man/8/mkisofs.
	// Mkisofs requires all argument paths to be relative to the input directory.
	mkisofsArgs := []string{
		// General mkisofs parameters.
		"-R", "-l", "-D", "-o", isoImageFilePath,

		// BIOS bootloader, params suggested by https://wiki.syslinux.org/wiki/index.php?title=ISOLINUX.
		"-b", "isolinux/isolinux.bin", "-c", "isolinux/boot.cat", "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",

		// UEFI bootloader.
		"-eltorito-alt-boot", "-e", efiBootImgPathRelativeToIsoRoot, "-no-emul-boot",

		// Directory to convert to an ISO.
		im.buildDirPath,
	}

	shell.MustExecuteLive("mkisofs", mkisofsArgs...)
}

// prepareIsoBootLoaderFilesAndFolders copies the files required by the ISO's bootloader
func (im *IsoMaker) prepareIsoBootLoaderFilesAndFolders() {
	im.setUpIsoGrub2Bootloader()

	im.createVmlinuzImage()

	im.copyInitrd()
}

// copyInitrd copies a pre-built initrd into the isolinux folder.
func (im *IsoMaker) copyInitrd() {
	initrdDestinationPath := filepath.Join(im.buildDirPath, "isolinux/initrd.img")

	logger.Log.Debugf("Copying initrd from '%s'.", im.initrdPath)

	file.Copy(im.initrdPath, initrdDestinationPath)
}

// setUpIsoGrub2BootLoader prepares an efiboot.img containing Grub2,
// which is booted in case of an UEFI boot of the ISO image.
func (im *IsoMaker) setUpIsoGrub2Bootloader() {
	const (
		blockSizeInBytes     = 1024 * 1024
		numberOfBlocksToCopy = 3
	)

	logger.Log.Info("Preparing ISO's bootloaders.")

	ddArgs := []string{
		"if=/dev/zero",                                // Zero device to read a stream of zeroed bytes from.
		fmt.Sprintf("of=%s", im.efiBootImgPath),       // Output file.
		fmt.Sprintf("bs=%d", blockSizeInBytes),        // Size of one copied block. Used together with "count".
		fmt.Sprintf("count=%d", numberOfBlocksToCopy), // Number of blocks to copy to the output file.
	}
	logger.Log.Debugf("Creating an empty '%s' file of %d bytes.", im.efiBootImgPath, blockSizeInBytes*numberOfBlocksToCopy)
	shell.MustExecuteLive("dd", ddArgs...)

	logger.Log.Debugf("Formatting '%s' as an MS-DOS filesystem.", im.efiBootImgPath)
	shell.MustExecuteLive("mkdosfs", im.efiBootImgPath)

	efiBootImgTempMountDir := filepath.Join(im.buildDirPath, "efiboot_temp")
	logger.Log.Tracef("Creating temporary mount directory '%s'.", efiBootImgTempMountDir)
	logger.PanicOnError(os.Mkdir(efiBootImgTempMountDir, os.ModePerm))

	defer func() {
		logger.Log.Debugf("Removing '%s'.", efiBootImgTempMountDir)
		logger.PanicOnError(os.RemoveAll(efiBootImgTempMountDir), "Failed to remove temporary mount directory '%s'.", efiBootImgTempMountDir)
	}()

	mountArgs := []string{
		"-o",                   // Indicates we're passing options to "mount". Needed to mount a loop device.
		"loop",                 // Indicates we'd like to mount a loop device. We let the system choose a free /dev/loop* device.
		im.efiBootImgPath,      // Efiboot.img file we'd like to mount to act like a block-based device.
		efiBootImgTempMountDir, // Path to mount the image to.
	}
	logger.Log.Debugf("Mounting '%s' to '%s' to copy EFI modules required to boot grub2.", im.efiBootImgPath, efiBootImgTempMountDir)
	shell.MustExecuteLive("mount", mountArgs...)

	defer func() {
		logger.Log.Debugf("Unmounting '%s'.", efiBootImgTempMountDir)
		logger.PanicOnError(syscall.Unmount(efiBootImgTempMountDir, 0), "Failed to unmount '%s'.", efiBootImgTempMountDir)
	}()

	logger.Log.Debug("Copying EFI modules into efiboot.img.")
	// Copy Shim (boot<arch>64.efi) and grub2 (grub<arch>64.efi)
	if runtime.GOARCH == "arm64" {
		im.copyShimFromInitrd(efiBootImgTempMountDir, "bootaa64.efi", "grubaa64.efi")
	} else {
		im.copyShimFromInitrd(efiBootImgTempMountDir, "bootx64.efi", "grubx64.efi")
	}
}

func (im *IsoMaker) copyShimFromInitrd(efiBootImgTempMountDir, bootBootloaderFile, grubBootloaderFile string) {
	bootDirPath := filepath.Join(efiBootImgTempMountDir, "EFI", "BOOT")

	initrdBootBootloaderFilePath := filepath.Join(initrdEFIBootDirectoryPath, bootBootloaderFile)
	buildDirBootEFIFilePath := filepath.Join(bootDirPath, bootBootloaderFile)
	im.extractFromInitrdAndCopy(initrdBootBootloaderFilePath, buildDirBootEFIFilePath)

	initrdGrubBootloaderFilePath := filepath.Join(initrdEFIBootDirectoryPath, grubBootloaderFile)
	buildDirGrubEFIFilePath := filepath.Join(bootDirPath, grubBootloaderFile)
	im.extractFromInitrdAndCopy(initrdGrubBootloaderFilePath, buildDirGrubEFIFilePath)

	im.applyRufusWorkaround(bootBootloaderFile, grubBootloaderFile)
}

// Rufus ISO-to-USB converter has a limitation where it will only copy the boot<arch>64.efi binary from a given efi*.img
// archive into the standard UEFI EFI/BOOT folder instead of extracting the whole archive as per the El Torito ISO
// specification.
//
// Most distros (including ours) use a 2 stage bootloader flow (shim->grub->kernel). Since the Rufus limitation only
// copies the 1st stage to EFI/BOOT/boot<arch>64.efi, it cannot find the 2nd stage bootloader (grub<arch>64.efi) which should
// be in the same directory: EFI/BOOT/grub<arch>64.efi. This causes the USB installation to fail to boot.
//
// Rufus prioritizes the presence of an EFI folder on the ISO disk over extraction of the efi*.img archive.
// So to workaround the limitation, create an EFI folder and make a duplicate copy of the bootloader files
// in EFI/Boot so Rufus doesn't attempt to extract the efi*.img in the first place.
func (im *IsoMaker) applyRufusWorkaround(bootBootloaderFile, grubBootloaderFile string) {
	const buildDirBootEFIDirectoryPath = "efi/boot"

	initrdBootloaderFilePath := filepath.Join(initrdEFIBootDirectoryPath, bootBootloaderFile)
	buildDirBootEFIUsbFilePath := filepath.Join(im.buildDirPath, buildDirBootEFIDirectoryPath, bootBootloaderFile)
	im.extractFromInitrdAndCopy(initrdBootloaderFilePath, buildDirBootEFIUsbFilePath)

	initrdGrubEFIFilePath := filepath.Join(initrdEFIBootDirectoryPath, grubBootloaderFile)
	buildDirGrubEFIUsbFilePath := filepath.Join(im.buildDirPath, buildDirBootEFIDirectoryPath, grubBootloaderFile)
	im.extractFromInitrdAndCopy(initrdGrubEFIFilePath, buildDirGrubEFIUsbFilePath)
}

// createVmlinuzImage builds the 'vmlinuz' file containing the Linux kernel
// ran by the ISO bootloader.
func (im *IsoMaker) createVmlinuzImage() {
	const bootKernelFile = "boot/vmlinuz"

	vmlinuzFilePath := filepath.Join(im.buildDirPath, "isolinux/vmlinuz")

	// In order to select the correct kernel for isolinux, open the initrd archive
	// and extract the vmlinuz file in it. An initrd is a gzip of a cpio archive.
	//
	im.extractFromInitrdAndCopy(bootKernelFile, vmlinuzFilePath)
}

// createIsoRpmsRepo initializes the RPMs repo on the ISO image
// later accessed by the ISO installer.
func (im *IsoMaker) createIsoRpmsRepo() {
	isoRrpmsRepoDirPath := filepath.Join(im.buildDirPath, "RPMS")

	logger.Log.Debugf("Creating ISO RPMs repo under '%s'.", isoRrpmsRepoDirPath)

	logger.PanicOnError(os.MkdirAll(isoRrpmsRepoDirPath, os.ModePerm), "Failed to mkdir '%s'.", isoRrpmsRepoDirPath)

	fetchedRepoDirContentsPath := filepath.Join(im.fetchedRepoDirPath, "*")
	recursiveCopyDereferencingLinks(fetchedRepoDirContentsPath, isoRrpmsRepoDirPath)
}

// prepareWorkDirectory makes sure we start with a clean directory
// under "im.buildDirPath". The work directory will contain the contents of the ISO image.
func (im *IsoMaker) prepareWorkDirectory() {
	logger.Log.Infof("Building ISO under '%s'.", im.buildDirPath)

	exists, err := file.DirExists(im.buildDirPath)
	logger.PanicOnError(err, "Failed while checking if directory '%s' exists.", im.buildDirPath)
	if exists {
		logger.Log.Warningf("Unexpected: temporary ISO build path '%s' exists. Removing.", im.buildDirPath)
		logger.PanicOnError(os.RemoveAll(im.buildDirPath), "Failed while removing directory '%s'.", im.buildDirPath)
	}

	logger.PanicOnError(os.Mkdir(im.buildDirPath, os.ModePerm), "Failed while creating directory '%s'.", im.buildDirPath)

	im.deferIsoMakerCleanUp(func() {
		logger.Log.Debugf("Removing '%s'.", im.buildDirPath)

		logger.PanicOnError(os.RemoveAll(im.buildDirPath), "Failed to remove '%s'.", im.buildDirPath)
	})

	im.copyStaticIsoRootFiles()

	im.copyArchitectureDependentIsoRootFiles()

	im.copyAndRenameConfigFiles()
}

// copyStaticIsoRootFiles copies architecture-independent files from the
// Mariner repo directories.
func (im *IsoMaker) copyStaticIsoRootFiles() {
	staticIsoRootFilesPath := filepath.Join(im.resourcesDirPath, "assets/isomaker/iso_root_static_files/*")

	logger.Log.Debugf("Copying static ISO root files from '%s'.", staticIsoRootFilesPath)

	recursiveCopyDereferencingLinks(staticIsoRootFilesPath, im.buildDirPath)
}

// copyArchitectureDependentIsoRootFiles copies the pre-built UEFI modules required
// to boot the ISO image.
func (im *IsoMaker) copyArchitectureDependentIsoRootFiles() {
	architectureDependentFilesDirectory := filepath.Join(im.resourcesDirPath, isoRootArchDependentDirPath, runtime.GOARCH, "*")

	logger.Log.Debugf("Copying architecture-dependent (%s) ISO root files from '%s'.", runtime.GOARCH, architectureDependentFilesDirectory)

	recursiveCopyDereferencingLinks(architectureDependentFilesDirectory, im.buildDirPath)
}

// copyAndRenameConfigFiles takes care of copying the config JSON along with all the files
// required by the installed system.
func (im *IsoMaker) copyAndRenameConfigFiles() {
	const configDirName = "config"

	logger.Log.Debugf("Copying the config JSON and required files to the ISO's root.")

	configFilesAbsDirPath := filepath.Join(im.buildDirPath, configDirName)
	logger.PanicOnError(os.Mkdir(configFilesAbsDirPath, os.ModePerm), "Failed to create ISO's config files directory under '%s'.", configFilesAbsDirPath)

	im.copyAndRenameAdditionalFiles(configFilesAbsDirPath)
	im.copyAndRenamePackagesJSONs(configFilesAbsDirPath)
	im.copyAndRenamePostInstallScripts(configFilesAbsDirPath)
	im.copyAndRenameSSHPublicKeys(configFilesAbsDirPath)
	im.saveConfigJSON(configFilesAbsDirPath)
}

// copyAndRenameAdditionalFiles will copy all additional files into an
// ISO directory to make them available to the installer.
// Each file gets placed in a separate directory to avoid potential name conflicts and
// the config gets updated with the new ISO paths.
func (im *IsoMaker) copyAndRenameAdditionalFiles(configFilesAbsDirPath string) {
	const additionalFilesSubDirName = "additionalfiles"

	for i := range im.config.SystemConfigs {
		systemConfig := &im.config.SystemConfigs[i]

		absAdditionalFiles := make(map[string]string)
		for localAbsFilePath, installedSystemAbsFilePath := range systemConfig.AdditionalFiles {
			isoRelativeFilePath := im.copyFileToConfigRoot(configFilesAbsDirPath, additionalFilesSubDirName, localAbsFilePath)
			absAdditionalFiles[isoRelativeFilePath] = installedSystemAbsFilePath
		}
		systemConfig.AdditionalFiles = absAdditionalFiles
	}
}

// copyAndRenamePackagesJSONs will copy all package list JSONs into an
// ISO directory to make them available to the installer.
// Each file gets placed in a separate directory to avoid potential name conflicts and
// the config gets updated with the new ISO paths.
func (im *IsoMaker) copyAndRenamePackagesJSONs(configFilesAbsDirPath string) {
	const packagesSubDirName = "packages"

	for _, systemConfig := range im.config.SystemConfigs {
		for i, localPackagesAbsFilePath := range systemConfig.PackageLists {
			isoPackagesRelativeFilePath := im.copyFileToConfigRoot(configFilesAbsDirPath, packagesSubDirName, localPackagesAbsFilePath)

			systemConfig.PackageLists[i] = isoPackagesRelativeFilePath
		}
	}
}

// copyAndRenamePostInstallScripts will copy all post-install scripts into an
// ISO directory to make them available to the installer.
// Each file gets placed in a separate directory to avoid potential name conflicts and
// the config gets updated with the new ISO paths.
func (im *IsoMaker) copyAndRenamePostInstallScripts(configFilesAbsDirPath string) {
	const postInstallScriptsSubDirName = "postinstallscripts"

	for _, systemConfig := range im.config.SystemConfigs {
		for i, localScriptAbsFilePath := range systemConfig.PostInstallScripts {
			isoScriptRelativeFilePath := im.copyFileToConfigRoot(configFilesAbsDirPath, postInstallScriptsSubDirName, localScriptAbsFilePath.Path)

			systemConfig.PostInstallScripts[i].Path = isoScriptRelativeFilePath
		}
	}
}

// copyAndRenameSSHPublicKeys will copy all SSH public keys into an
// ISO directory to make them available to the installer.
// Each file gets placed in a separate directory to avoid potential name conflicts and
// the config gets updated with the new ISO paths.
func (im *IsoMaker) copyAndRenameSSHPublicKeys(configFilesAbsDirPath string) {
	const sshPublicKeysSubDirName = "sshpublickeys"

	for _, systemConfig := range im.config.SystemConfigs {
		for _, user := range systemConfig.Users {
			for i, localSSHPublicKeyAbsPath := range user.SSHPubKeyPaths {
				isoSSHPublicKeyRelativeFilePath := im.copyFileToConfigRoot(configFilesAbsDirPath, sshPublicKeysSubDirName, localSSHPublicKeyAbsPath)

				user.SSHPubKeyPaths[i] = isoSSHPublicKeyRelativeFilePath
			}
		}
	}
}

// saveConfigJSON will save the modified config JSON into an
// ISO directory to make it available to the installer.
func (im *IsoMaker) saveConfigJSON(configFilesAbsDirPath string) {
	const (
		attendedInstallConfigFileName   = "attended_config.json"
		unattendedInstallConfigFileName = "unattended_config.json"
	)

	isoConfigFileAbsPath := filepath.Join(configFilesAbsDirPath, attendedInstallConfigFileName)
	if im.unattendedInstall {
		isoConfigFileAbsPath = filepath.Join(configFilesAbsDirPath, unattendedInstallConfigFileName)
	}

	logger.PanicOnError(jsonutils.WriteJSONFile(isoConfigFileAbsPath, &im.config), "Failed to save config JSON to '%s'.", isoConfigFileAbsPath)
}

// copyFileToConfigRoot copies a single file to its own, numbered subdirectory to avoid name conflicts
// and returns the realitve path to the file for the sake of config updates for the installer.
func (im *IsoMaker) copyFileToConfigRoot(configFilesAbsDirPath, configFilesSubDirName, localAbsFilePath string) string {
	fileName := filepath.Base(localAbsFilePath)
	configFileSubDirRelativePath := fmt.Sprintf("%s/%d", configFilesSubDirName, im.configSubDirNumber)
	configFileSubDirAbsPath := filepath.Join(configFilesAbsDirPath, configFileSubDirRelativePath)

	logger.PanicOnError(os.MkdirAll(configFileSubDirAbsPath, os.ModePerm), "Failed to create ISO's config subdirectory '%s'.", configFileSubDirAbsPath)

	isoRelativeFilePath := filepath.Join(configFileSubDirRelativePath, fileName)
	isoAbsFilePath := filepath.Join(configFilesAbsDirPath, isoRelativeFilePath)

	logger.Log.Tracef("Copying file to ISO's config root '%s' from '%s'.", isoAbsFilePath, localAbsFilePath)

	logger.PanicOnError(file.Copy(localAbsFilePath, isoAbsFilePath), "Failed to copy file to ISO's config root '%s' from '%s'.", isoAbsFilePath, localAbsFilePath)

	im.configSubDirNumber++

	return isoRelativeFilePath
}

// initializePaths initializes absolute, global directory paths used by multiple other functions.
func (im *IsoMaker) initializePaths() {
	var err error
	im.buildDirPath, err = filepath.Abs(im.buildDirPath)
	logger.PanicOnError(err, "Failed while retrieving absolute path from source root path: '%s'.", im.buildDirPath)

	im.efiBootImgPath = filepath.Join(im.buildDirPath, efiBootImgPathRelativeToIsoRoot)
}

// buildIsoImageFilePath gets the output ISO file path from the config JSON file name
// and the image build environment.
func (im *IsoMaker) buildIsoImageFilePath() string {
	imageBaseName := strings.TrimSuffix(filepath.Base(im.configFilePath), ".json")
	isoImageFileName := fmt.Sprintf("%v-%v%v.iso", imageBaseName, im.releaseVersion, im.imageNameTag)

	return filepath.Join(im.outputDirPath, isoImageFileName)
}

// deferIsoMakerCleanUp accepts clean-up tasks to be ran when the entire
// build process has finished, NOT at the end of the current scope.
func (im *IsoMaker) deferIsoMakerCleanUp(cleanUpTask func()) {
	im.isoMakerCleanUpTasks = append(im.isoMakerCleanUpTasks, cleanUpTask)
}

// isoMakerCleanUp runs all clean-up tasks scheduled through "deferIsoMakerCleanUp".
// Tasks are ran in reverse order to how they were scheduled.
func (im *IsoMaker) isoMakerCleanUp() {
	// We defer again to run the tasks in the correct order AND so that a potential
	// panic from one of these doesn't prevent other ones from running.
	for _, cleanUpTask := range im.isoMakerCleanUpTasks {
		defer cleanUpTask()
	}
}

func (im *IsoMaker) readAndVerifyConfig() {
	config, err := configuration.LoadWithAbsolutePaths(im.configFilePath, im.baseDirPath)
	logger.PanicOnError(err, "Failed while reading config file from '%s' with base directory '%s'.", im.configFilePath, im.baseDirPath)

	if im.unattendedInstall && (len(config.SystemConfigs) > 1) && !config.DefaultSystemConfig.IsDefault {
		logger.Log.Panic("For unattended installation with more than one system configuration present you must select a default one with the [IsDefault] field.")
	}

	im.config = config
}

// recursiveCopyDereferencingLinks simulates the behavior of "cp -r -L".
func recursiveCopyDereferencingLinks(source string, target string) {
	err := os.MkdirAll(target, os.ModePerm)
	logger.PanicOnError(err)

	sourceToTarget := make(map[string]string)

	if filepath.Base(source) == "*" {
		filesToCopy, err := filepath.Glob(source)
		logger.PanicOnError(err)
		for _, file := range filesToCopy {
			sourceToTarget[file] = target
		}
	} else {
		sourceToTarget[source] = target
	}

	for sourcePath, targetPath := range sourceToTarget {
		shell.MustExecuteLive("cp", "-r", "-L", sourcePath, targetPath)
	}
}

func (im *IsoMaker) extractFromInitrdAndCopy(srcFileName, destFilePath string) {
	// Setup a series of io readers: initrd file -> parallelized gzip -> cpio

	logger.Log.Debugf("Searching for (%s) in initrd (%s) and copying to (%s)", srcFileName, im.initrdPath, destFilePath)

	initrdFile, err := os.Open(im.initrdPath)
	logger.PanicOnError(err)
	defer initrdFile.Close()

	gzipReader, err := pgzip.NewReader(initrdFile)
	logger.PanicOnError(err)
	cpioReader := cpio.NewReader(gzipReader)

	for {
		// Search through the headers until the source file is found
		var hdr *cpio.Header
		hdr, err = cpioReader.Next()
		if err == io.EOF {
			err = fmt.Errorf("did not find (%s) in initrd (%s)", srcFileName, im.initrdPath)
			logger.PanicOnError(err)
		}
		logger.PanicOnError(err)

		if strings.HasPrefix(hdr.Name, srcFileName) {
			logger.Log.Debugf("Found source file (%s) in initrd", srcFileName)
			// Source file found, copy it to destination
			err = os.MkdirAll(filepath.Dir(destFilePath), os.ModePerm)
			logger.PanicOnError(err)
			dstFile, err := os.Create(destFilePath)
			logger.PanicOnError(err)
			defer dstFile.Close()

			logger.Log.Debugf("Copying (%s) to (%s)", srcFileName, destFilePath)
			_, err = io.Copy(dstFile, cpioReader)
			logger.PanicOnError(err)
			break
		}
	}
}
