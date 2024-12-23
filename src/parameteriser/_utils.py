from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

__all__ = [
    "default_if_none",
    "default_path",
    "dict_if_none",
    "estimate_mean_std",
    "get_package_version",
    "list_if_none",
    "methods_of",
    "print_comment_line",
    "print_organisms",
    "print_table",
    "select_organism",
    "select_substrate",
    "set_if_none",
    "unwrap",
    "unwrap2",
]

if TYPE_CHECKING:
    from collections.abc import Iterable

    import pandas as pd

    from ._type_vars import T1, T2, T

###############################################################################
# general stuff
###############################################################################


def methods_of(obj: object) -> list[str]:
    return [i for i in dir(obj) if callable(getattr(obj, i)) and not i.startswith("_")]


def print_comment_line(char: str = "#", n: int = 79) -> None:
    print(char * n)  # noqa: T201


def print_table(
    vals: Iterable[str],
    max_width: int = 80,
    max_rows: int | None = None,
) -> None:
    from math import floor

    from more_itertools import batched

    sep = " | "
    vals = list(vals)
    max_length = max(len(i) for i in vals)
    items_per_line = floor((max_width + len(sep)) / max_length)

    for line, group in enumerate(batched(vals, items_per_line)):
        print(sep.join(f"{i:<{max_length}}" for i in group))  # noqa: T201
        if max_rows is not None and line == (max_rows - 1):
            print("...")  # noqa: T201
            break


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


def print_organisms(
    df: pd.DataFrame,
    max_width: int = 79,
    max_rows: int | None = None,
) -> None:
    organisms = df["organism"].unique()
    organisms.sort()
    print_table(organisms, max_width=max_width, max_rows=max_rows)


def select_organism(df: pd.DataFrame, organism: str) -> pd.DataFrame:
    return df[df["organism"] == organism].drop(columns=["organism"])


def select_substrate(df: pd.DataFrame, substrate: str) -> pd.DataFrame:
    return df[df["substrate"] == substrate].drop(columns=["substrate"])


def estimate_mean_std(values: pd.Series) -> tuple[float, float]:
    from math import sqrt

    from scipy.integrate import quad
    from scipy.stats import gaussian_kde

    kde = gaussian_kde(values)
    mean, _err = quad(lambda x: x * kde.pdf(x), -np.inf, np.inf)
    integral, _err = quad(lambda x: x**2 * kde.pdf(x), -np.inf, np.inf)
    var = integral - mean**2
    return mean, sqrt(var)
