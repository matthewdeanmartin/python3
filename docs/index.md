# A `python3` command when you need one

`python3-alias` installs a `python3` console command. It forwards command-line arguments and the exit status to a Python interpreter. By default, that is the interpreter which launched the alias. You can select a virtual environment, an explicit executable, or a Python version with environment variables.

The command is useful in scripts that expect `python3`, including Makefiles on Windows where that name may be absent. It does not install a Python interpreter.

Start with [installation](installation.md), then [choose an interpreter](routing.md). The [README](https://github.com/matthewdeanmartin/python3#readme) records why the package exists.
