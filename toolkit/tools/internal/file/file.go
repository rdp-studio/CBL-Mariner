// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package file

import (
	"bufio"
	"crypto/sha1"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"microsoft.com/pkggen/internal/logger"
	"microsoft.com/pkggen/internal/shell"
)

// IsDir check if a given file path is a directory.
func IsDir(filePath string) (isDir bool, err error) {
	info, err := os.Stat(filePath)
	if err != nil {
		return
	}

	return info.IsDir(), nil
}

// IsFile returns true if the provided path is a file.
func IsFile(path string) (isFile bool, err error) {
	info, err := os.Stat(path)
	if err != nil {
		return
	}

	return !info.IsDir(), nil
}

// Move moves a file from src to dst. Will preserve permissions.
func Move(src, dst string) (err error) {
	const squashErrors = false

	src, err = filepath.Abs(src)
	if err != nil {
		logger.Log.Errorf("Failed to get absolute path for move source (%s).", src)
		return
	}

	dst, err = filepath.Abs(dst)
	if err != nil {
		logger.Log.Errorf("Failed to get absolute path for move destination (%s).", dst)
		return
	}

	if src == dst {
		logger.Log.Warnf("Skipping move. Source and destination are the same file (%s).", src)
		return
	}

	logger.Log.Debugf("Moving (%s) -> (%s)", src, dst)

	// Create the directory for the destination file
	err = os.MkdirAll(filepath.Dir(dst), os.ModePerm)
	if err != nil {
		logger.Log.Warnf("Could not create directory for destination file (%s)", dst)
		return
	}

	// use mv command so cross partition is handled
	err = shell.ExecuteLive(squashErrors, "mv", src, dst)
	return
}

// Copy copies a file from src to dst, creating directories for the destination if needed.
// dst is assumed to be a file and not a directory. Will preserve permissions.
func Copy(src, dst string) (err error) {
	return copyWithPermissions(src, dst, os.ModePerm, false, os.ModePerm)
}

// CopyAndChangeMode copies a file from src to dst, creating directories with the given access rights for the destination if needed.
// dst is assumed to be a file and not a directory. Will change the permissions to the given value.
func CopyAndChangeMode(src, dst string, dirmode os.FileMode, filemode os.FileMode) (err error) {
	return copyWithPermissions(src, dst, dirmode, true, filemode)
}

// readLines reads file under path and returns lines as strings and any error encountered
func ReadLines(path string) (lines []string, err error) {
	handle, err := os.Open(path)
	if err != nil {
		return
	}
	defer handle.Close()

	scanner := bufio.NewScanner(handle)

	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}

	return lines, scanner.Err()
}

// Create creates a new file with the provided Unix permissions
func Create(dst string, perm os.FileMode) (err error) {
	logger.Log.Debugf("Creating (%s) with mode (%v)", dst, perm)

	dstFile, err := os.OpenFile(dst, os.O_CREATE|os.O_EXCL, perm)
	if err != nil {
		return
	}
	defer dstFile.Close()
	return
}

// Write writes a string to the file dst.
func Write(data string, dst string) (err error) {
	logger.Log.Debugf("Writing to (%s)", dst)

	dstFile, err := os.Create(dst)
	if err != nil {
		return
	}
	defer dstFile.Close()

	_, err = dstFile.WriteString(data)
	return
}

// Append appends a string to the end of file dst.
func Append(data string, dst string) (err error) {
	logger.Log.Debugf("Appending to file (%s): (%s)", dst, data)

	dstFile, err := os.OpenFile(dst, os.O_APPEND|os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		return
	}
	defer dstFile.Close()

	_, err = dstFile.WriteString(data)
	return
}

// GenerateSHA1 calculates a sha1 of a file
func GenerateSHA1(path string) (hash string, err error) {
	file, err := os.Open(path)
	if err != nil {
		return
	}
	defer file.Close()

	sha1Generator := sha1.New()
	_, err = io.Copy(sha1Generator, file)
	if err != nil {
		return
	}

	rawHash := sha1Generator.Sum(nil)
	hash = hex.EncodeToString(rawHash)

	return
}

// GenerateSHA256 calculates a sha256 of a file
func GenerateSHA256(path string) (hash string, err error) {
	file, err := os.Open(path)
	if err != nil {
		return
	}
	defer file.Close()

	sha256Generator := sha256.New()
	_, err = io.Copy(sha256Generator, file)
	if err != nil {
		return
	}

	rawHash := sha256Generator.Sum(nil)
	hash = hex.EncodeToString(rawHash)

	return
}

// DirExists returns true if the directory exists,
// false otherwise.
func DirExists(path string) (exists bool, err error) {
	stat, err := os.Stat(path)
	if err == nil && stat.IsDir() {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return stat.IsDir(), err
}

// PathExists returns true if the path exists,
// false otherwise.
func PathExists(path string) (exists bool, err error) {
	_, err = os.Stat(path)
	if os.IsNotExist(err) {
		return false, nil
	}
	return (err == nil), err
}

// GetAbsPathWithBase converts 'inputPath' to an absolute path starting
// from 'baseDirPath', but only if it wasn't an absolute path in the first place.
func GetAbsPathWithBase(baseDirPath, inputPath string) string {
	if filepath.IsAbs(inputPath) {
		return inputPath
	}

	return filepath.Join(baseDirPath, inputPath)
}

// copyWithPermissions copies a file from src to dst, creating directories with the requested mode for the destination if needed.
// Depending on the changeMode parameter, it may also change the file mode.
func copyWithPermissions(src, dst string, dirmode os.FileMode, changeMode bool, filemode os.FileMode) (err error) {
	const squashErrors = false

	logger.Log.Debugf("Copying (%s) -> (%s)", src, dst)

	isSrcFile, err := IsFile(src)
	if err != nil {
		return
	}
	if !isSrcFile {
		return fmt.Errorf("source (%s) is not a file", src)
	}

	isDstExist, err := PathExists(dst)
	if err != nil {
		return err
	}
	if isDstExist {
		isDstDir, err := IsDir(dst)
		if err != nil {
			return err
		}
		if isDstDir {
			return fmt.Errorf("destination (%s) already exists and is a directory", dst)
		}
	}

	if !isDstExist {
		// Create destination directory if needed
		destDir := filepath.Dir(dst)
		err = os.MkdirAll(destDir, dirmode)
		if err != nil {
			return
		}
	}

	err = shell.ExecuteLive(squashErrors, "cp", "--preserve=mode", src, dst)
	if err != nil {
		return
	}

	if changeMode {
		logger.Log.Debugf("Calling chmod on (%s) with the mode (%v)", dst, filemode)
		err = os.Chmod(dst, filemode)
	}

	return
}
