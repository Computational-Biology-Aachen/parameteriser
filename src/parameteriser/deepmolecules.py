from __future__ import annotations

__all__ = [
    "predict_km",
    "predict_kcat",
]


def predict_km(substrate: str, enzyme_sequence: str) -> float:  # noqa: ARG001
    raise NotImplementedError


def predict_kcat(substrate: str, product: str, enzyme_sequence: str) -> float:  # noqa: ARG001
    raise NotImplementedError
