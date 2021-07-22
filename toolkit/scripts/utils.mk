# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Contains:
#	- Misc. Makefile Defines
#	- Misc. Makefile Functions
#	- Variable prerequisite tracking

######## MISC. MAKEFILE DEFINES ########

# Check if we have pigz available to speed up archive commands
ARCHIVE_TOOL ?= $(shell if command -v pigz 1>/dev/null 2>&1 ; then echo pigz ; else echo gzip ; fi )
# Host and target architecture
build_arch := $(shell uname -m)

######## MISC. MAKEFILE Functions ########

# Creates a folder if it doesn't exist. Also sets the timestamp to 0 if it is
# created.
#
# $1 - Folder path
define create_folder
$(shell if [ ! -d $1 ]; then mkdir -p $1 && touch -d @0 $1 ; fi )
endef

# Echos a message to console, then calls "exit 1"
# Of the form: { echo "MSG" ; exit 1 ; }
#
# $1 - Error message to print
define print_error
{ echo "$1" ; exit 1 ; }
endef

# Echos a message to console, then, if STOP_ON_WARNING is set to "y" calls "exit 1"
# Of the form: { echo "MSG" ; < exit 1 ;> }
#
# $1 - Warning message to print
define print_warning
{ echo "$1" ; $(if $(filter y,$(STOP_ON_WARNING)),exit 1 ;) }
endef

######## VARIABLE DEPENDENCY TRACKING ########

# List of variables to watch for changes.
watch_vars=PACKAGE_BUILD_LIST PACKAGE_REBUILD_LIST PACKAGE_IGNORE_LIST REPO_LIST CONFIG_FILE STOP_ON_PKG_FAIL
# Current list: $(depend_PACKAGE_BUILD_LIST) $(depend_PACKAGE_REBUILD_LIST) $(depend_PACKAGE_IGNORE_LIST) $(depend_REPO_LIST) $(depend_CONFIG_FILE) $(depend_STOP_ON_PKG_FAIL)

.PHONY: variable_depends_on_phony clean-variable_depends_on_phony
clean: clean-variable_depends_on_phony

$(call create_folder,$(STATUS_FLAGS_DIR))
clean-variable_depends_on_phony:
	rm -rf $(STATUS_FLAGS_DIR)

# Watch for the variables by depending on '$(depend_<VAR_NAME>)'.
# Each variable will be tracked as a file $(STATUS_FLAGS_DIR)/<VAR_NAME>_tracking_flag.
# By having each generated target depend on the .PHONY target: variable_depends_on_phony,
# they will alway run. Each rule will check the currently stored value in the file and only
# update it if needed.

# Generate a target which watches a variable for changes so rebuilds can be 
# triggered if needed. Uses one file per variable. If the value of the variable 
# is not the same as recorded in the file, update the file to match. This will 
# force a rebuild of any dependent targets.
#
# $1 - name of the variable to watch for changes
define depend_on_var
depend_$1=$(STATUS_FLAGS_DIR)/$1_tracking_flag
$(STATUS_FLAGS_DIR)/$1_tracking_flag: variable_depends_on_phony
	@if [ ! -f $$@ ]; then \
		echo $($1) > $$@ ; \
	elif [ "$($1)" != "$$$$(cat $$@)" ]; then \
		echo "Updated value of $1 ($$$$(cat $$@) -> $($1))" ; \
		echo $($1) > $$@ ; \
	fi
endef

# Invoke the above rule for each tracked variable
$(foreach var,$(watch_vars),$(eval $(call depend_on_var,$(var))))