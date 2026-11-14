# python3
Hack to handle a missing alias/symlink, for example when you're on windows or don't want to be bothered

This exists so that the following Makefile command will execute correctly on Windows.
```Makefile
PLATFORM_ARCH := $(shell python3 -c "import platform; print(platform.machine())")
```

## Installation

To get a standalone `python3` command backed by pipx's isolated interpreter:
```bash
pipx install python3-alias
```

To use a known interpreter, install into an isolated virtual environment with pip. `uv` reserves the `python3` executable name and cannot install this project's console script; do not use `uv sync` to install this package.
```bash
python -m pip install --only-binary=:all: python3-alias
```

## Motivation

Yes, I know, one solution is for *you* to personally purchase a Macbook for everyone in the world. Please
include me when you do.

### Things that don't work

In git bash, this isn't picked up.
```bash
alias python3=python
```

Link python3 to python in bash
```bash
ln -s /c/Users/USER/AppData/Local/Programs/Python/Python312/python /usr/bin/python3
# ln: failed to create symbolic link '/usr/bin/python3': Permission denied
```

Also adding `python3=python` to this file didn't work. 
```bash
nano "/C/Program Files/Git/etc/profile.d/aliases.sh"
```

Also, a shell file named `python3` didn't work.

Installing python from the Microsoft Store might work, I didn't try. I'd rather install from python.org.

## Redirecting to a different Python

By default the alias forwards to whichever Python launched it (`sys.executable`). You can override this
with environment variables, checked in this order:

| Variable                | Value                          | Effect                                                                         |
|-------------------------|--------------------------------|--------------------------------------------------------------------------------|
| `PYTHON3_ALIAS_VENV`    | path to a venv directory       | Activates the venv (sets `PATH`, `VIRTUAL_ENV`, unsets `PYTHONHOME`) and runs its python. |
| `PYTHON3_ALIAS_PYTHON`  | full path to a python.exe      | Runs that interpreter directly.                                                |
| `PYTHON3_ALIAS_VERSION` | `3.14`, `3.7`, etc.            | Windows: launches via `py -X.Y`. POSIX: launches `pythonX.Y` from `PATH`.      |

The first one set wins. If none are set, the alias behaves as before.

### Examples

```bash
# Pin a specific interpreter
PYTHON3_ALIAS_PYTHON="C:/Python314/python.exe" python3 -V

# Use the py launcher to pick a version (Windows)
PYTHON3_ALIAS_VERSION=3.14 python3 -V

# Run inside a venv without sourcing its activate script
PYTHON3_ALIAS_VENV=./.venv python3 -m pip list
```

## Limitations

This alias isn't to replace pyenv, asdf or the like.

## Project Links

- [GitHub](https://github.com/matthewdeanmartin/python3)
- [Homepage](https://matthewdeanmartin.github.io/python3/)
- [Documentation source](https://github.com/matthewdeanmartin/python3/tree/main/docs)
- [PyPI](https://pypi.org/project/python3-alias/)
- [Bug Tracker](https://github.com/matthewdeanmartin/python3/issues)
- [Change Log](https://github.com/matthewdeanmartin/python3/blob/main/CHANGELOG.md)

## Installer limitation

`uv` reserves the `python3` console-script name and refuses to install this package's launcher. Use `pip` or `pipx` in an isolated environment. On POSIX, an existing interpreter-named launcher may take precedence over this package's script.
