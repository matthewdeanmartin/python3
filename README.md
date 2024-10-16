# python3
Hack to handle a missing alias/symlink, for example when you're on windows or don't want to be bothered

This exists so that the following Makefile command will execute correctly on windows.
```Makefile
PLATFORM_ARCH := $(shell python3 -c "import platform; print(platform.machine())")
```

## Installation

To get python3 everywhere and python3 means just some random isolated python3
```bash
pipx install python3-alias
```

To get a known version of python3, install into the system or venv.
```bash
pip install python3-alias
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

## Limitations

At the moment, there are no features to configure the python3 alias to use a python executable other than
the system, pipx or venv depending on where you installed it.

This alias isn't to replace pyenv, asdf or the like.
