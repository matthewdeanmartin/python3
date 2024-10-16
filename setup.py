import sys
from setuptools import setup
from distutils.command.install import install as _install

class CustomInstall(_install):
    """Customized setuptools install command to check Python 3 existence and conditionally register a script."""

    def run(self):
        # Check if 'python3' alias exists
        if not self._is_python3_present():
            # Register the script
            print("Python3 alias not found. Registering python3 alias...")
            # You can modify this line to add any specific alias creation logic on Windows
            self.distribution.entry_points['console_scripts'] = ['python3=python3.__main__:run']
        else:
            print("Python3 alias found. Skipping alias registration.")
        _install.run(self)

    def _is_python3_present(self):
        """Helper to check if 'python3' command exists in the system."""
        import shutil
        return shutil.which('python3') is not None

setup(
    name="python3-alias",
    version="1.0.1",
    description="Hack to deal with a missing python3 alias on Windows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Matthew Martin",
    author_email="matthewdeanmartin@gmail.com",
    keywords=["python3", "alias"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=["python3"],
    include_package_data=True,
    license="MIT",
    url="https://github.com/matthewdeanmartin/python3",
    project_urls={
        "Homepage": "https://github.com/matthewdeanmartin/python3",
        "Documentation": "https://github.com/matthewdeanmartin/python3",
        "Repository": "https://github.com/matthewdeanmartin/python3",
    },
    entry_points={
        'console_scripts': []  # Initially empty; added conditionally
    },
    cmdclass={
        'install': CustomInstall,
    },
)
