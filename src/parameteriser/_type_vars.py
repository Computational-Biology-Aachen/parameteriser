from collections.abc import Iterable
from typing import TypeVar

__all__ = ["T1", "T2", "T", "Ti", "Tin", "Tout"]

T = TypeVar("T")
Tin = TypeVar("Tin")
Tout = TypeVar("Tout")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
Ti = TypeVar("Ti", bound=Iterable)
