# type: ignore

from __future__ import annotations

from typing import List

import pytest


def _multiline_comparison(expected: List[str], test: str):
    for l1, l2 in zip(expected, test.split("\n")):
        assert l1 == l2


@pytest.fixture()
def multiline_comparison():
    return _multiline_comparison
