// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// Json utilities

package jsonutils

import (
	"encoding/json"
	"io/ioutil"
	"os"

	"microsoft.com/pkggen/internal/logger"
)

const (
	defaultJsonFilePermission os.FileMode = 0664
)

// ReadJSONFile reads a .JSON file. Behaves as Go's built-in encoding/json.Unmarshal()
// but accepts a file path instead of a byte slice.
func ReadJSONFile(path string, data interface{}) error {
	jsonFile, err := os.Open(path)
	if err != nil {
		return err
	}
	defer jsonFile.Close()

	jsonData, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		return err
	}

	logger.Log.Tracef("Read %#x bytes of JSON data.", len(jsonData))

	return json.Unmarshal(jsonData, &data)
}

// WriteJSONFile writes a .JSON file. Behaves as Go's built-in encoding/json.MarshalIndent()
// but accepts a file path in addition to the  data.
func WriteJSONFile(outputFilePath string, data interface{}) error {
	outputBytes, err := json.MarshalIndent(data, "", " ")
	if err != nil {
		return err
	}

	logger.Log.Tracef("Writing %#x bytes of JSON data.", len(outputBytes))

	return ioutil.WriteFile(outputFilePath, outputBytes, defaultJsonFilePermission)
}
