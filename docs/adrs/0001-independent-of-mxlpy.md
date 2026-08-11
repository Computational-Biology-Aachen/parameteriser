# ADR 0001: Deliberately Independent of `mxlpy` — a Standalone Parameter-Lookup Library

**Status:** Implemented
**Scope:** whole package — most concretely `pyproject.toml`'s `dependencies` (no `mxlpy`
entry at all)

---

## 1. Context

`parameteriser` looks up and estimates enzyme kinetic parameters (from the BRENDA
database, sequence homology via BLAST, and ML prediction) — the kind of parameter values
an `mxlpy` model's rate laws consume. Despite that natural fit, `parameteriser` has no
`mxlpy` dependency anywhere in its `pyproject.toml`, and none of its modules import it.

## 2. Decision

Keep `parameteriser` fully standalone from `mxlpy` and the rest of the `mxlbricks`/
`mxlmodels` dependency graph. Any integration between the two happens in the caller's
code (e.g. a modeling notebook importing both and wiring `parameteriser`'s output into an
`mxlpy` model's parameters by hand), never inside `parameteriser` itself.

## 3. Rationale

Parameter lookup from BRENDA/BLAST/ML prediction is a genuinely separate problem from
mechanistic model-building, useful to anyone doing enzyme kinetics work regardless of
which (if any) ODE modeling framework they use downstream. Coupling `parameteriser` to
`mxlpy`'s `Model`/`Parameter` types would narrow its audience to `mxlpy` users for no
real technical benefit — the two packages don't share data structures that need
synchronizing, only a data hand-off (a parameter value) that any consumer can use however
it likes.

## 4. Consequences

- Don't add an `mxlpy`-specific convenience layer (e.g. "apply looked-up parameters
  directly to a `Model`") inside `parameteriser` — that glue belongs in the calling
  code or in a separate integration module, not in this package's core.
- When `mxlpy`'s own APIs change, `parameteriser` is unaffected — there is no coupling to
  break. Conversely, `parameteriser` changes never need to consider `mxlpy` compatibility.
- This independence is also why `parameteriser` is licensed GPL-3 (unlike the MIT-licensed
  rest of the tool family) and hosted on GitLab rather than the
  `Computational-Biology-Aachen` GitHub org — it predates, and was never folded into, that
  later organizational convention.
