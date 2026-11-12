# Sources — psychology-stroop pack

Verification policy (same honesty rule as the ontology file): a bibliographic
check is NOT a full-text read. This table records exactly what was seen, where,
and when.

| # | Source | Kind | Status | What was actually verified |
|---|---|---|---|---|
| 1 | Stroop, J. R. (1935), 'Studies of interference in serial verbal reactions', *Journal of Experimental Psychology* 18(6), 643–662 — https://doi.org/10.1037/h0054651 | PRIMARY | VERIFIED_BIBLIOGRAPHIC | **Bibliographic record only** confirmed through the Crossref API on 2026-11-12 (title, author, journal, volume, issue, pages, DOI). **Full text NOT read.** Its reported finding appears in the store only as DOCUMENTED_CLAIM (PSY-005). |
| 2 | MacLeod, C. M. (1991), 'Half a century of research on the Stroop effect: An integrative review', *Psychological Bulletin* 109(2), 163–203 — https://doi.org/10.1037/0033-2909.109.2.163 | SECONDARY | VERIFIED_BIBLIOGRAPHIC | **Bibliographic record only** confirmed through the Crossref API on 2026-11-12. **Full text NOT read.** Cited as the standard review; its arguments were NOT checked here, and the theory statements are standard textbook-level accounts, not quotations from it. |
| 3 | Speed-accuracy tradeoff literature — locator **required** | REFERENCE | UNVERIFIED | No locator verified in this build. THEORY-SPEED-ACCURACY-TRADEOFF may only name a rival reading; every link is capped at CANDIDATE (T6, demonstrated by REJ-PSY-007). |

## Consequences in the record store

- PSY-005 records Stroop (1935)'s finding as **DOCUMENTED_CLAIM** with a
  `source_mention` evidence row — the source's claim, not our observation. Our
  own OBSERVED records (PSY-001..003) come from the synthetic measurements and
  are marked as such.
- THEORY-AUTOMATICITY-ACCOUNT and THEORY-CAPACITY-ACCOUNT have verified
  sources, so links *may* be INFERRED; PSY-008 keeps that level while stating
  that automaticity itself was not measured.
- THEORY-SPEED-ACCURACY-TRADEOFF has no verified source, so its link (PSY-009)
  is capped at CANDIDATE.
- The synthetic responses support observations **about the file only**.
  Nothing in this pack is a finding about real participants.
