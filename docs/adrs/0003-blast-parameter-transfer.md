# ADR 0003: BLAST-Based Sequence Similarity for Cross-Organism Parameter Transfer

**Status:** Implemented
**Scope:** `src/parameteriser/_blast.py`; the `bioconda::blast` dependency (`pixi.toml`,
`linux-64` only)

---

## 1. Context

BRENDA does not have measured kinetic parameters for every enzyme in every organism a
modeler might care about. A common practical workaround in enzyme kinetics is parameter
transfer from a homologous enzyme in a related organism, using sequence similarity as the
justification. `_blast.py` writes a FASTA proteome, builds a local BLAST protein database
(`makeblastdb`), and exposes `blast_sequence_against_others` to find close matches.

## 2. Decision

Shell out to the real NCBI `blast+` binaries (via `subprocess`) rather than a pure-Python
sequence-alignment implementation, and treat the `blast` binary as an optional,
platform-gated dependency: it's declared in `pixi.toml` under
`[target.linux-64.dependencies]` from `bioconda`, not in the base `uv`-managed
`pyproject.toml` dependencies.

## 3. Rationale

BLAST is the standard, trusted tool for this exact task in bioinformatics — reimplementing
sequence alignment/search in Python would be both slower and a correctness risk for no
benefit over calling the real thing. Gating it behind the `pixi`/conda "Full" install path
(see the README's Basic vs. Full installation split) rather than making it a base
dependency keeps the common case (BRENDA lookup only) lightweight and installable via
plain `uv sync`, without forcing every user to have conda/bioconda access or a
Linux-specific binary just to use unrelated parts of the package.

## 4. Consequences

- Anything depending on `blast_sequence_against_others` only works in the `pixi`-managed
  environment, on `linux-64` — this is a real platform constraint, not an oversight; don't
  expect it to work under a plain `uv sync` install or on `osx-arm64`/`win-64`.
- If BLAST-based lookup needs to become a core, always-available feature, that requires
  either broadening the `pixi` platform list or vendoring/depending on a
  cross-platform-installable `blast+` distribution — not a small change.
