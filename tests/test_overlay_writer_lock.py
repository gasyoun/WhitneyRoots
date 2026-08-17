# -*- coding: utf-8 -*-
"""H2892 — the writer lock must actually refuse, and must write nothing.

Every script the H2890 integrity census lists as a writer over one of the three
human-reviewed files is invoked here for real, as a subprocess, with no hatch in
the environment. Two things are asserted per script:

  1. it exits **2** (the refusal code, distinct from its own data errors), and
  2. the three reviewed files are byte-identical afterwards.

(2) is the assertion that matters. A guard that prints a refusal and then falls
through to the write would pass a naive exit-code test on a machine where the
input happens to be missing; hashing the reviewed files before and after is the
only check that cannot be satisfied by luck.

The hatched direction is tested in-process, by calling the guard with a fake
environment. Actually running any of these scripts with ``ALLOW_OVERLAY_WIPE=1``
would rewrite ``src/app_data.json`` — the exact event this whole file exists to
prevent — so no test in this repo may do it.
"""
import ast
import hashlib
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

from overlay_guard import (  # noqa: E402
    DONT_RERUN,
    HATCH,
    REFUSAL_EXIT,
    REVIEWED_FILES,
    hatch_is_set,
    refuse_unless_hatched,
)

#: Every writer the census lists, plus corpus_verify_classes.py, which the
#: DANGER_FACTS do-not-rerun row names. Adding a writer over a reviewed file
#: without adding it here is what test_every_census_writer_is_guarded catches.
GUARDED_SCRIPTS = (
    "scripts/dcs/apply_corpus_inferred_additions.py",
    "scripts/dcs/apply_grammar_confirmed_additions.py",
    "scripts/dcs/apply_ppp_corrections.py",
    "scripts/dcs/apply_section_b_additions.py",
    "scripts/dcs/corpus_verify_classes.py",
    "scripts/dcs/fix_ppp_apparatus_bleed.py",
    "scripts/dcs/fix_ppp_gloss_bleed.py",
    "scripts/dcs/fix_ppp_infinitives.py",
    "scripts/dcs/grammar_ref_builder.py",
    "scripts/dcs/revert_collapse_additions.py",
    "scripts/dict_align.py",
    "scripts/emit_crosswalk.py",
)


def _digests():
    out = {}
    for rel in REVIEWED_FILES:
        path = os.path.join(REPO, rel.replace("/", os.sep))
        with open(path, "rb") as fh:
            out[rel] = hashlib.sha256(fh.read()).hexdigest()
    return out


def _unhatched_env():
    env = dict(os.environ)
    env.pop(HATCH, None)
    # The guard prints the do-not-rerun sentence, which carries an em dash; a
    # cp1252 console would raise UnicodeEncodeError instead of refusing cleanly.
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.mark.parametrize("rel", GUARDED_SCRIPTS)
def test_guarded_script_refuses_and_writes_nothing(rel):
    before = _digests()
    proc = subprocess.run(
        [sys.executable, rel.replace("/", os.sep)],
        cwd=REPO,
        env=_unhatched_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == REFUSAL_EXIT, (
        "%s exited %s, not the refusal code %s.\nstdout:\n%s\nstderr:\n%s"
        % (rel, proc.returncode, REFUSAL_EXIT, proc.stdout, proc.stderr))
    assert DONT_RERUN in proc.stderr, (
        "%s refused without printing the AGENTS.md do-not-rerun sentence" % rel)
    assert _digests() == before, "%s CHANGED a reviewed file while refusing" % rel


#: Basenames of the three reviewed files, for the static writer scan below.
REVIEWED_BASENAMES = tuple(rel.rsplit("/", 1)[-1] for rel in REVIEWED_FILES)


def _module_level_strings(module):
    """name -> its assignment's source text, for resolving `open(APP_DATA, 'w')`."""
    out = {}
    for node in module.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                out[target.id] = ast.unparse(node.value)
    return out


def _writes_a_reviewed_file(source):
    """True when the module opens a reviewed file in write mode.

    Deliberately looks at the write CALL, not at whether the filename appears
    anywhere in the file: three scripts (build_mw_derivations, build_ru_root_glosses,
    build_decisions_doc) READ crosswalk/roots.csv and alignment_review.json and
    write only their own derived artifacts. A substring scan calls those writers
    and would push a guard onto scripts that need none.
    """
    module = ast.parse(source)
    constants = _module_level_strings(module)
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name == "write_text":
            argument = ast.unparse(func.value) if hasattr(func, "value") else ""
        elif name == "open":
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for keyword in node.keywords:
                if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                    mode = str(keyword.value.value)
            if "w" not in mode and "a" not in mode:
                continue
            argument = ast.unparse(node.args[0]) if node.args else ""
        else:
            continue
        expanded = argument + " " + constants.get(argument.strip(), "")
        if any(base in expanded for base in REVIEWED_BASENAMES):
            return True
    return False


def test_every_census_writer_is_guarded():
    """A new writer must not slip in unguarded.

    Any script under scripts/ that opens one of the reviewed files for writing
    has to import the guard. This is the regression that the H2890 census found
    the hard way: eleven writers, none of them locked, all added one at a time.
    """
    missing = []
    for base, _dirs, files in os.walk(os.path.join(REPO, "scripts")):
        for name in sorted(files):
            if not name.endswith(".py") or name == "overlay_guard.py":
                continue
            path = os.path.join(base, name)
            with open(path, encoding="utf-8") as fh:
                source = fh.read()
            if _writes_a_reviewed_file(source) and "overlay_guard" not in source:
                missing.append(os.path.relpath(path, REPO).replace(os.sep, "/"))
    assert not missing, "unguarded writer(s) over reviewed data: %s" % missing


def test_guard_call_precedes_every_write():
    """The guard has to be the FIRST executable statement, not merely present.

    Statement-level, via the AST: a substring scan cannot tell `json.dump` in a
    docstring from `json.dump` in code, and fix_ppp_apparatus_bleed.py documents
    its own write in prose 1,300 bytes above the guard.
    """
    for rel in GUARDED_SCRIPTS:
        path = os.path.join(REPO, rel.replace("/", os.sep))
        with open(path, encoding="utf-8") as fh:
            module = ast.parse(fh.read())
        body = list(module.body)
        if ast.get_docstring(module):
            body.pop(0)
        guard_at = None
        for index, node in enumerate(body):
            rendered = ast.unparse(node)
            if "_refuse_unless_hatched(__file__" in rendered:
                guard_at = index
                break
            assert rendered.startswith(("import ", "from ", "_sys.path.insert")), (
                "%s runs %r before the guard" % (rel, rendered.splitlines()[0]))
        assert guard_at is not None, "%s has no guard call" % rel


def test_hatch_is_exact():
    for value in ("", "0", "true", "TRUE", "yes", "2", " 1"):
        assert not hatch_is_set({HATCH: value}), (
            "%r must not read as consent" % value)
    assert hatch_is_set({HATCH: "1"})


def test_hatched_call_returns_and_does_not_exit():
    assert refuse_unless_hatched(__file__, environ={HATCH: "1"}) is None


def test_unhatched_call_raises_systemexit_2():
    with pytest.raises(SystemExit) as excinfo:
        refuse_unless_hatched(__file__, environ={})
    assert excinfo.value.code == REFUSAL_EXIT
