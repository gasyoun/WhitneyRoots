# -*- coding: utf-8 -*-
"""Refuse-by-default writer lock over the human-reviewed WhitneyRoots overlays (H2892).

This repo had no write lock anywhere. The H2890 integrity census found eleven
scripts that open one of the three human-reviewed files with ``'w'`` and rewrite
it whole:

    src/app_data.json            (935 lexicon records)
    crosswalk/roots.csv          (930 rows)
    crosswalk/alignment_review.json

AGENTS.md has said "do not re-run these" since the beginning, and prose is not a
gate: Phase 8 already reverted 120 of 139 empirical class additions once. H2891
added the *detector* (a committed digest per reviewed file, checked in CI). This
module is the *lock* — the writers refuse to run at all.

Contract
--------
A guarded script exits **2** and writes nothing unless ``ALLOW_OVERLAY_WIPE=1``
is set in the environment. Exit 2 is deliberately distinct from the scripts' own
data errors (``SystemExit('ERROR: ...')`` -> 1), so a caller can tell "I was
refused" from "the data was wrong".

The hatch is exact: the literal string ``1``. Anything else — ``true``, ``yes``,
an empty string — refuses, because a half-set hatch must not read as consent.

Setting the hatch is not a formality. It means: this run is expected to rewrite
a reviewed file, the human overlay in it is either being restored deliberately
or is known to be absent, and the tripwire pin will be re-pinned in the SAME
commit with a reason. If that sentence is not true, do not set the hatch.

``corpus_verify_classes.py`` is guarded too, deliberately. The census measured
it and found it opens ``src/app_data.json`` read-only and writes only
``corpus_class_verdicts.json`` — it is not a wiper. But it is named alongside
``apply_*`` in the DANGER_FACTS do-not-rerun row, and narrowing a safety fence is
a human decision, not a side effect of an implementation pass. Guarding a
read-only consumer costs one environment variable; un-guarding it on an agent's
say-so could cost a reviewed overlay.

Usage, at the very top of a writer, before its own imports do any work::

    import pathlib, sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from overlay_guard import refuse_unless_hatched
    refuse_unless_hatched(__file__)
"""
import os
import sys

#: The one escape hatch. Exact string match on ``1``.
HATCH = 'ALLOW_OVERLAY_WIPE'

#: Verbatim from the generated block of
#: https://github.com/gasyoun/WhitneyRoots/blob/main/AGENTS.md
DONT_RERUN = (
    'apply_* and corpus_verify are DO-NOT-RERUN overlay-wipers (they destroy '
    'human-reviewed overlays) — produce new additive artifacts only, never '
    'write into reviewed crosswalk files'
)

#: The three files the H2890 census declares human-reviewed, repo-relative.
REVIEWED_FILES = (
    'src/app_data.json',
    'crosswalk/roots.csv',
    'crosswalk/alignment_review.json',
)

REFUSAL_EXIT = 2


def hatch_is_set(environ=None):
    """True only for the exact string ``1``."""
    env = os.environ if environ is None else environ
    return env.get(HATCH) == '1'


def refuse_unless_hatched(script, targets=REVIEWED_FILES, rewrites=True,
                          environ=None):
    """Exit 2 with the do-not-rerun sentence unless the hatch is set.

    ``script`` is the caller's ``__file__``; ``targets`` names the reviewed files
    this particular writer touches, for the operator reading the refusal.
    ``rewrites=False`` marks a script the census measured as read-only over
    those files but that the DANGER_FACTS fence still names (see the module
    docstring on ``corpus_verify_classes.py``), so the refusal does not claim a
    write that does not happen. Returns ``None`` when the hatch is set, so a
    hatched run proceeds untouched.
    """
    if hatch_is_set(environ):
        return None

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):  # pragma: no cover - exotic streams
            pass

    name = os.path.basename(script)
    listed = '\n'.join('    %s' % target for target in targets)
    preamble = 'It rewrites, in full:' if rewrites else (
        'The census measured it as read-only over these reviewed files, but the\n'
        'DANGER_FACTS do-not-rerun row names it and only a human may narrow that:')
    sys.stderr.write(
        'REFUSED: %s is a guarded writer over human-reviewed data (H2892).\n'
        '\n'
        '%s\n'
        '\n'
        '%s\n'
        '%s\n'
        '\n'
        'Nothing was written. If this run is genuinely meant to rewrite a\n'
        'reviewed file, set the hatch and re-pin the tripwire in the same commit:\n'
        '\n'
        '    %s=1 python %s\n'
        '    python -m csl_pyutil.integrity_tripwire --extract \\\n'
        '           --pin data/integrity/whitney_roots.pin.json --write-pin \\\n'
        '           --reason "what changed and why" --updated DD-MM-YYYY\n'
        '\n'
        'If it is not, the additive route is a NEW artifact next to the reviewed\n'
        'file, never a rewrite of it.\n'
        % (name, DONT_RERUN, preamble, listed, HATCH, name)
    )
    raise SystemExit(REFUSAL_EXIT)
