// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// Shared logger

package logger

import (
	"bufio"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"

	log "github.com/sirupsen/logrus"
	"microsoft.com/pkggen/internal/logger/hooks/writerhook"
)

var (
	// Log contains the shared Logger
	Log *log.Logger

	stderrHook *writerhook.WriterHook
	fileHook   *writerhook.WriterHook

	// Valid log levels
	levelsArray = []string{"panic", "fatal", "error", "warn", "info", "debug", "trace"}
)

const (
	// LevelsPlaceholder are all valid log levels separated by '|' character.
	LevelsPlaceholder = "(panic|fatal|error|warn|info|debug|trace)"

	// LevelsFlag is the suggested name of the flag for loglevel
	LevelsFlag = "log-level"

	// LevelsHelp is the suggested help message for the loglevel flag
	LevelsHelp = "The minimum log level."

	// FileFlag is the suggested name for logfile flag
	FileFlag = "log-file"

	// FileFlagHelp is the suggested help message for the logfile flag
	FileFlagHelp = "Path to the image's log file."

	defaultLogFileLevel   = log.DebugLevel
	defaultStderrLogLevel = log.InfoLevel
)

// InitLogFile initializes the common logger with a file
func InitLogFile(filePath string) (err error) {
	const useColors = false

	err = os.MkdirAll(filepath.Dir(filePath), os.ModePerm)
	if err != nil {
		return
	}

	file, err := os.Create(filePath)
	if err != nil {
		return
	}

	fileHook = writerhook.NewWriterHook(file, defaultLogFileLevel, useColors)
	Log.Hooks.Add(fileHook)
	Log.SetLevel(defaultLogFileLevel)

	return
}

// InitStderrLog initializes the logger to print to stderr
func InitStderrLog() {
	const useColors = true

	Log = log.New()

	// By default send all log messages through stderrHook
	stderrHook = writerhook.NewWriterHook(os.Stderr, defaultStderrLogLevel, useColors)
	Log.AddHook(stderrHook)
	Log.SetLevel(defaultStderrLogLevel)
	Log.SetOutput(ioutil.Discard)
}

// SetFileLogLevel sets the lowest log level for file output
func SetFileLogLevel(level string) (err error) {
	return setHookLogLevel(fileHook, level)
}

// SetStderrLogLevel sets the lowest log level for stderr output
func SetStderrLogLevel(level string) (err error) {
	return setHookLogLevel(stderrHook, level)
}

// InitBestEffort runs InitStderrLog always, and InitLogFile if path is not empty
func InitBestEffort(path string, level string) {
	if level == "" {
		level = defaultStderrLogLevel.String()
	}

	InitStderrLog()

	if path != "" {
		PanicOnError(InitLogFile(path), "Failed while setting log file (%s).", path)
	}

	PanicOnError(SetStderrLogLevel(level), "Failed while setting log level.")
}

// Levels returns list of strings representing valid log levels.
func Levels() []string {
	return levelsArray
}

// PanicOnError logs the error and any message strings and then panics
func PanicOnError(err interface{}, args ...interface{}) {
	if err != nil {
		if len(args) > 0 {
			Log.Errorf(args[0].(string), args[1:]...)
		}

		Log.Panicln(err)
	}
}

// WarningOnError logs a warning error and any message strings
func WarningOnError(err interface{}, args ...interface{}) {
	if err != nil {
		if len(args) > 0 {
			Log.Warningf(args[0].(string), args[1:]...)
		}
	}
}

// StreamOutput calls the provided logFunction on every line from the provided pipe
func StreamOutput(pipe io.Reader, logFunction func(...interface{}), wg *sync.WaitGroup, outputChan chan string) {
	for scanner := bufio.NewScanner(pipe); scanner.Scan(); {
		line := scanner.Text()
		logFunction(line)

		Log.Tracef("StreamOutput:\t'%s'", line)

		// Optionally buffer the output to print in the event of an error
		if outputChan != nil {
			select {
			case outputChan <- line:
			default:
				// In the event the buffer is full, drop the line
			}
		}
	}

	wg.Done()
}

// ReplaceStderrWriter replaces the stderr writer and returns the old one
func ReplaceStderrWriter(newOut io.Writer) (oldOut io.Writer) {
	return stderrHook.ReplaceWriter(newOut)
}

// ReplaceStderrFormatter replaces the stderr formatter and returns the old formatter
func ReplaceStderrFormatter(newFormatter log.Formatter) (oldFormatter log.Formatter) {
	return stderrHook.ReplaceFormatter(newFormatter)
}

func setHookLogLevel(hook *writerhook.WriterHook, level string) (err error) {
	logLevel, err := log.ParseLevel(level)
	if err != nil {
		return
	}

	// Update the base logger level if its not at least equal to the hook level
	// Otherwise the hook will not receive any entries
	if logLevel > hook.CurrentLevel() {
		Log.SetLevel(logLevel)
	}

	hook.SetLevel(logLevel)
	return
}
