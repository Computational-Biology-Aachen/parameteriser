# ADR 0002: Two BRENDA Access Strategies — `v0` HTML Scraping vs. `_v1` Official SOAP API

**Status:** Implemented (both retained)
**Scope:** `src/parameteriser/brenda/v0/`, `src/parameteriser/brenda/_v1/`

---

## 1. Context

The BRENDA enzyme database has no simple REST API. `brenda/v0/__init__.py` drives a real
browser (`selenium`) to load BRENDA's web pages and scrapes the rendered HTML tables
(`BeautifulSoup`) for kinetic parameters — screen-scraping, coupled tightly to BRENDA's
current page structure. `brenda/_v1/__init__.py` instead uses BRENDA's official SOAP API
via the `zeep` client, authenticating with a registered (hashed) email/password against
`brenda_zeep.wsdl`, and models results as typed dataclasses (`Km`, `Sequence`,
`BrendaType`).

## 2. Decision

Keep both implementations rather than deleting `v0` once `_v1` existed. `_v1` is the
underscore-prefixed, newer, more structurally sound approach (typed results, an official
API contract instead of scraping); `v0` remains for whatever `_v1`'s SOAP surface doesn't
cover or hasn't been ported to yet.

## 3. Rationale

Screen-scraping a live website (`v0`) is inherently brittle — any BRENDA front-end
redesign can silently break table extraction — and requires a full browser via
`selenium`, a heavy runtime dependency for what should be a data lookup. The official
SOAP API (`_v1`) is the structurally correct long-term approach: a stable, versioned
contract with typed responses instead of scraped HTML. It wasn't a straight swap because
BRENDA's SOAP API may not (yet) expose everything the HTML tables do, and the migration
from one to the other is itself real work — hence `_v1` existing as newer, actively
developed code alongside `v0`, not `v0` being deleted outright the moment `_v1` existed.

## 4. Consequences

- Prefer `_v1` for any new lookup capability going forward — reach for `v0`'s
  selenium/BeautifulSoup approach only if the SOAP API genuinely doesn't expose the
  needed data.
- `v0`'s selenium dependency is a real deployment cost (a browser must be available in
  whatever environment runs it) that `_v1` avoids — this is itself a reason to prefer
  `_v1` wherever it's sufficient, independent of BRENDA's page structure risk.
- The `_v1` prefix (leading underscore, signaling not-yet-fully-public/stable API) should
  be revisited and dropped once `_v1` is confirmed to cover the cases that still send
  callers to `v0`.
