# Sources — physics-pendulum pack

Verification policy (same honesty rule as the ontology file): a bibliographic
check is NOT a full-text read. This table records exactly what was seen, where,
and when.

| # | Source | Kind | Status | What was actually verified |
|---|---|---|---|---|
| 1 | OpenStax, *University Physics Volume 1*, §15.4 "Pendulums" — https://openstax.org/books/university-physics-volume-1/pages/15-4-pendulums | SECONDARY (textbook) | VERIFIED_BIBLIOGRAPHIC | **Section text read** on 2026-11-12 (open access). Read: learning outcomes; simple-pendulum definition (point mass, massless string); restoring force −m·g·sin(θ); small-angle approximation with the stated bound (below ~15°, sin θ vs θ differ by under 1%); period depends on length and g, independent of mass, nearly amplitude-independent below ~15°; "a pendulum can be used to measure the acceleration due to gravity" (Example 15.3 heading). Not peer-reviewed research. |
| 2 | 'Tracking the Acceleration Due to Gravity and Damping of a Pendulum: A Video Analysis', *Physics Education Research Journal* 5(2), 2023 — https://doi.org/10.21580/perj.2023.5.2.16614 | PRIMARY (research paper) | VERIFIED_BIBLIOGRAPHIC | **Bibliographic record only** (title, journal, year, DOI) seen in a Crossref API search result on 2026-11-12. **Full text NOT read.** Cited for the damping frame; its findings were not reproduced here. |
| 3 | Large-angle (anharmonic) period correction — locator **required** | SECONDARY | UNVERIFIED | No locator verified in this build. The term may only name a rival (TERM-SMALL-ANGLE-APPROXIMATION); no link may exceed CANDIDATE. |
| 4 | Measurement uncertainty (e.g. the GUM) — locator **required** | REFERENCE | UNVERIFIED | No locator verified in this build. |
| 5 | Systematic error / experimental methods — locator **required** | REFERENCE | UNVERIFIED | No locator verified in this build. |

## Consequences in the record store

- THEORY-SIMPLE-PENDULUM-MODEL and THEORY-DAMPED-OSCILLATION carry a
  VERIFIED_BIBLIOGRAPHIC source, so links may be INFERRED (PHY-011 is).
- THEORY-ERROR-ANALYSIS has none, so its link (PHY-012) is capped at CANDIDATE
  by gate T6. The cap is demonstrated, not documented away.
- The synthetic measurements support observations **about the file only**.
  Nothing in this pack is a finding about a real pendulum.
