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
import csv
import fnmatch
import os
import subprocess
import sys

#: The one escape hatch. Exact string match on ``1``.
HATCH = 'ALLOW_OVERLAY_WIPE'

#: H6980: the protected-path registry, canonical in kosha and vendored here.
#: The guard refuses by PATH, so a new builder that targets a reviewed file is
#: caught even when its script name was never on the H2890 list.
REGISTRY_REL = 'data/manifest/protected_paths.tsv'

#: Test/CI override, mirroring the csl-atlas generator's registry argument.
REGISTRY_ENV = 'OVERLAY_GUARD_REGISTRY'

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

#: H6980 fallback only: when the registry file is absent, the twelve writers the
#: H2892 census named keep refusing as before. This is NOT the live protection —
#: the registry is.
GUARDED_SCRIPT_NAMES = (
    'apply_corpus_inferred_additions.py',
    'apply_grammar_confirmed_additions.py',
    'apply_ppp_corrections.py',
    'apply_section_b_additions.py',
    'corpus_verify_classes.py',
    'fix_ppp_apparatus_bleed.py',
    'fix_ppp_gloss_bleed.py',
    'fix_ppp_infinitives.py',
    'grammar_ref_builder.py',
    'revert_collapse_additions.py',
    'dict_align.py',
    'emit_crosswalk.py',
)

REFUSAL_EXIT = 2


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _repo_name():
    """Repo slug for registry rows: env override, git remote, then dirname."""
    explicit = os.environ.get('OVERLAY_GUARD_REPO')
    if explicit:
        return explicit
    root = _repo_root()
    try:
        url = subprocess.check_output(
            ['git', '-C', root, 'config', '--get', 'remote.origin.url'],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:  # pragma: no cover - git absent is not a refusal reason
        url = ''
    if url:
        name = url.rstrip('/').rsplit('/', 1)[-1]
        if name.endswith('.git'):
            name = name[:-4]
        if name:
            return name
    return os.path.basename(root)


def _normalise(target):
    """Repo-relative POSIX spelling, so globs match on every platform."""
    if os.path.isabs(target):
        try:
            target = os.path.relpath(target, _repo_root())
        except ValueError:  # different drive on Windows
            return str(target).replace('\\', '/')
    target = str(target).replace('\\', '/')
    while target.startswith('./'):
        target = target[2:]
    return target


def registry_path(registry=None, environ=None):
    env = os.environ if environ is None else environ
    if registry:
        return registry
    override = env.get(REGISTRY_ENV)
    if override:
        return override
    return os.path.join(_repo_root(), *REGISTRY_REL.split('/'))


def load_protected_paths(registry=None, environ=None):
    """Return this repo's protected globs, or ``None`` when no registry exists.

    A missing or malformed registry is not consent: the caller falls back to
    the embedded H2892 names. An empty tuple means the registry exists and has
    no rows for this repo, so path matching simply protects nothing here.
    """
    path = registry_path(registry=registry, environ=environ)
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding='utf-8', newline='') as fh:
        rows = (line for line in fh
                if line.strip() and not line.lstrip().startswith('#'))
        reader = csv.DictReader(rows, delimiter='\t')
        required = {'repo', 'path_glob', 'reason', 'owner', 'since'}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            return None
        repo = _repo_name()
        return tuple(
            row['path_glob'].strip().replace('\\', '/')
            for row in reader
            if (row.get('repo') or '').strip() == repo
            and (row.get('path_glob') or '').strip()
        )


def is_protected_path(target, protected=None, environ=None):
    """True when ``target`` matches a registry glob (or a fallback reviewed file)."""
    if protected is None:
        protected = load_protected_paths(environ=environ)
    normalised = _normalise(target)
    if protected is None:
        return normalised in REVIEWED_FILES
    return any(fnmatch.fnmatchcase(normalised, glob) for glob in protected)


def hatch_is_set(environ=None):
    """True only for the exact string ``1``."""
    env = os.environ if environ is None else environ
    return env.get(HATCH) == '1'


def refuse_unless_hatched(script, targets=None, rewrites=True,
                          environ=None, registry=None):
    """Exit 2 when a target is protected and the hatch is unset.

    ``script`` is the caller's ``__file__``; ``targets`` names the paths this
    writer touches. Protection is decided by matching those paths against the
    registry (H6980), not by the script name, so a new builder over a reviewed
    file is refused just like the original twelve. When the registry file is
    missing, the H2892 behaviour is the fallback: the twelve named writers and
    the three reviewed files still refuse.

    ``rewrites=False`` marks a script the census measured as read-only over
    those files but that the DANGER_FACTS fence still names (see the module
    docstring on ``corpus_verify_classes.py``), so the refusal does not claim a
    write that does not happen. Returns ``None`` when nothing protected is
    targeted or the hatch is set, so the run proceeds untouched.
    """
    env = os.environ if environ is None else environ
    if hatch_is_set(env):
        return None

    candidates = REVIEWED_FILES if targets is None else tuple(targets)
    protected = load_protected_paths(registry=registry, environ=env)
    if protected is None:
        name = os.path.basename(script)
        hit = name in GUARDED_SCRIPT_NAMES or any(
            _normalise(target) in REVIEWED_FILES for target in candidates)
        if not hit:
            return None
        matched = candidates or REVIEWED_FILES
    else:
        matched = tuple(target for target in candidates
                        if is_protected_path(target, protected))
        if not matched:
            return None

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):  # pragma: no cover - exotic streams
            pass

    name = os.path.basename(script)
    listed = '\n'.join('    %s' % target for target in matched)
    preamble = 'It rewrites, in full:' if rewrites else (
        'The census measured it as read-only over these reviewed files, but the\n'
        'DANGER_FACTS do-not-rerun row names it and only a human may narrow that:')
    sys.stderr.write(
        'REFUSED: %s targets human-reviewed data (H2892/H6980).\n'
        '\n'
        '%s\n'
        '\n'
        '%s\n'
        '%s\n'
        '\n'
        'Protected paths come from %s, not from this script name.\n'
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
        % (name, DONT_RERUN, preamble, listed, REGISTRY_REL, HATCH, name)
    )
    raise SystemExit(REFUSAL_EXIT)
