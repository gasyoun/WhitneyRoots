# Vidyut dhātupāṭha — acquisition provenance (H8020)

_Created: 15-11-2026 · Last updated: 15-11-2026_

What: `dhatupatha.tsv` — the vidyut digital dhātupāṭha (2,259 dhātu, SLP1 upadeśa
+ artha), the data prerequisite for the dhatupatha index mode (D11/D17 of the
`~/.codex/skills/dhatupatha` grill; handoff H8020).

## Upstream identity

- Repo: [ambuda-org/vidyut](https://github.com/ambuda-org/vidyut), file
  [`vidyut-prakriya/data/dhatupatha.tsv`](https://github.com/ambuda-org/vidyut/blob/main/vidyut-prakriya/data/dhatupatha.tsv)
- Upstream commit at retrieval: `c0fa4163799ba822297d47ce36f690e98914d8f3`
  (2024-12-29T18:51:40Z, last commit touching the file)
- Raw URL:
  `https://raw.githubusercontent.com/ambuda-org/vidyut/main/vidyut-prakriya/data/dhatupatha.tsv`
- License: MIT — the upstream data README records the files as sourced from
  ashtadhyayi.com with the author's permission, MIT.

## Landing

- Path: `scratch/vidyut_data/prakriya/dhatupatha.tsv` — **gitignored**
  (`.gitignore` line 9): local-only landing per the H8020 stop condition. To
  re-acquire on any box:
  `curl -sL -o scratch/vidyut_data/prakriya/dhatupatha.tsv https://raw.githubusercontent.com/ambuda-org/vidyut/main/vidyut-prakriya/data/dhatupatha.tsv`
- Retrieved: 15-11-2026, MSI box, by the H8020 parent session.

## Identity receipt

- sha256: `bb2013ead0ea536dc7f887164c385c703cb0014ccf6e5af35b87e6d3049ba380`
- 55,022 bytes; 2,260 lines = 1 header + **2,259 data rows** (verified `wc -l`)
- Header: `code` · `dhatu` · `artha`; first row `01.0001 BU sattAyAm`
  (contract format `01.0001 BU sattAyAm` — exact match); last row
  `10.0509 -` (empty artha, upstream's own content)

## Structural catch (mandated by H8020)

The vidyut `code` column is a **gana.sūtra** numbering (`01.0001`). It joins
DHATUP. x,y coordinates **only BY ROOT, never on the coordinate itself** —
SanskritLexicography
`REUSE_SURVEY_DHATUPATHA_COORDINATE_SOURCES_07-09-2026.md`. Consumers
(index mode, pāda/artha fills) must root-join; coordinate-level joins are
structurally invalid.

## Verification commands

```bash
curl -sL -o dhatupatha.tsv https://raw.githubusercontent.com/ambuda-org/vidyut/main/vidyut-prakriya/data/dhatupatha.tsv
wc -l dhatupatha.tsv          # 2260 = header + 2259
head -2 dhatupatha.tsv        # code/dhatu/artha; 01.0001 BU sattAyAm
sha256sum dhatupatha.tsv      # bb2013ea…
```

_Dr. Mārcis Gasūns_
