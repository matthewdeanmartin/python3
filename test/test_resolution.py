"""Cross-platform unit tests for python3.__main__ interpreter resolution."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from python3 import __main__ as m

ENV_VARS = ("PYTHON3_ALIAS_VENV", "PYTHON3_ALIAS_PYTHON", "PYTHON3_ALIAS_VERSION")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure none of the alias env vars leak between tests."""
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.delenv("PYTHONHOME", raising=False)


def _make_venv(root: Path, *, windows: bool) -> Path:
    """Create a venv-shaped directory with a stub python executable."""
    bindir = root / ("Scripts" if windows else "bin")
    bindir.mkdir(parents=True)
    exe = bindir / ("python.exe" if windows else "python")
    exe.write_text("")
    if not windows:
        exe.chmod(0o755)
    return root


# ---------- _venv_python ----------


def test_venv_python_posix_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "linux")
    venv = _make_venv(tmp_path / "v", windows=False)
    result = m._venv_python(str(venv))
    assert Path(result) == venv / "bin" / "python"


def test_venv_python_windows_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "win32")
    venv = _make_venv(tmp_path / "v", windows=True)
    result = m._venv_python(str(venv))
    assert Path(result) == venv / "Scripts" / "python.exe"


def test_venv_python_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        m._venv_python(str(tmp_path / "does-not-exist"))


# ---------- _venv_env ----------


@pytest.mark.parametrize(
    "platform,bin_subdir",
    [("linux", "bin"), ("darwin", "bin"), ("win32", "Scripts")],
)
def test_venv_env_sets_path_and_virtual_env(tmp_path, monkeypatch, platform, bin_subdir):
    monkeypatch.setattr(m.sys, "platform", platform)
    monkeypatch.setenv("PATH", "/preexisting")
    venv = _make_venv(tmp_path / "v", windows=(platform == "win32"))

    env = m._venv_env(str(venv))

    expected_bin = (venv / bin_subdir).resolve()
    assert env["PATH"].startswith(f"{expected_bin}{os.pathsep}")
    assert "/preexisting" in env["PATH"]
    assert Path(env["VIRTUAL_ENV"]) == venv.resolve()


def test_venv_env_unsets_pythonhome(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONHOME", "/leftover")
    venv = _make_venv(tmp_path / "v", windows=(sys.platform == "win32"))
    env = m._venv_env(str(venv))
    assert "PYTHONHOME" not in env


def test_venv_env_does_not_mutate_os_environ(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/before")
    venv = _make_venv(tmp_path / "v", windows=(sys.platform == "win32"))
    m._venv_env(str(venv))
    assert os.environ["PATH"] == "/before"
    assert "VIRTUAL_ENV" not in os.environ


# ---------- _resolve_versioned ----------


def test_resolve_versioned_windows_uses_py_launcher(monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "win32")
    monkeypatch.setattr(m.shutil, "which", lambda name: r"C:\Windows\py.exe" if name == "py" else None)
    assert m._resolve_versioned("3.14") == [r"C:\Windows\py.exe", "-3.14"]


def test_resolve_versioned_windows_falls_back_to_versioned_python(monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "win32")

    def fake_which(name):
        return r"C:\Python314\python3.14.exe" if name == "python3.14" else None

    monkeypatch.setattr(m.shutil, "which", fake_which)
    assert m._resolve_versioned("3.14") == [r"C:\Python314\python3.14.exe"]


def test_resolve_versioned_windows_raises_when_nothing_found(monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "win32")
    monkeypatch.setattr(m.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError):
        m._resolve_versioned("3.99")


def test_resolve_versioned_posix_uses_pythonxy(monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "linux")
    monkeypatch.setattr(m.shutil, "which", lambda name: f"/usr/bin/{name}" if name == "python3.14" else None)
    assert m._resolve_versioned("3.14") == ["/usr/bin/python3.14"]


def test_resolve_versioned_posix_raises_when_missing(monkeypatch):
    monkeypatch.setattr(m.sys, "platform", "linux")
    monkeypatch.setattr(m.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError):
        m._resolve_versioned("3.99")


# ---------- _resolve_command precedence ----------


def test_resolve_command_default_is_sys_executable():
    prefix, env = m._resolve_command()
    assert prefix == [sys.executable]
    assert env is None


def test_resolve_command_python_var(monkeypatch):
    monkeypatch.setenv("PYTHON3_ALIAS_PYTHON", "/some/python")
    prefix, env = m._resolve_command()
    assert prefix == ["/some/python"]
    assert env is None


def test_resolve_command_version_var(monkeypatch):
    monkeypatch.setenv("PYTHON3_ALIAS_VERSION", "3.14")
    monkeypatch.setattr(m, "_resolve_versioned", lambda v: [f"/fake/python{v}"])
    prefix, env = m._resolve_command()
    assert prefix == ["/fake/python3.14"]
    assert env is None


def test_resolve_command_venv_var(tmp_path, monkeypatch):
    venv = _make_venv(tmp_path / "v", windows=(sys.platform == "win32"))
    monkeypatch.setenv("PYTHON3_ALIAS_VENV", str(venv))
    prefix, env = m._resolve_command()
    assert len(prefix) == 1
    assert Path(prefix[0]).parent.parent == venv
    assert env is not None
    assert Path(env["VIRTUAL_ENV"]) == venv.resolve()


def test_resolve_command_venv_beats_python(tmp_path, monkeypatch):
    venv = _make_venv(tmp_path / "v", windows=(sys.platform == "win32"))
    monkeypatch.setenv("PYTHON3_ALIAS_VENV", str(venv))
    monkeypatch.setenv("PYTHON3_ALIAS_PYTHON", "/should/be/ignored")
    prefix, _ = m._resolve_command()
    assert "ignored" not in prefix[0]


def test_resolve_command_python_beats_version(monkeypatch):
    monkeypatch.setenv("PYTHON3_ALIAS_PYTHON", "/explicit/python")
    monkeypatch.setenv("PYTHON3_ALIAS_VERSION", "3.14")
    monkeypatch.setattr(m, "_resolve_versioned", lambda v: pytest.fail("should not be called"))
    prefix, _ = m._resolve_command()
    assert prefix == ["/explicit/python"]


# ---------- run_current_python ----------


def test_run_current_python_passes_args_and_returns_code(monkeypatch):
    captured = {}

    def fake_run(cmd, env=None):
        captured["cmd"] = cmd
        captured["env"] = env
        return subprocess.CompletedProcess(cmd, 42)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    rc = m.run_current_python(["-c", "print('hi')"])
    assert rc == 42
    assert captured["cmd"] == [sys.executable, "-c", "print('hi')"]
    assert captured["env"] is None


def test_run_current_python_propagates_nonzero(monkeypatch):
    monkeypatch.setattr(m.subprocess, "run", lambda cmd, env=None: subprocess.CompletedProcess(cmd, 7))
    assert m.run_current_python([]) == 7


def test_run_current_python_reraises_oserror(monkeypatch):
    def boom(*a, **k):
        raise OSError("no such file")

    monkeypatch.setattr(m.subprocess, "run", boom)
    with pytest.raises(OSError):
        m.run_current_python([])


def test_run_current_python_with_venv_passes_env(tmp_path, monkeypatch):
    venv = _make_venv(tmp_path / "v", windows=(sys.platform == "win32"))
    monkeypatch.setenv("PYTHON3_ALIAS_VENV", str(venv))

    captured = {}

    def fake_run(cmd, env=None):
        captured["env"] = env
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(m.subprocess, "run", fake_run)
    m.run_current_python([])
    assert captured["env"] is not None
    assert Path(captured["env"]["VIRTUAL_ENV"]) == venv.resolve()


# ---------- run() entry point ----------


def test_run_exits_with_subprocess_returncode(monkeypatch):
    monkeypatch.setattr(m.sys, "argv", ["python3", "-V"])
    monkeypatch.setattr(m, "run_current_python", lambda args: 3)
    with pytest.raises(SystemExit) as exc:
        m.run()
    assert exc.value.code == 3


def test_run_exits_1_on_unexpected_exception(monkeypatch):
    monkeypatch.setattr(m.sys, "argv", ["python3"])

    def boom(_args):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(m, "run_current_python", boom)
    with pytest.raises(SystemExit) as exc:
        m.run()
    assert exc.value.code == 1
