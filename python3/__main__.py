"""
Alias for python3 when other methods for creating an alias are burdensome.

Resolution order for which interpreter to launch:
    1. PYTHON3_ALIAS_VENV    — path to a venv; activates it (PATH/VIRTUAL_ENV) and uses its python
    2. PYTHON3_ALIAS_PYTHON  — full path to a python executable
    3. PYTHON3_ALIAS_VERSION — like "3.14" or "3.7"; uses py.exe on Windows, pythonX.Y on POSIX
    4. sys.executable        — fallback (current behavior)
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _venv_python(venv: str) -> str:
    """Return the python executable inside the given venv directory."""
    venv_path = Path(venv)
    if sys.platform == "win32":
        candidate = venv_path / "Scripts" / "python.exe"
    else:
        candidate = venv_path / "bin" / "python"
    if not candidate.exists():
        raise FileNotFoundError(f"No python found inside venv at {candidate}")
    return str(candidate)


def _venv_env(venv: str) -> dict[str, str]:
    """Return a copy of os.environ with venv activation applied."""
    venv_path = Path(venv).resolve()
    env = os.environ.copy()
    bindir = venv_path / ("Scripts" if sys.platform == "win32" else "bin")
    sep = os.pathsep
    env["PATH"] = f"{bindir}{sep}{env.get('PATH', '')}"
    env["VIRTUAL_ENV"] = str(venv_path)
    env.pop("PYTHONHOME", None)
    return env


def _resolve_versioned(version: str) -> list[str]:
    """Resolve PYTHON3_ALIAS_VERSION (e.g. '3.14') to a launch command prefix."""
    if sys.platform == "win32":
        py = shutil.which("py")
        if py:
            return [py, f"-{version}"]
        # Fall back to pythonX.Y on PATH if no launcher
        candidate = shutil.which(f"python{version}")
        if candidate:
            return [candidate]
        raise FileNotFoundError(
            f"Could not find py launcher or python{version} on PATH"
        )
    candidate = shutil.which(f"python{version}")
    if not candidate:
        raise FileNotFoundError(f"Could not find python{version} on PATH")
    return [candidate]


def _resolve_command() -> tuple[list[str], dict[str, str] | None]:
    """Return (command-prefix, env-or-None) based on env vars or sys.executable."""
    venv = os.environ.get("PYTHON3_ALIAS_VENV")
    if venv:
        LOGGER.info(f"PYTHON3_ALIAS_VENV={venv}")
        return [_venv_python(venv)], _venv_env(venv)

    explicit = os.environ.get("PYTHON3_ALIAS_PYTHON")
    if explicit:
        LOGGER.info(f"PYTHON3_ALIAS_PYTHON={explicit}")
        return [explicit], None

    version = os.environ.get("PYTHON3_ALIAS_VERSION")
    if version:
        LOGGER.info(f"PYTHON3_ALIAS_VERSION={version}")
        return _resolve_versioned(version), None

    return [sys.executable], None


def run_current_python(args: list[str]) -> int:
    """Execute the resolved Python interpreter with the given arguments.

    Args:
        args (list[str]): A list of command-line arguments to pass to the Python interpreter.

    Returns:
        int: The return code of the subprocess call.

    Raises:
        OSError: If there is an issue running the subprocess.
    """
    prefix, env = _resolve_command()
    command = prefix + args
    LOGGER.info(f"Executing command: {command}")

    try:
        result = subprocess.run(command, env=env)
        return result.returncode
    except OSError as e:
        LOGGER.error(f"An OS-related error occurred: {e}")
        raise


def run() -> None:
    """Main entry point for the CLI utility."""
    args = sys.argv[1:]
    LOGGER.info(f"Arguments passed: {args}")

    # pylint: disable=broad-exception-caught
    try:
        exit_code = run_current_python(args)
        sys.exit(exit_code)
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    run()
