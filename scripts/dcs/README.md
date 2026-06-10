# `scripts/dcs/` — Whitney ↔ DCS linkage pipeline

`extract_dcs.py` links every Whitney root to the **Digital Corpus of Sanskrit (DCS)** by
`root = lemma` (IAST), then emits frequency enrichment, a verification audit, participle
indexes, and an editorial worklist. It reads two inputs and writes nothing back to them.

## Run

```sh
python scripts/dcs/extract_dcs.py
```

Defaults assume `VisualDCS` is a sibling of this repo. Override paths if needed:

```sh
python scripts/dcs/extract_dcs.py --db /path/to/dcs_full.sqlite --app-data src/app_data.json
```

Requires only the Python stdlib (`sqlite3`). One full scan of ~1M verb tokens; takes a minute.

## Inputs

| Input | Notes |
|---|---|
| `src/app_data.json` | Whitney roots (935 entries). The join source. |
| `../VisualDCS/src/DCS-data-2026/dcs_full.sqlite` | DCS CoNLL-U corpus (5.69M tokens). **Use `dcs_full`, not the 31 MB `dcs.sqlite` sample.** |

## Outputs

| File | What |
|---|---|
| `src/dcs_freq.json` | Per-root sidecar (keyed by Whitney `id`): `total`, `rank`, `grammar_class`, 9 `participles`, `top_forms`, `ppp`, `preverbs`, `present_stem_signal`. Merged at runtime by `src/core/data.js`. |
| `Whitney_DCS_audit.{md,json}` | Verification: class verdicts (agree/partial/conflict) + PPP confirmation. |
| `Whitney_DCS_worklist.{md,csv}` | Editorial worklist for correcting `app_data.json` — class conflicts the corpus corroborates against Whitney, and unattested PPP, prioritised by frequency. |
| `src/participle_index.json` | Surface participle form → Whitney root + category (powers the form-lookup search). |
| `src/participle_index_dcs.json` | Same, but all DCS verbal roots (~5.5 MB reference). |

## How the linkage works

- **Join key** (`dcs_key`): strip Whitney's `1 `/`2 ` homonym prefix, NFC, unify anusvāra,
  drop avagraha. Conservative — does **not** fold vowel length or sibilants (that would merge
  distinct roots).
- **Curated `ALIASES`**: citation/sandhi spellings auto-normalization can't bridge
  (`gach`→`gam`, `har`→`hṛ`, `prach`→`pracch`, …). Each target hand-verified as attested in DCS.
- After aliasing, **755 / 935** entries link; the rest are genuinely unattested as verbs in DCS.

## Data-encoding traps (cost real debugging)

- DCS token features are **SQL NULL** when absent, not the string `'None'`.
- Verb **class (Gaṇa) is only on `lemma.grammar`** (`"1.P.,4.P.,4.Ā."`), never per-token; a
  lemma string has several `lemma` rows incl. noun homonyms — count verbs via `upos='VERB'`.
- **PPP** = `feat_verbform='Part' AND feat_tense IS NULL`; stem from `m_unsandhied`.
- Whitney verb `classes` are **Roman** (I–X); DCS grammar is **Arabic** (1–10) — normalize
  before comparing or everything looks like a conflict.
- Whitney's `ppp` field is **ASCII diacritic-folded** (`bhuta`); DCS is full IAST (`bhūta`) —
  fold both sides for the PPP test.

## Honesty rules baked into the audit

DCS `grammar` is itself lexicon metadata, so a class disagreement there is *lexicon-vs-lexicon*,
not corpus proof. Absence of a finite class in the corpus is *no evidence*, never "Whitney is
wrong." The present-stem signal is a coarse heuristic; its `athematic` bucket corroborates no
specific class. After editing any `src/*.js`, run `node scripts/bundle.js`.
