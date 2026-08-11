# ADR 0004: ML-Based Parameter Prediction (`deepmolecules`) Kept Optional and Experimental

**Status:** Implemented; currently broken (numpy 1/2 mismatch, per README)
**Scope:** `src/parameteriser/experimental/deepmolecules.py`; `pixi.toml`
`[pypi-dependencies]`

---

## 1. Context

Where BRENDA has no measured value and BLAST-based transfer isn't applicable either,
`experimental/deepmolecules.py` wraps the third-party `deepmolecules` package to *predict*
Km/kcat directly from a substrate/product and enzyme sequence via machine learning. It is
the only ML-based estimation path in `parameteriser`, kept under an `experimental/`
subpackage and only installable via `pixi`'s "Full" path — not `uv`'s base install.

## 2. Decision

Keep `deepmolecules` integration isolated under `experimental/` and gated as an optional
`pixi` extra, rather than a core dependency — including tolerating that it is presently
broken (README: "currently broken due to a numpy 1 / 2 version mismatch") without that
blocking the rest of the package.

## 3. Rationale

`deepmolecules` is an external, less-actively-maintained ML package outside this
project's control — depending on it unconditionally would mean `parameteriser`'s core
BRENDA-lookup functionality (the primary, reliable use case) inherits its
availability/compatibility problems. Scoping it to `experimental/` and an opt-in install
path means a numpy version conflict in `deepmolecules` degrades only the ML-prediction
feature, not the whole package — consistent with treating measured-then-transferred
(BRENDA, then BLAST-based homology) parameters as the trustworthy default and ML
prediction as a last-resort, lower-confidence fallback.

## 4. Consequences

- Don't promote `deepmolecules`-based prediction out of `experimental/` or into the core
  dependency set until its upstream numpy-compatibility issue is actually resolved and it
  has proven stable — the current brokenness is expected, tracked, and contained by
  design, not a surprise regression to fix urgently.
- New ML-based prediction features should follow the same pattern: `experimental/`
  namespace, `pixi`-only optional dependency, never a base `uv` dependency — until a
  method has earned core-dependency trust the way BRENDA/BLAST lookups have.
