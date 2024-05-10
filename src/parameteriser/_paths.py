from __future__ import annotations

import sys
from pathlib import Path


def _default_path(name: str | Path) -> Path:
    path = Path(name)
    path.mkdir(exist_ok=True, parents=True)
    return path


def _default_cache_dir(path: Path | None = None) -> Path:
    path = Path.home() / ".cache" / "parameteriser" if path is None else path
    path.mkdir(exist_ok=True, parents=True)
    return path


def _default_temp_dir() -> Path:
    if sys.platform in ["win32", "cygwin"]:
        tmp = Path(r"%userprofile%") / "AppData" / "Local" / "Temp" / "parameteriser"
    else:
        tmp = Path("/tmp") / "parameteriser"  # noqa: S108

    tmp.mkdir(exist_ok=True, parents=True)
    return tmp


def _clear_files_of_dir(path: Path) -> None:
    """Assumes directory only contains files!"""
    for file in path.iterdir():
        file.unlink()


def _rmdir(path: Path) -> None:
    for item in path.iterdir():
        if item.is_dir():
            _rmdir(item)
        else:
            item.unlink()
    path.rmdir()
