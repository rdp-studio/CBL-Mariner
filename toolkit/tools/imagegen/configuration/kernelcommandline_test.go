// Copyright Microsoft Corporation.
// Licensed under the MIT License.

package configuration

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

//TestMain found in configuration_test.go.

var (
	validCommandLine KernelCommandLine = KernelCommandLine{
		ImaPolicy: []ImaPolicy{
			ImaPolicyTcb,
		},
		ExtraCommandLine: "param1=value param2=\"value2 value3\"",
	}
	invalidExtraCommandLine     = "invalid=`delim`"
	validExtraComandLineJSON    = `{"ImaPolicy": ["tcb"], "ExtraCommandLine": "param1=value param2=\"value2 value3\""}`
	invalidExtraComandLineJSON1 = `{"ImaPolicy": [ "not-an-ima-policy" ]}`
	invalidExtraComandLineJSON2 = `{"ExtraCommandLine": "` + invalidExtraCommandLine + `"}`
)

func TestShouldSucceedParsingDefaultCommandLine_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine
	err := marshalJSONString("{}", &checkedCommandline)
	assert.NoError(t, err)
	assert.Equal(t, KernelCommandLine{}, checkedCommandline)
}

func TestShouldSucceedParseValidCommandLine_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine

	assert.NoError(t, validCommandLine.IsValid())
	err := remarshalJSON(validCommandLine, &checkedCommandline)
	assert.NoError(t, err)
	assert.Equal(t, validCommandLine, checkedCommandline)
}

func TestShouldSucceedParsingMultipleIma_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine
	multipleImaCommandLine := validCommandLine
	multipleImaCommandLine.ImaPolicy = append(multipleImaCommandLine.ImaPolicy, ImaPolicyAppraiseTcb)

	assert.NoError(t, multipleImaCommandLine.IsValid())
	err := remarshalJSON(multipleImaCommandLine, &checkedCommandline)
	assert.NoError(t, err)
	assert.Equal(t, multipleImaCommandLine, checkedCommandline)
}

func TestShouldSucceedParsesNoIma_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine
	nilImaCommandLine := validCommandLine
	nilImaCommandLine.ImaPolicy = nil

	assert.NoError(t, nilImaCommandLine.IsValid())
	err := remarshalJSON(nilImaCommandLine, &checkedCommandline)
	assert.NoError(t, err)
	assert.Equal(t, nilImaCommandLine, checkedCommandline)
}

func TestShouldFailParsingMixedValidInvalidIma_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine
	multipleImaCommandLine := validCommandLine
	multipleImaCommandLine.ImaPolicy = append(multipleImaCommandLine.ImaPolicy, invalidImaPolicy)

	err := multipleImaCommandLine.IsValid()
	assert.Error(t, err)
	assert.Equal(t, "invalid value for ImaPolicy (not_a_policy)", err.Error())

	err = remarshalJSON(multipleImaCommandLine, &checkedCommandline)
	assert.Error(t, err)
	assert.Equal(t, "failed to parse [KernelCommandLine]: failed to parse [ImaPolicy]: invalid value for ImaPolicy (not_a_policy)", err.Error())
}

func TestShouldFailWrongSedDelimeter_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine
	invalidSedExtraCommandLine := validCommandLine
	invalidSedExtraCommandLine.ExtraCommandLine = invalidExtraCommandLine

	err := invalidSedExtraCommandLine.IsValid()
	assert.Error(t, err)
	assert.Equal(t, "ExtraCommandLine contains character ` which is reserved for use by sed", err.Error())

	err = remarshalJSON(invalidSedExtraCommandLine, &checkedCommandline)
	assert.Error(t, err)
	assert.Equal(t, "failed to parse [KernelCommandLine]: ExtraCommandLine contains character ` which is reserved for use by sed", err.Error())
}

func TestShouldSucceedParsingValidJSON_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine

	err := marshalJSONString(validExtraComandLineJSON, &checkedCommandline)
	assert.NoError(t, err)
	assert.Equal(t, validCommandLine, checkedCommandline)
}

func TestShouldFailParsingInvalidJSON_KernelCommandLine(t *testing.T) {
	var checkedCommandline KernelCommandLine

	err := marshalJSONString(invalidExtraComandLineJSON1, &checkedCommandline)
	assert.Error(t, err)
	assert.Equal(t, "failed to parse [KernelCommandLine]: failed to parse [ImaPolicy]: invalid value for ImaPolicy (not-an-ima-policy)", err.Error())

	checkedCommandline = KernelCommandLine{}
	err = marshalJSONString(invalidExtraComandLineJSON2, &checkedCommandline)
	assert.Error(t, err)
	assert.Equal(t, "failed to parse [KernelCommandLine]: ExtraCommandLine contains character ` which is reserved for use by sed", err.Error())
}
