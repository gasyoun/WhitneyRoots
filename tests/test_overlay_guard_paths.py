# -*- coding: utf-8 -*-
"""H6980 — the overlay guard refuses by protected PATH, not by script name.

The three cases are the acceptance fixture:

  1. a builder that is not one of the twelve H2892 scripts, targeting a
     protected path, exits 2 without the hatch and writes nothing;
  2. the same builder with ``ALLOW_OVERLAY_WIPE=1`` writes;
  3. the same builder on an unprotected path writes without the hatch.

The registry is passed explicitly so the test owns the protected path and never
writes near a real human-reviewed file. The repo's own registry is exercised by
the unchanged H2892 tests in ``test_overlay_writer_lock.py``.
"""
import csv
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

from overlay_guard import (  # noqa: E402
    HATCH,
    REFUSAL_EXIT,
    load_protected_paths,
    refuse_unless_hatched,
)

FIXTURE = os.path.join(REPO, "tests", "fixtures", "h6980_new_builder.py")
PROTECTED = "scratch/h6980/protected.json"
UNPROTECTED = "scratch/h6980/free.json"
HEADER = ("repo", "path_glob", "reason", "owner", "since")


def _registry(tmp_path):
    path = tmp_path / "protected_paths.tsv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerow(("WhitneyRoots", PROTECTED,
                         "test fixture human-reviewed file",
                         "H6980 fixture", "2026-10-18"))
    return path


def _run(target, registry, hatch=False):
    env = dict(os.environ)
    env.pop(HATCH, None)
    if hatch:
        env[HATCH] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, FIXTURE, "--target", target,
         "--registry", str(registry)],
        cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")


def _remove(*targets):
    for target in targets:
        path = os.path.join(REPO, *target.split("/"))
        if os.path.exists(path):
            os.remove(path)


def test_new_builder_refuses_protected_path_without_hatch(tmp_path):
    _remove(PROTECTED)
    proc = _run(PROTECTED, _registry(tmp_path))
    assert proc.returncode == REFUSAL_EXIT, proc.stderr
    assert "Protected paths come from" in proc.stderr
    assert not os.path.exists(os.path.join(REPO, *PROTECTED.split("/"))), (
        "the guard refused but the builder still wrote the protected path")
    _remove(PROTECTED)


def test_new_builder_writes_protected_path_with_hatch(tmp_path):
    _remove(PROTECTED)
    proc = _run(PROTECTED, _registry(tmp_path), hatch=True)
    assert proc.returncode == 0, proc.stderr
    path = os.path.join(REPO, *PROTECTED.split("/"))
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        assert fh.read() == "fixture\n"
    _remove(PROTECTED)


def test_new_builder_writes_unprotected_path_without_hatch(tmp_path):
    _remove(UNPROTECTED)
    proc = _run(UNPROTECTED, _registry(tmp_path))
    assert proc.returncode == 0, proc.stderr
    path = os.path.join(REPO, *UNPROTECTED.split("/"))
    assert os.path.exists(path)
    _remove(UNPROTECTED)


def test_missing_registry_falls_back_to_the_twelve_script_names(tmp_path):
    absent = str(tmp_path / "absent.tsv")
    with pytest.raises(SystemExit) as excinfo:
        refuse_unless_hatched(
            "scripts/dcs/apply_ppp_corrections.py",
            targets=("scratch/anything.json",),
            registry=absent, environ={})
    assert excinfo.value.code == REFUSAL_EXIT
    assert refuse_unless_hatched(
        "scripts/h6980_new_builder.py", targets=(UNPROTECTED,),
        registry=absent, environ={}) is None


def test_repo_registry_is_narrow_and_owned():
    registry = os.path.join(REPO, "data", "manifest", "protected_paths.tsv")
    paths = load_protected_paths(registry=registry)
    assert paths, "the repo must ship its protected-path registry"
    for path in paths:
        assert not path.endswith(("/", "/**")), (
            "H6980 forbids directory-wide protection: %s" % path)
    with open(registry, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            assert row["repo"] and row["path_glob"]
            assert row["reason"].strip(), "every row needs a reason"
            assert row["owner"].strip(), "every row needs an owner"
            assert row["since"].strip(), "every row needs a since date"
