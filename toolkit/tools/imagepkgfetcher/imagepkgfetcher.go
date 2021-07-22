// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package main

import (
	"os"
	"strings"

	"gopkg.in/alecthomas/kingpin.v2"
	"microsoft.com/pkggen/imagegen/configuration"
	"microsoft.com/pkggen/imagegen/installutils"
	"microsoft.com/pkggen/internal/exe"
	"microsoft.com/pkggen/internal/logger"
	"microsoft.com/pkggen/internal/packagerepo/repocloner"
	"microsoft.com/pkggen/internal/packagerepo/repocloner/rpmrepocloner"
	"microsoft.com/pkggen/internal/packagerepo/repoutils"
	"microsoft.com/pkggen/internal/pkggraph"
	"microsoft.com/pkggen/internal/pkgjson"
)

var (
	app = kingpin.New("imagepkgfetcher", "A tool to download a provided list of packages into a given directory.")

	configFile = exe.InputFlag(app, "Path to the image config file.")
	outDir     = exe.OutputDirFlag(app, "Directory to download packages into.")

	baseDirPath    = app.Flag("base-dir", "Base directory for relative file paths from the config. Defaults to config's directory.").ExistingDir()
	existingRpmDir = app.Flag("rpm-dir", "Directory that contains already built RPMs. Should contain top level directories for architecture.").Required().ExistingDir()
	tmpDir         = app.Flag("tmp-dir", "Directory to store temporary files while downloading.").Required().String()

	workertar            = app.Flag("tdnf-worker", "Full path to worker_chroot.tar.gz").Required().ExistingFile()
	repoFiles            = app.Flag("repo-file", "Full path to a repo file").Required().ExistingFiles()
	useUpdateRepo        = app.Flag("use-update-repo", "Pull packages from the upstream update repo").Bool()
	usePreviewRepo       = app.Flag("use-preview-repo", "Pull packages from the upstream preview repo").Bool()
	disableUpstreamRepos = app.Flag("disable-upstream-repos", "Disables pulling packages from upstream repos").Bool()

	tlsClientCert = app.Flag("tls-cert", "TLS client certificate to use when downloading files.").String()
	tlsClientKey  = app.Flag("tls-key", "TLS client key to use when downloading files.").String()

	externalOnly = app.Flag("external-only", "Only clone packages not provided locally.").Bool()
	inputGraph   = app.Flag("package-graph", "Path to the graph file to read, only needed if external-only is set.").ExistingFile()

	inputSummaryFile  = app.Flag("input-summary-file", "Path to a file with the summary of packages cloned to be restored").String()
	outputSummaryFile = app.Flag("output-summary-file", "Path to save the summary of packages cloned").String()

	logFile  = exe.LogFileFlag(app)
	logLevel = exe.LogLevelFlag(app)
)

func main() {
	app.Version(exe.ToolkitVersion)
	kingpin.MustParse(app.Parse(os.Args[1:]))
	logger.InitBestEffort(*logFile, *logLevel)

	if *externalOnly && strings.TrimSpace(*inputGraph) == "" {
		logger.Log.Fatal("input-graph must be provided if external-only is set.")
	}

	cloner := rpmrepocloner.New()
	err := cloner.Initialize(*outDir, *tmpDir, *workertar, *existingRpmDir, *useUpdateRepo, *usePreviewRepo, *repoFiles)
	if err != nil {
		logger.Log.Panicf("Failed to initialize RPM repo cloner. Error: %s", err)
	}
	defer cloner.Close()

	if !*disableUpstreamRepos {
		tlsKey, tlsCert := strings.TrimSpace(*tlsClientKey), strings.TrimSpace(*tlsClientCert)
		err = cloner.AddNetworkFiles(tlsCert, tlsKey)
		if err != nil {
			logger.Log.Panicf("Failed to customize RPM repo cloner. Error: %s", err)
		}
	}

	if strings.TrimSpace(*inputSummaryFile) != "" {
		// If an input summary file was provided, simply restore the cache using the file.
		err = repoutils.RestoreClonedRepoContents(cloner, *inputSummaryFile)
	} else {
		err = cloneSystemConfigs(cloner, *configFile, *baseDirPath, *externalOnly, *inputGraph)
	}

	if err != nil {
		logger.Log.Panicf("Failed to clone RPM repo. Error: %s", err)
	}

	logger.Log.Info("Configuring downloaded RPMs as a local repository")
	err = cloner.ConvertDownloadedPackagesIntoRepo()
	if err != nil {
		logger.Log.Panicf("Failed to convert downloaded RPMs into a repo. Error: %s", err)
	}

	if strings.TrimSpace(*outputSummaryFile) != "" {
		err = repoutils.SaveClonedRepoContents(cloner, *outputSummaryFile)
		logger.PanicOnError(err, "Failed to save cloned repo contents")
	}
}

func cloneSystemConfigs(cloner repocloner.RepoCloner, configFile, baseDirPath string, externalOnly bool, inputGraph string) (err error) {
	const cloneDeps = true

	cfg, err := configuration.LoadWithAbsolutePaths(configFile, baseDirPath)
	if err != nil {
		return
	}

	packageVersionsInConfig, err := installutils.PackageNamesFromConfig(cfg)
	if err != nil {
		return
	}

	// Add kernel packages from KernelOptions
	packageVersionsInConfig = append(packageVersionsInConfig, installutils.KernelPackages(cfg)...)

	if externalOnly {
		packageVersionsInConfig, err = filterExternalPackagesOnly(packageVersionsInConfig, inputGraph)
		if err != nil {
			return
		}
	}

	// Add any packages required by the install tools
	packageVersionsInConfig = append(packageVersionsInConfig, installutils.GetRequiredPackagesForInstall()...)

	logger.Log.Infof("Cloning: %v", packageVersionsInConfig)
	err = cloner.Clone(cloneDeps, packageVersionsInConfig...)
	return
}

// filterExternalPackagesOnly returns the subset of packageVersionsInConfig that only contains external packages.
func filterExternalPackagesOnly(packageVersionsInConfig []*pkgjson.PackageVer, inputGraph string) (filteredPackages []*pkgjson.PackageVer, err error) {
	dependencyGraph := pkggraph.NewPkgGraph()
	err = pkggraph.ReadDOTGraphFile(dependencyGraph, inputGraph)
	if err != nil {
		return
	}

	for _, pkgVer := range packageVersionsInConfig {
		pkgNode, _ := dependencyGraph.FindBestPkgNode(pkgVer)

		// There are two ways an external package will be represented by pkgNode.
		// 1) pkgNode may be nil. This is possible if the package is never consumed during the build phase,
		//    which means it will not be in the graph.
		// 2) pkgNode will be of 'StateUnresolved'. This will be the case if a local package has it listed as
		//    a Requires or BuildRequires.
		if pkgNode == nil || pkgNode.RunNode.State == pkggraph.StateUnresolved {
			filteredPackages = append(filteredPackages, pkgVer)
		}
	}

	return
}
