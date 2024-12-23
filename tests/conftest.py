# type: ignore

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


def _multiline_comparison(expected: list[str], test: str) -> None:
    for l1, l2 in zip(expected, test.split("\n"), strict=False):
        assert l1 == l2


@pytest.fixture()
def multiline_comparison() -> Callable[..., None]:
    return _multiline_comparison
