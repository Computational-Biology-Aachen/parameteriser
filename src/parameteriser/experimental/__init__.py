import contextlib

with contextlib.suppress(ImportError):
    from . import deepmolecules

__all__ = ["deepmolecules"]
