#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_whitney.py — Layer-2 ingest of Whitney's *Sanskrit Grammar* (2nd ed., 1889)
from English Wikisource into a structured, citable section graph.

WhitneyRoots project, DESIGN.md §7 (form->§ concordance) and §9 Phase 3.

------------------------------------------------------------------------------
WIKISOURCE STRUCTURE (discovered 2026-06-13)
------------------------------------------------------------------------------
Root page : https://en.wikisource.org/wiki/Sanskrit_Grammar_(Whitney)
The work is split into ONE subpage PER CHAPTER, addressed by Roman numeral:

    Sanskrit_Grammar_(Whitney)/Chapter_I  ... /Chapter_XVIII
    plus /Preface, /Introduction, /Appendix, /Sanskrit_Index, /General_Index

Each chapter page carries Whitney's numbered sections ("paragraphs") 1..1340.
In the rendered HTML, every section number is an explicit anchor span:

    <span id="781" title="Anchor:781" style="font-weight: bold;"
          class="wst-anchor">781.</span> The formation of the perfect ...

so a single section is directly addressable by URL fragment, e.g.
    https://en.wikisource.org/wiki/Sanskrit_Grammar_(Whitney)/Chapter_X#781

Letter sub-sections (781a, 781b, ...) use the SAME span class but a
non-numeric id; we capture only the integer top-level § as a record, and keep
the sub-section text inside that record's body (matching Whitney's own layout).

We fetch the rendered HTML via the MediaWiki API (action=parse&prop=text),
which is stable and gives us the anchor spans verbatim:
    https://en.wikisource.org/w/api.php?action=parse&page=...&prop=text&format=json

------------------------------------------------------------------------------
OUTPUT — src/whitney_sections.json
------------------------------------------------------------------------------
{
  "_meta": { ...provenance, what was fetched vs deferred... },
  "sections": [
    { "section_number": 781,
      "chapter": "X",
      "chapter_title": "The Perfect-System",
      "title": null,                # Whitney sections have no per-§ title
      "text": "The formation of the perfect ...",
      "wikisource_url": ".../Chapter_X#781",
      "char_len": 1234 },
    ...
  ]
}

------------------------------------------------------------------------------
USAGE
------------------------------------------------------------------------------
    python fetch_whitney.py             # PILOT: Chapters X + XIII (proves pipeline)
    python fetch_whitney.py --pilot     # same as default
    python fetch_whitney.py --full      # ALL verb-system chapters IX..XV
    python fetch_whitney.py --all       # every chapter I..XVIII
    python fetch_whitney.py --chapters X,XIII,XI
    python fetch_whitney.py --refresh   # ignore HTML cache, re-download

Idempotent: raw chapter HTML is cached under scratch/wikisource/<Chapter>.html
and reused on subsequent runs unless --refresh is given. Re-running overwrites
src/whitney_sections.json deterministically.
"""

import sys
import os
import re
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from html import unescape

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Paths (resolved relative to the repo root, two levels up from this script)
# --------------------------------------------------------------------------- #
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir))
CACHE_DIR = os.path.join(REPO_ROOT, "scratch", "wikisource")
OUT_PATH = os.path.join(REPO_ROOT, "src", "whitney_sections.json")

# --------------------------------------------------------------------------- #
# Wikisource constants
# --------------------------------------------------------------------------- #
API = "https://en.wikisource.org/w/api.php"
PAGE_BASE = "https://en.wikisource.org/wiki/Sanskrit_Grammar_(Whitney)"
WORK_PREFIX = "Sanskrit_Grammar_(Whitney)"
UA = (
    "WhitneyRootsCrosswalk/0.1 "
    "(https://github.com/sanskrit-lexicon/WhitneyRoots; gasyoun@gmail.com) "
    "Layer2-ingest research-bot"
)
POLITE_DELAY_S = 1.5  # be polite between live fetches

# Roman-numeral chapter subpages, in order. Titles match the Wikisource ToC.
CHAPTERS = [
    ("I", "Alphabet"),
    ("II", "System of Sounds; Pronunciation"),
    ("III", "Rules of Euphonic Combination"),
    ("IV", "Declension"),
    ("V", "Nouns and Adjectives"),
    ("VI", "Numerals"),
    ("VII", "Pronouns"),
    ("VIII", "Conjugation"),
    ("IX", "The Present-System"),
    ("X", "The Perfect-System"),
    ("XI", "The Aorist-Systems"),
    ("XII", "The Future-Systems"),
    ("XIII", "Verbal Adjectives and Nouns: Participles, Infinitives, Gerunds"),
    ("XIV", "Derivative or Secondary Conjugation"),
    ("XV", "Periphrastic and Compound Conjugation"),
    ("XVI", "Indeclinables"),
    ("XVII", "Derivation of Declinable Stems"),
    ("XVIII", "Formation of Compound Stems"),
]
CHAP_TITLE = {num: title for num, title in CHAPTERS}

# Convenience chapter sets.
# Verb-system chapters are where every form->§ concordance row lives.
VERB_CHAPTERS = ["IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
# Pilot: the two anchor ranges named in the task — perfect (Ch X, §§781-823)
# and PPP (Ch XIII, §§952-958, whose chapter also covers infinitive/gerund).
PILOT_CHAPTERS = ["X", "XIII"]
ALL_CHAPTERS = [num for num, _ in CHAPTERS]

# --------------------------------------------------------------------------- #
# Parsing regexes
# --------------------------------------------------------------------------- #
# Top-level numbered section marker, e.g.:
#   <span id="781" title="Anchor:781" ... class="wst-anchor">781.</span>
# id must be a *pure integer* (letter sub-sections like id="781a" are excluded).
SECTION_SPAN_RE = re.compile(
    r'<span\s+id="(\d+)"[^>]*class="wst-anchor"[^>]*>\s*\d+\s*\.?\s*</span>'
)
# Any wst-anchor span (used to strip the leftover marker text from a body).
ANY_ANCHOR_SPAN_RE = re.compile(r'<span\s+id="[^"]*"[^>]*class="wst-anchor"[^>]*>.*?</span>')

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t ]+")
MULTINL_RE = re.compile(r"\n{3,}")
# Wikisource editorial cruft to drop from the plain text.
EDITNOTE_RE = re.compile(r"\[\s*edit\s*\]", re.IGNORECASE)
REF_SUP_RE = re.compile(r"\[\d+\]")  # footnote markers like [1]


def log(msg):
    print(msg, flush=True)


def chapter_page_path(num):
    """Wiki page title for a chapter, e.g. 'Sanskrit_Grammar_(Whitney)/Chapter_X'."""
    return f"{WORK_PREFIX}/Chapter_{num}"


def chapter_url(num):
    """Human-facing base URL for a chapter (section fragment appended later)."""
    return f"{PAGE_BASE}/Chapter_{num}"


def cache_path(num):
    return os.path.join(CACHE_DIR, f"Chapter_{num}.html")


def fetch_chapter_html(num, refresh=False):
    """
    Return the rendered HTML body of a chapter page.
    Uses scratch/wikisource cache unless refresh=True. Live fetch goes through
    the MediaWiki action=parse API and is rate-limited + UA-identified.
    """
    cp = cache_path(num)
    if not refresh and os.path.exists(cp) and os.path.getsize(cp) > 0:
        with open(cp, "r", encoding="utf-8") as fh:
            log(f"  [cache] Chapter_{num} ({os.path.getsize(cp)} bytes)")
            return fh.read()

    params = {
        "action": "parse",
        "page": chapter_page_path(num),
        "prop": "text",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    log(f"  [fetch] {chapter_page_path(num)}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching Chapter_{num}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching Chapter_{num}: {e.reason}") from e

    data = json.loads(raw)
    if "error" in data:
        raise RuntimeError(f"API error for Chapter_{num}: {data['error']}")
    html = data["parse"]["text"]
    # formatversion=2 gives text as a string; guard for the older {'*': ...} shape.
    if isinstance(html, dict):
        html = html.get("*", "")

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cp, "w", encoding="utf-8") as fh:  # UTF-8, no BOM
        fh.write(html)
    time.sleep(POLITE_DELAY_S)
    return html


def html_to_text(fragment):
    """Convert an HTML fragment to readable plain text (UTF-8, IAST preserved)."""
    s = fragment
    # Remove <style>/<script> ELEMENTS entirely (content included). Wikisource
    # inlines TemplateStyles <style> blocks mid-text (e.g. ".mw-parser-output
    # .wst-mono{...}"); stripping only the tags would leave raw CSS in the body.
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.DOTALL | re.IGNORECASE)
    # Drop leftover wst-anchor marker spans (e.g. sub-section "781a." labels)
    # but KEEP their following text. We only remove the span tags, not content.
    s = re.sub(r'<span\s+id="[^"]*"[^>]*class="wst-anchor"[^>]*>(.*?)</span>',
               r" \1 ", s, flags=re.DOTALL)
    # Paragraph / break boundaries -> newlines so sentences don't fuse.
    s = re.sub(r"</p\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</li\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</tr\s*>", "\n", s, flags=re.IGNORECASE)
    # Strip all remaining tags.
    s = TAG_RE.sub("", s)
    # Unescape entities (&amp; &nbsp; numeric IAST entities, etc.).
    s = unescape(s)
    # Editorial cruft.
    s = EDITNOTE_RE.sub("", s)
    s = REF_SUP_RE.sub("", s)
    # Whitespace normalisation.
    s = s.replace("\r", "")
    s = WS_RE.sub(" ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = MULTINL_RE.sub("\n\n", s)
    return s.strip()


def parse_sections(html, num):
    """
    Slice a chapter's HTML into per-section records using the numbered
    wst-anchor spans as boundaries. Returns a list of dicts.
    """
    markers = list(SECTION_SPAN_RE.finditer(html))
    if not markers:
        log(f"  [warn] Chapter_{num}: no numbered section anchors found")
        return []

    records = []
    base = chapter_url(num)
    title = CHAP_TITLE.get(num)
    for i, m in enumerate(markers):
        sec = int(m.group(1))
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(html)
        body_html = html[start:end]
        text = html_to_text(body_html)
        records.append({
            "section_number": sec,
            "chapter": num,
            "chapter_title": title,
            "title": None,  # Whitney's sections are untitled paragraphs
            "text": text,
            "wikisource_url": f"{base}#{sec}",
            "char_len": len(text),
        })
    return records


def resolve_chapter_list(args):
    if args.chapters:
        wanted = [c.strip() for c in args.chapters.split(",") if c.strip()]
        bad = [c for c in wanted if c not in CHAP_TITLE]
        if bad:
            raise SystemExit(f"Unknown chapter(s): {bad}. Valid: {ALL_CHAPTERS}")
        return wanted, "explicit:" + ",".join(wanted)
    if args.all:
        return ALL_CHAPTERS, "all (I-XVIII)"
    if args.full:
        return VERB_CHAPTERS, "full verb-systems (IX-XV)"
    return PILOT_CHAPTERS, "pilot (X + XIII)"


def main():
    ap = argparse.ArgumentParser(description="Fetch Whitney's Sanskrit Grammar §§ from Wikisource.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pilot", action="store_true",
                   help="Fetch pilot chapters X + XIII (default).")
    g.add_argument("--full", action="store_true",
                   help="Fetch all verb-system chapters IX-XV (every concordance row).")
    g.add_argument("--all", action="store_true",
                   help="Fetch every chapter I-XVIII (whole grammar §§1-1340).")
    ap.add_argument("--chapters", default=None,
                    help="Comma-separated Roman numerals, e.g. X,XIII,XI.")
    ap.add_argument("--refresh", action="store_true",
                    help="Ignore the scratch/wikisource HTML cache and re-download.")
    args = ap.parse_args()

    chapters, mode_desc = resolve_chapter_list(args)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    log(f"Whitney Grammar Wikisource ingest — mode: {mode_desc}")
    log(f"Cache dir : {CACHE_DIR}")
    log(f"Output    : {OUT_PATH}")
    log("")

    all_sections = []
    fetched_chaps = []
    for num in chapters:
        log(f"Chapter {num} — {CHAP_TITLE.get(num, '?')}")
        try:
            html = fetch_chapter_html(num, refresh=args.refresh)
        except RuntimeError as e:
            log(f"  [error] {e}")
            continue
        recs = parse_sections(html, num)
        if recs:
            lo = recs[0]["section_number"]
            hi = recs[-1]["section_number"]
            log(f"  -> {len(recs)} sections, §§{lo}-{hi}")
            fetched_chaps.append({"chapter": num, "title": CHAP_TITLE.get(num),
                                  "n_sections": len(recs), "first": lo, "last": hi})
        all_sections.extend(recs)

    # Deterministic ordering by section number.
    all_sections.sort(key=lambda r: r["section_number"])

    # What did we defer? (relative to the full §§1-1340 grammar)
    fetched_nums = {n for n, _ in CHAPTERS if n in chapters}
    deferred_chaps = [
        {"chapter": n, "title": t}
        for n, t in CHAPTERS if n not in fetched_nums
    ]

    sec_lo = all_sections[0]["section_number"] if all_sections else None
    sec_hi = all_sections[-1]["section_number"] if all_sections else None

    out = {
        "_meta": {
            "work": "Whitney, William Dwight. Sanskrit Grammar, 2nd ed. (1889).",
            "source": "English Wikisource",
            "source_root": PAGE_BASE,
            "source_structure": (
                "One subpage per chapter (Roman numeral); each section is an "
                "HTML anchor span id=\"NNN\" class=\"wst-anchor\"; a section is "
                "addressable as .../Chapter_<RN>#<NNN>."
            ),
            "api": API,
            "license": "Public domain (published before 1931); output CC BY-SA 4.0.",
            "fetch_mode": mode_desc,
            "generated_by": "scripts/wikisource/fetch_whitney.py",
            "section_count": len(all_sections),
            "section_range": [sec_lo, sec_hi],
            "chapters_fetched": fetched_chaps,
            "chapters_deferred": deferred_chaps,
            "note_full_grammar": "Whitney's grammar runs §§1-1340 across chapters I-XVIII.",
        },
        "sections": all_sections,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as fh:  # UTF-8, NO BOM
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    log("")
    log(f"Wrote {len(all_sections)} sections to {OUT_PATH}")
    if all_sections:
        log(f"Section range: §§{sec_lo}-{sec_hi}")
    log(f"Chapters fetched : {[c['chapter'] for c in fetched_chaps]}")
    log(f"Chapters deferred: {[c['chapter'] for c in deferred_chaps]}")


if __name__ == "__main__":
    main()
