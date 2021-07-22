// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package formats

import (
	"microsoft.com/pkggen/internal/shell"
	"microsoft.com/pkggen/internal/systemdependency"
)

// TarGzipType represents the tar.gz format
const TarGzipType = "tar.gz"

// TarGzip implements Converter interface to convert a RAW image into a tar.gz file
type TarGzip struct {
}

// Convert converts the image in the tar.gz format
func (t *TarGzip) Convert(input, output string, isInputFile bool) (err error) {
	const squashErrors = false

	tool, err := systemdependency.GzipTool()
	if err != nil {
		return
	}

	if isInputFile {
		err = shell.ExecuteLive(squashErrors, "tar", "-I", tool, "-cf", output, input)
	} else {
		err = shell.ExecuteLive(squashErrors, "tar", "-I", tool, "-cf", output, "-C", input, ".")
	}

	return
}

// Extension returns the filetype extension produced by this converter.
func (t *TarGzip) Extension() string {
	return TarGzipType
}

// NewTarGzip returns a new TarGzip format encoder
func NewTarGzip() *TarGzip {
	return &TarGzip{}
}
