# Installation

For an isolated command on your path, use pipx:

```bash
pipx install python3-alias
python3 --version
```

To route through a known interpreter, install in a dedicated virtual environment with pip and place that environment's `Scripts` directory (Windows) or `bin` directory (POSIX) on your path:

```bash
python -m venv .alias-env
.alias-env/Scripts/python -m pip install --only-binary=:all: python3-alias
```

The second command shows a Git Bash path on Windows. For POSIX, use `.alias-env/bin/python`.

`uv` reserves `python3` as an interpreter launcher name and refuses this package's console script. Its dependency lock can still be checked with `uv lock --upgrade --no-build`; install the package wheel with pip in an isolated environment. Do not replace a system interpreter or global `python3` alias.

On POSIX, a preexisting `python3` launcher may precede the installed console script on `PATH`. Check which executable your shell resolves before relying on it.
