dans-datastation-tools
======================

Command line utilities for Data Station application management

SYNOPSIS
--------

```bash
pip3 install dans-datastation-tools

# Available commands, use --help for more information

# Manage a dataverse collection
dv-dataverse-retrieve-pids
dv-dataverse-oai-harvest

# Manage role assignments
dv-dataset-find-with-role-assignment
dv-dataset-add-role-assignment
dv-dataset-delete-role-assignment

# Manage dataset metadata
dv-dataset-replace-metadata-field-values
dv-dataset-retrieve-metadata
dv-dataset-retrieve-metadata-field

# Manage dataset state
dv-dataset-delete-draft
dv-dataset-publish
dv-dataset-reindex
dv-dataset-unlock
dv-dataset-update-datacite-record

# User management
dv-user-import

# Helper scripts for the migration from EASY
dv-dataset-destroy-migration-placeholder
dv-file-prestage


```

DESCRIPTION
-----------

This module contains a variety of command line scripts to facilitate DANS Data Station management. Each script comes
with a command line help.


INSTALLATION & CONFIGURATION
----------------------------

### Installation

* Globally:

  ```bash
  sudo pip3 install dans-datastation-tools
  ```

* For the current user:

  ```bash
  pip3 install --user dans-datastation-tools
  ```
  You may have to add the directory where `pip3` installs the command to the `PATH` manually.

### Configuration

The configuration file is called `.dans-datastation-tools.yml`. Each command starts by looking for this file in the
current working directory and then in the user's home directory. If it is not found in either location it is
instantiated with some default and placeholder values in the current directory. It is recommended that you move this
file to your home directory. Using the configuration file from the current working directory is mainly useful for
development.

For the available configuration options and their meaning, see the explanatory comments in the configuration file
itself.
