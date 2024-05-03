from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._type_vars import T1, T2, T

###############################################################################
# general stuff
###############################################################################


def methods_of(obj: object) -> list[str]:
    return [i for i in dir(obj) if callable(getattr(obj, i)) and not i.startswith("_")]


def print_comment_line(char: str = "#", n: int = 79) -> None:
    print(char * n)  # noqa: T201


def default_if_none(el: T | None, default: T) -> T:
    return default if el is None else el


def list_if_none(el: list[T] | None) -> list[T]:
    return default_if_none(el, [])


def set_if_none(el: set[T] | None) -> set[T]:
    return default_if_none(el, set())


def dict_if_none(el: dict[T1, T2] | None) -> dict[T1, T2]:
    return default_if_none(el, {})


def default_path(path: Path | str) -> Path:
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(exist_ok=True, parents=True)
    return path


def unwrap(x: T | None) -> T:
    assert x is not None
    return x


def unwrap2(x: tuple[T1 | None, T2 | None]) -> tuple[T1, T2]:
    x1, x2 = x
    assert x1 is not None
    assert x2 is not None
    return (x1, x2)


def get_package_version(pkg_name: str) -> str:
    from importlib.metadata import version

    return version(pkg_name)
