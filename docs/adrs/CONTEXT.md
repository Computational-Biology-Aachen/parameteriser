# Parameteriser: Architecture Context

This is the entry point for understanding *why* `parameteriser` is shaped the way it is —
written down ahead of a maintainer handoff, alongside the equivalent `docs/adrs/`
directories in the sibling `mxlpy`, `mxlbricks`, `mxlmodels`, `absorpig`, and `schemegen`
repos.

## Independence Is the Central Fact

→ [ADR 0001 — Deliberately independent of `mxlpy` — a standalone parameter-lookup library](0001-independent-of-mxlpy.md)

Unlike `mxlbricks`/`mxlmodels`/`schemegen`, `parameteriser` has zero dependency on
`mxlpy` and is meant to be useful to anyone doing enzyme kinetics, not just `mxlpy` users.
This also explains its outlier packaging: GPL-3 licensed (not MIT) and hosted on GitLab
under a personal namespace rather than the `Computational-Biology-Aachen` GitHub org.

## Getting Parameters, in Order of Confidence

Three independent strategies for filling in a kinetic parameter, roughly from
highest to lowest confidence:

→ [ADR 0002 — Two BRENDA access strategies: `v0` HTML scraping vs. `_v1` official SOAP API](0002-brenda-v0-scraping-vs-v1-soap.md)
→ [ADR 0003 — BLAST-based sequence similarity for cross-organism parameter transfer](0003-blast-parameter-transfer.md)
→ [ADR 0004 — ML-based parameter prediction (`deepmolecules`) kept optional and experimental](0004-deepmolecules-optional-experimental.md)

Read in order: prefer a real measured value from BRENDA (ADR 0002) first; if none exists
for the organism/enzyme in question, fall back to transferring a value from a homologous
sequence via BLAST (ADR 0003); only reach for ML prediction (ADR 0004) — the least
trusted, currently-broken path — when neither of the above has an answer.

## Dual Toolchain

Like `mxlpy` (see its own
[ADR 0012](https://github.com/Computational-Biology-Aachen/MxlPy/blob/main/docs/adrs/0012-dual-uv-pixi-toolchains.md)), `parameteriser`
uses `uv` for the base install and `pixi` for a "Full" install — but for a different
concrete reason here: `pixi`/conda brings in the `bioconda`-only `blast` binary (ADR
0003) and the `deepmolecules` PyPI extra (ADR 0004), not a conda-forge-only Python
package.

## Threads That Cross Multiple ADRs

- **Confidence-ordered fallback, not a single method.** ADR 0002, 0003, and 0004 are the
  same underlying shape: prefer the most directly-verified source of a parameter value
  and only fall back to a weaker method when the stronger one has nothing — never treat
  BLAST transfer or ML prediction as equally trustworthy as a measured BRENDA value.
- **Keep the core lightweight; gate the heavy/fragile stuff behind `pixi`.** Both the
  `blast` binary (ADR 0003) and `deepmolecules` (ADR 0004) are optional, `pixi`-only
  dependencies precisely so a plain `uv sync` for BRENDA lookup alone stays simple and
  reliable even when the optional paths are unavailable or broken.

## See Also

- [`mxlpy`'s `docs/adrs/CONTEXT.md`](https://github.com/Computational-Biology-Aachen/MxlPy/blob/main/docs/adrs/CONTEXT.md),
  ADR 0012, for the sibling dual-toolchain decision with a different concrete driver
  (`assimulo`, not `blast`/`deepmolecules`).
