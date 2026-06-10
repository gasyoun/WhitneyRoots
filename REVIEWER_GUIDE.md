<!--
  REVIEWER_GUIDE.md — bilingual (English / Русский)
  Human-reviewer algorithm for the Whitney-Grammar / DCS verification work.
  Authority order everywhere: Whitney Grammar  >  Whitney Roots  >  DCS corpus  >  Zalizniak (tie-breaker for the hard cases).
-->

# Whitney Roots — Reviewer Guide & Algorithm
# Whitney Roots — Руководство и алгоритм для проверяющего

> **Authority order / Порядок авторитетности:**
> Whitney **Grammar** (§§) → Whitney **Roots** (`app_data.json`) → **DCS** corpus → **Zalizniak** (tie-breaker).
> The corpus is the *lowest* authority and can only *suggest*, never *decide*.
> Корпус — *низший* авторитет: он только *подсказывает*, но не *решает*.

---

## EN — What happened and why a review is needed

The automated pass added 139 verb-class entries to `app_data.json` from a DCS-corpus
present-stem heuristic. A critical review found the heuristic **cannot distinguish class I
from class VI** — they differ only by accent (`cárati` I vs. `tudáti` VI), and the DCS forms
carry no usable accent, so the script returned "I, VI" for almost every thematic root and then
"completed the pair." **120 of those additions were reverted** to the pure Whitney Roots class
set; **19 were kept but flagged** because they add a *genuinely distinct* class (III, IV, VII…)
that still needs a human + Zalizniak to confirm.

Nothing in Whitney Roots was deleted — every revert only *removed a corpus-added class*, never
an original one. The corpus analysis is preserved as advisory documents.

Your job: walk the queues below in order, decide each case against the Grammar (and Zalizniak
for ties), and record the decision.

## RU — Что произошло и зачем нужна проверка

Автоматический проход добавил в `app_data.json` 139 классов глаголов на основе эвристики
по основам настоящего времени из корпуса DCS. Критическая проверка показала, что эвристика
**не может отличить I класс от VI** — они различаются только ударением (`cárati` I и `tudáti` VI),
а формы DCS не несут пригодного ударения; поэтому скрипт почти для каждого тематического корня
выдавал «I, VI» и «дополнял пару». **120 таких добавлений откатили** к чистому набору классов
Whitney Roots; **19 оставили с пометкой**, потому что они добавляют *действительно иной* класс
(III, IV, VII…), который всё же требует подтверждения человеком и по Зализняку.

Из Whitney Roots ничего не удалено — откат всегда *убирал только класс, добавленный из корпуса*,
никогда исходный. Корпусный анализ сохранён как справочные документы.

Задача: пройти очереди ниже по порядку, решить каждый случай по Грамматике (а в спорных —
по Зализняку) и зафиксировать решение.

---

## The review queues (priority order) / Очереди проверки (по приоритету)

| # | Queue / Очередь | Count | File to open / Файл |
|---|---|---|---|
| **A** | Kept class additions / Оставленные добавления классов | 19 | `review_queue.json` |
| **B** | High-frequency PPP, suspicious / Частотные ППП, подозрительные | 12 | `ppp_source_validation.md` → SUSPICIOUS |
| **C** | Malformed PPP, likely error / Дефектные ППП, вероятная ошибка | 76 | `ppp_source_validation.md` → LIKELY_ERROR |
| **D** | Grammar "exception" tags / Метки «exception» | 101 | `src/grammar_refs.json` |
| **E** | Reverted I/VI pairs (optional re-check) / Откаты I/VI | 117 | `git show <commit>` + Zalizniak |

---

## EN — General algorithm for ONE item

```
1. LOCATE   open the queue file, take the next id (root).
2. STATE    note current classes / PPP in src/app_data.json for that id.
3. GRAMMAR  grep the Grammar text for the root and the relevant §:
              grep -n "<root>" src/wg_text.txt
            or look the § up in Whitney_Grammar_Citations.md (column "Grammar §§").
            Read the paragraph. Does Whitney's Grammar assign the class / list the PPP?
4. DECIDE   Grammar confirms      → KEEP  (mark "confirmed: §NNN").
            Grammar contradicts   → REVERT/CORRECT (mark "§NNN says X").
            Grammar silent        → consult Zalizniak:
                                      Zalizniak confirms → KEEP (mark "Zal. vol/p").
                                      Zalizniak silent   → REVERT to Whitney Roots
                                                           (corpus alone is not enough).
5. RECORD   write the verdict + citation into review_queue.json ("status",
            "verdict", "evidence"); for data edits change src/app_data.json.
6. BUNDLE   after any src/ edit:  node scripts/bundle.js
```

### How to tell class I from class VI (the crux)

Without accent you cannot use the bare stem. Decide by **root-vowel grade**, which *does* differ:

| | Class I (bhū-type) | Class VI (tud-type) |
|---|---|---|
| Root grade | **guṇa** (strengthened): `bhū→bháva`, `nī→náya` | **zero/weak** (unstrengthened): `tud→tudá`, `viś→viśá` |
| Accent | on the root | on the thematic `-á` |
| Tell-tale | root vowel raised (e/o, ar) | root vowel stays i/u/ṛ |

So for a root whose vowel *would* change under guṇa, the surface form still decides
(`viśáti` keeps `i` ⇒ VI; a class-I form would be `*véśati`). For roots where guṇa changes
nothing (`car`, `nam`, fixed `a`), **the corpus is silent — defer to Whitney/Zalizniak.**

## RU — Общий алгоритм для ОДНОГО пункта

```
1. НАЙТИ    откройте файл очереди, возьмите следующий id (корень).
2. СОСТОЯНИЕ зафиксируйте текущие classes / ППП в src/app_data.json для этого id.
3. ГРАММАТИКА найдите корень и нужный § в тексте Грамматики:
              grep -n "<корень>" src/wg_text.txt
            или по таблице Whitney_Grammar_Citations.md (столбец «Grammar §§»).
            Прочитайте абзац. Назначает ли Грамматика этот класс / приводит ли ППП?
4. РЕШЕНИЕ  Грамматика подтверждает → ОСТАВИТЬ (пометка «confirmed: §NNN»).
            Грамматика противоречит  → ОТКАТ/ИСПРАВИТЬ (пометка «§NNN говорит X»).
            Грамматика молчит        → смотреть Зализняка:
                                        подтверждает → ОСТАВИТЬ (пометка «Зал. том/с.»).
                                        молчит       → ОТКАТ к Whitney Roots
                                                       (одного корпуса недостаточно).
5. ЗАПИСАТЬ вердикт + ссылку в review_queue.json («status», «verdict», «evidence»);
            правки данных — в src/app_data.json.
6. СБОРКА   после любой правки в src/:  node scripts/bundle.js
```

### Как отличить I класс от VI (суть проблемы)

Без ударения «голая» основа не помогает. Решайте по **ступени корневого гласного**, она различается:

| | I класс (тип bhū) | VI класс (тип tud) |
|---|---|---|
| Ступень корня | **гуна** (усиленная): `bhū→bháva`, `nī→náya` | **нулевая/слабая**: `tud→tudá`, `viś→viśá` |
| Ударение | на корне | на тематическом `-á` |
| Признак | гласный корня повышен (e/o, ar) | гласный остаётся i/u/ṛ |

Если под гуной гласный *менялся бы*, поверхностная форма всё решает (`viśáti` сохраняет `i` ⇒ VI;
форма I класса была бы `*véśati`). Где гуна ничего не меняет (`car`, `nam`, фиксированное `a`) —
**корпус молчит, решает Уитни/Зализняк.**

---

## Queue A — the 19 kept class additions (worked examples)

`review_queue.json` lists all 19. Highest-value cases and what to check:

| id | root | Whitney Roots | added | Where to look / verdict hint |
|---|---|---|---|---|
| 120 | krī | IX | **+I** | §717+ (nā-class). krī is the paradigm root `krīṇā́ti`. No class-I krī exists → **likely REVERT.** |
| 269 | jñā | I, IX | **+IV** | `jñāyate` is the **passive** (yá-stem), not class IV. Check §761/§768 → probably REVERT. |
| 494 | bandh | I, IX | **+IV** | Same passive-vs-IV trap as jñā. Check Grammar. |
| 402 | dhṛ | I | **+IV** | `dhriyáte` is passive/medial. Check before keeping. |
| 141/142 | kṣi | I, II, VI | **+IV** | Multiple kṣi roots; check meaning + §. |
| 227 | cit | I | **+III** | cit has reduplicated `cikitti`-forms → III plausible; confirm in §642+. |
| 352 | 4 dā | ∅ | **+III** | First read the *meaning* field — which dā is "4 dā"? Only "give" is III (`dádāti`). |
| 365 | du | V | **+VII** | du `dunóti` is V; VII (nasal-infix) doubtful → check §683+. |
| 397 | dhi | V | **+VII** | Same as du. |
| 914 | hi | I, V | **+VII** | hi `hinóti` is V; VII doubtful. |
| 862 | stan | I, II | **+VII** | Doubtful; check. |
| 473/578/890 | pṛṇ, mṛṇ, sphur | ∅ | **+I,VI** | Whitney Roots gave no class; these are transfers discussed at §731. Decide from §. |
| 719–721 | vā | II, IV | **+I** | "blow" (II `vā́ti`) vs "weave" (IV); check which entry, then §. |
| 75 | ṛdh | IV, V, VII | **+I** | I doubtful on top of three classes; check §. |

**Default rule for Queue A:** if the Grammar paragraph does **not** state the added class and
Zalizniak does not either, **revert** (set `classes` back to the Whitney Roots value shown).

---

## Queue B — 12 suspicious high-frequency PPP (`ppp_source_validation.md`)

These roots occur 1000+ times yet the listed PPP never appears in DCS. Morphology is clean,
so the form is *possible* — the question is whether Whitney's listed PPP is right.

- `han` → `ghata` (8 744×): the normal PPP is **`hata`**; `ghata` looks wrong → check §954+.
- `vad` → `vadita`, `kṣip` → `kṣipita`, `tap` → `tapita`, `tyaj` → `tyajita`: `-ita` set-forms;
  confirm against §956 (set vs aniṭ). Many class-I roots take plain `-ta` (`tapta`, `tyakta`).
- `pṛ` → `pṛta / pūrta`: check §957d.

**Action:** for each, read the Grammar PPP §; if Whitney's Grammar gives a different PPP,
correct `app_data.json`; if Grammar agrees, keep and mark "Vedic/rare, corpus gap."

## Queue C — 76 malformed PPP, likely error (`ppp_source_validation.md`)

These are almost certainly source-extraction artifacts, not real PPP:

- `-tos`, `-tvi`, `-tave`, `-dhyai`, `-os` endings = infinitive/sandhi fragments, **not** PPP.
  (The 12 worst — `vastave`, `saktave`, `ratave`, `tamitos`, `ksaradhyai` … — were already
  removed.) Continue with: `janitos→janita`, `labdhva→labdha`, `bhugna 1→bhagna`, etc.
- **Action:** correct to the standard `-ta`/`-na` form, or delete the fragment. Cite the § that
  gives the true PPP.

## Queue D — 101 "exception" tags (`src/grammar_refs.json`)

The `type:"exception"` flag was auto-set when an exception keyword sat within 100 chars of the
root. Short roots (e.g. `as`, `i`) match English words and stray text, so some tags are false.

- **Action:** open the `snippet` field; if the sentence is really about that root deviating,
  keep; otherwise downgrade `exception`→`specific`/`generic`. Spot-check ~20 first.

---

## Recording verdicts / Запись вердиктов

Edit `review_queue.json`, per item, add:

```json
{ "id": "120", "root": "krī",
  "status": "REVIEWED",
  "verdict": "REVERT",            // KEEP | REVERT | CORRECT
  "evidence": "§717 — krī is the nā-class paradigm; no class-I present.",
  "authority": "Grammar"          // Grammar | Zalizniak | Roots
}
```

Data edits go in `src/app_data.json`; then run `node scripts/bundle.js`.
For provenance, commit messages start `review:` (e.g. `review: revert krī +I per §717`).

Правки данных — в `src/app_data.json`; затем `node scripts/bundle.js`.
Коммиты проверки начинаются с `review:`.

---

## Files map / Карта файлов

| File | Role |
|---|---|
| `src/app_data.json` | **Live data.** The only file the app reads. Edit here. |
| `review_queue.json` | Queue A — 19 kept additions to adjudicate. |
| `Whitney_Grammar_Citations.md` | §-citation table for all 935 roots (human-readable). |
| `src/grammar_refs.json` | Machine citations + snippets + exception tags (Queue D). |
| `src/wg_text.txt` | Full Grammar text — grep here for any § or root. |
| `ppp_source_validation.md` | Queues B & C (PPP). |
| `PPP_CORRECTION_PLAN.md` | Detailed PPP rationale. |
| `detailed_conflict_triage.md`, `candidates_for_addition.md` | **Superseded** analysis (see headers) — historical only. |
| `scripts/dcs/revert_collapse_additions.py` | The revert that produced the current state (re-runnable). |

_Generated as part of the Whitney Grammar verification work. Keep the authority order sacred:
Grammar > Roots > corpus > Zalizniak-as-tiebreaker._
