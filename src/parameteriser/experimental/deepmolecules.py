"""Kinetic parameter prediction via deepmolecules models."""

from __future__ import annotations

from deepmolecules import kcat as _kcat
from deepmolecules import km as _km

__all__ = [
    "predict_kcat",
    "predict_km",
]


def predict_km(substrate: str, enzyme_sequence: str) -> float:
    """Predict KM value for a substrate-enzyme pair in mM."""
    return _km.predict(
        substrates=[substrate],
        enzymes=[enzyme_sequence],
    )["KM [mM]"].iloc[0]


def predict_kcat(substrate: str, product: str, enzyme_sequence: str) -> float:
    """Predict kcat value for a substrate-product-enzyme triplet in 1/s."""
    return _kcat.predict(
        substrates=[substrate],
        products=[product],
        enzymes=[enzyme_sequence],
    )["kcat [s^(-1)]"].iloc[0]
