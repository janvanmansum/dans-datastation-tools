Development
===========

This page contains information for developers about how to contribute to this project.

Set-up
------

The project uses [poetry] for a build system. It is recommended practise to install poetry globally (or for your user),
so
*not* in a virtual environment. Poetry itself will create and manage a virtual environment to install the development
dependencies. To install poetry you can use `brew` on macOS, or you can use `python3 -m pip poetry`. (If pip is not
present, first execute `python3 -m ensurepip`.)

After `poetry` is installed execute:

```bash
poetry install
```

This will install the project and its dependencies in the Poetry virtual environment

### Troubleshooting

If your macOS Xcode tools are out of date, you may have to reinstall them. Otherwise the installation of the dependency
`lxml` will fail, complaining that `clang` cannot be executed. This happens on MacOS Monterey when `clang` is at version
11\. MacOS will, however, tell you that XCode is up-to-date when you try to upgrade.

To fix this:

```bash
sudo rm -rf /Library/Developer/CommandLineTools 
sudo xcode-select --install
```

After this `clang --version` should return a version number greater than 11.

Testing commands
----------------

After `poetry install` the commands provided by the module can be tested by prepending `poetry run` to the command line,
e.g.:

```shell
poetry run update-datacite-record 10.17026/some-suffix
```

For more information about how to use poetry, see the [poetry] documentation.

[poetry]: https://python-poetry.org/

Debugging commands in IntelliJ
------------------------------

There seems to be no special support for poetry with this respect. The only way to run a command in the debugger I have
found is to just call the entry-point script under `src/datastation/scripts`.

!!! Warning

    Change the working directory of the run configuration to the project root directory, so that you don't end up with
    a `.dans-datastation-tools.yml` file inside the `src/datastation/scripts` directory.

Adding to this documentation site
---------------------------------
See [dans-dev-tools](https://github.com/DANS-KNAW/dans-dev-tools#startsh-scripts):
`start-virtual-env.sh` and `start-mkdocs.sh`.

Browse to <http://127.0.0.1:8000>{:target=_blank} to view your changes.

Note that here we are using a separate virtual environment. This way we don't get the dependencies
for `dans-datastation-tools` and the doc site confused.

Coding style
------------

* Except for input from configured APIs such as Dataverse and DataCite, prefer reading input from:
    1. The command line (for simple values)
    2. The standard input (for longer inputs)
* Write output to the standard output
* Write status messages ("OK", "Oops", etc.) for the end user to the standard error
* Write all other information to the logs (at an appropriate level)
* Get all the configuration variables from the `config` dictionary in the `main` function and pass them to down to the
  functions instead of passing down the complete config dictionary.

### String interpolation

Use the following syntax for string interpolation:

```python
name = "John"
f"Hello {name}"
```

Do not use the old `%` syntax, or the `.format()` method or string concatenation.

### Parameter names

Use the following names for often used parameters. When there are subcommands, these parameters should be defined on the
top level, not on the subcommand level, unless they are only used by that subcommand.

* `-w`, `--wait-between-items` is a parameter that is used to specify the number of seconds to wait between items to
  process.
* `-d`, `--dry-run` is a parameter that is used to specify whether to actually perform the action or not.
* `-f`, `--format` is a parameter that is used to specify the format of the output. Available formats vary per command.
* `--fail-fast` is a parameter that is used to specify whether to stop processing when an error occurs. It has no
  brief form, because that would be `-f` which is already used for `--format`.

<!-- todo: add --report-file ? -->

