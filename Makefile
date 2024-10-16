PLATFORM_ARCH := $(shell python3 -c "import platform; print(platform.machine())")
PLATFORM_OS := $(shell python3 -c "import platform; print(platform.system())")
PY_VERSION := $(shell python3 -c "import sys; print('%s.%s' % (sys.version_info.major, sys.version_info.minor))")

$(info    PLATFORM_ARCH is $(PLATFORM_ARCH))
$(info    PLATFORM_OS is $(PLATFORM_OS))
$(info    PY_VERSION is $(PY_VERSION))

check:
	@black python3
	@pylint python3
	@ruff check python3
	@mypy python3