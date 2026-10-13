# Copyright 2025 Marvin van Aalst, Anna Matuszyńska

"""Experimental kinetic parameter prediction tools."""

import contextlib

with contextlib.suppress(ImportError):
    from . import deepmolecules

__all__ = ["deepmolecules"]
