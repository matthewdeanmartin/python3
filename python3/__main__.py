"""
Alias for python3 when other methods for creating an alias are burdensome.
"""

import sys
import subprocess
import logging

LOGGER = logging.getLogger(__name__)


def run_current_python(args: list[str]) -> int:
    """Execute the currently activated Python interpreter with the given arguments.

    Args:
        args (list[str]): A list of command-line arguments to pass to the Python interpreter.

    Returns:
        int: The return code of the subprocess call.

    Raises:
        OSError: If there is an issue running the subprocess.
        subprocess.CalledProcessError: If the subprocess exits with a non-zero status.
    """
    # Path to the currently active Python interpreter
    python_executable = sys.executable
    LOGGER.info(f"Using Python executable at: {python_executable}")

    # Prepare the command to run the current Python interpreter
    command = [python_executable] + args
    LOGGER.info(f"Executing command: {command}")

    # Run the subprocess, inheriting stdout and stderr to replicate behavior closely
    try:
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Python command failed with return code {e.returncode}")
        # Re-raise to preserve the original behavior of raising on non-zero exit
        raise
    except OSError as e:
        LOGGER.error(f"An OS-related error occurred: {e}")
        # Re-raise to preserve exact exception behavior
        raise


def run() -> None:
    """Main entry point for the CLI utility."""
    # Get the command-line arguments excluding the script name
    args = sys.argv[1:]
    LOGGER.info(f"Arguments passed: {args}")

    # Run the current Python interpreter with the provided arguments
    # pylint: disable=broad-exception-caught
    try:
        exit_code = run_current_python(args)
        sys.exit(exit_code)
    except subprocess.CalledProcessError as e:
        # CalledProcessError is already being logged, propagate the exit code
        sys.exit(e.returncode)
    except Exception as e:
        # For any unexpected exceptions, log and return a non-zero exit code
        LOGGER.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Configure basic logging for the CLI utility
    # logging.basicConfig(level=logging.INFO)
    run()
