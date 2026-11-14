# Interpreter routing

The alias passes all arguments through to the selected interpreter and returns its exit status. Set one of these variables before invoking `python3`. The first nonempty variable in the table wins.

| Priority | Variable | Behavior |
| --- | --- | --- |
| 1 | `PYTHON3_ALIAS_VENV` | Finds the venv's `Scripts/python.exe` on Windows or `bin/python` on POSIX, prepends that directory to `PATH`, sets `VIRTUAL_ENV`, and removes `PYTHONHOME` for the child. |
| 2 | `PYTHON3_ALIAS_PYTHON` | Runs an explicit interpreter path. |
| 3 | `PYTHON3_ALIAS_VERSION` | Uses `py -<version>` on Windows when the launcher exists; otherwise looks for `python<version>` on `PATH`. POSIX looks for `python<version>` on `PATH`. |
| 4 | none | Runs the interpreter that launched the alias (`sys.executable`). |

Examples for Git Bash on Windows:

```bash
PYTHON3_ALIAS_VERSION=3.14 python3 -V
PYTHON3_ALIAS_PYTHON='C:/Python314/python.exe' python3 -V
PYTHON3_ALIAS_VENV=./.venv python3 -m pip list
```

A path in these examples must exist on your machine. For a Makefile that expects `python3`, see the [README example](https://github.com/matthewdeanmartin/python3#readme).
