#!/usr/bin/env python3
"""Verify a hand-authored annotated HTML PRD.

Hand-authored HTML has no build step, so nothing catches a broken document before
a reader does. This script is that missing pass. It is a linter, not a proof: it
checks **markup hygiene** and **spec-contract conformance**, and it is blind to
whether the content is any good.

What it enforces:

  1. Tag balance          — no unclosed tags, no stray end tags, no crossed nesting.
  2. Triad continuity     — every .mk marker in a mockup has exactly one .nbadge row
                            in its legend table, numbered 1..N ascending, no gaps.
  3. No forbidden form    — no <pre>, no mermaid, no ASCII box-drawing art. These
                            three are the exact failure signature this skill exists
                            to prevent.
  4. Self-contained       — no CDN scripts, remote fonts, remote images, @import, or
                            any other external request. The file must render from a
                            file:// URL on an air-gapped machine.
  5. Language consistency — <html lang> must match the language actually written in
                            the body; a CJK body must keep the CJK font stack.
  6. Marker discipline    — in ol.inter-list, 正常 items carry a numeric .marker and
                            异常 items carry .marker.err with the literal "!".
  7. Structural minimums  — a .toc, a .doc-head, at least one .anno-wrap and one
                            .spec.field, and no duplicate TOC labels. (Warnings;
                            --strict promotes them to failures.)
  8. Stale-marker scan    — document-wide .mk vs .nbadge count reconciliation.
  9. Spec contract        — per .screen: every .spec-label is one of the fixed
                            strings from references/design-system.md §6 (either
                            language); the ①②③④ blocks appear in that order; a
                            ③ block carries a state *picture* (inline <svg> or a
                            .flow chain), not just a table; a ② block is a
                            single-row three-column table; and a .screen is not
                            empty of both .spec blocks and triads. (Warnings;
                            --strict promotes them to failures.)

What it CANNOT enforce — a clean run is necessary, never sufficient:

  * whether the requirements are correct, complete, feasible, or agreed;
  * whether a field list matches the real schema, or a state machine is total;
  * whether the legend text actually describes the element its marker points at;
  * whether an E-R diagram, role matrix, or version section exists and is right.
    Those are content judgements. Check group 9 verifies the *shape* of the spec
    blocks, never their truth. Read references/checklist.md for the rest.

Usage:
    python3 scripts/verify_prd_html.py path/to/prd.html [--strict] [--json]

Exit code 0 means clean. Anything else means the PRD is not done yet. Every check
runs even if an earlier one fails, so one pass tells you everything that is wrong.
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

# Tags whose end tag may be omitted in valid HTML — never reported as unclosed.
OPTIONAL_END = {
    "p", "li", "td", "th", "tr", "tbody", "thead", "tfoot",
    "option", "dt", "dd", "colgroup", "rt", "rp",
}

# start tag -> set of open tags it implicitly closes
AUTO_CLOSE = {
    "li": {"li"},
    "p": {"p"},
    "tr": {"td", "th", "tr"},
    "td": {"td", "th"},
    "th": {"td", "th"},
    "tbody": {"td", "th", "tr", "thead", "tbody"},
    "thead": {"td", "th", "tr"},
    "tfoot": {"td", "th", "tr", "tbody", "thead"},
    "dt": {"dt", "dd"},
    "dd": {"dt", "dd"},
    "option": {"option"},
}

BOX_GLYPHS = "┌┐└┘─│├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"
BOX_RE = re.compile("[" + BOX_GLYPHS + "]")

# Pure-ASCII box art: a line that is nothing but frame characters, e.g.
#   +--------------+   |   +----+----+   |   |    |     |
# Two or more such lines in one text node is a drawn frame, not prose.
ASCII_FRAME_LINE_RE = re.compile(r"^[ \t]*[|+][-=+| \t]*[|+][ \t]*$")

# Mermaid, scoped to constructs that actually render a diagram. A bare mention
# of the word in prose (a changelog row saying a mermaid chart was replaced) is
# legitimate and must not fail the document.
MERMAID_RENDER_RES = (
    (re.compile(r"""class\s*=\s*["'][^"']*\bmermaid\b""", re.I),
     'class="mermaid" — diagrams must be inline SVG or .flow chains'),
    (re.compile(r"""<script[^>]*type\s*=\s*["']text/x-mermaid""", re.I),
     "<script type=text/x-mermaid> — diagrams must be inline SVG or .flow chains"),
    (re.compile(r"\bmermaid\s*\.\s*(?:initialize|render|run)\s*\(", re.I),
     "mermaid API call — diagrams must be inline SVG or .flow chains"),
    (re.compile(r"```\s*mermaid", re.I),
     "```mermaid fence — diagrams must be inline SVG or .flow chains"),
)
MERMAID_WORD_RE = re.compile(r"\bmermaid\b", re.I)

CJK_RE = re.compile(r"[一-鿿㐀-䶿]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]+")
# Compare like with like: one *word* against one *word*. Counting CJK
# characters against Latin words inflates the CJK share ~5x (an English word
# averages ~5 characters) and fails an English PRD that quotes CJK UI strings.
# Counting characters against characters over-corrects the other way: a
# correct zh-CN PRD keeps product, metric and entity names in English, so the
# reference document is only 40% CJK by raw character count. A Chinese word
# averages ~2 characters, so halving the CJK character count approximates its
# word count and puts both sides on the same scale.
CJK_CHARS_PER_WORD = 2.0
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

CJK_FONTS = ("PingFang SC", "Hiragino Sans GB", "Microsoft YaHei")

CHECK_TITLES = {
    1: "Tag balance",
    2: "Triad continuity (.mk <-> .nbadge)",
    3: "Forbidden constructs (<pre> / mermaid / box art)",
    4: "Self-contained (no external requests)",
    5: "Language consistency (<html lang> vs body)",
    6: "Interaction marker discipline",
    7: "Structural minimums",
    8: "Stale-marker scan",
    9: "Spec-contract conformance (.screen / .spec)",
}

# --- Spec dimensions -------------------------------------------------------- #

# The fixed child order of .screen-body: ① -> ② -> ③ -> ④ (design-system.md §3).
DIM_ORDER = ("field", "cond", "state", "inter")
DIM_SET = set(DIM_ORDER)
DIM_RANK = {d: i for i, d in enumerate(DIM_ORDER)}
DIM_NUM = {"field": "①", "cond": "②", "state": "③", "inter": "④"}

# Fallback copy of references/design-system.md §6 "The four spec labels", byte
# for byte. The loader below prefers the real file; this exists only so the
# script still runs when copied away from the skill tree. If §6 ever changes,
# §6 wins — it is the single source of truth and this must be re-synced.
FIXED_SPEC_LABELS_FALLBACK = {
    "field": {
        "① 字段、字段说明、数据来源",
        "① Fields, description, data source",
    },
    "cond": {
        "② 前置条件、排序机制、刷新机制",
        "② Preconditions, sorting, refresh",
    },
    "state": {
        "③ 状态流转",
        "③ State transitions",
    },
    "inter": {
        # Full form plus the two sanctioned short forms, both languages.
        "④ 交互操作（正常 + 异常）",
        "④ Interactions (normal + abnormal)",
        "④ 交互",
        "④ Interactions",
        "④ 交互 / 状态",
        "④ Interactions / states",
    },
}

DESIGN_SYSTEM_MD = (
    Path(__file__).resolve().parent.parent / "references" / "design-system.md")

# `① …` / `② …` spans quoted in backticks inside §6, before the legend-header
# subsection. Covers both the four-row table and the sanctioned short forms.
_S6_LABEL_RE = re.compile(r"`([①②③④][^`\n]*)`")
_NUM_TO_DIM = {DIM_NUM[d]: d for d in DIM_ORDER}


def load_fixed_spec_labels(path=DESIGN_SYSTEM_MD):
    """Read the fixed spec-label strings from design-system.md §6.

    §6 is the single source of truth. Parsing it beats restating it: the strings
    cannot drift out of sync with the document that defines them. Falls back to
    the embedded copy if the reference file is absent or unparseable.
    """
    try:
        text = path.read_text(encoding="utf-8")
        body = text.split("## 6. Fixed strings", 1)[1]
        body = body.split("### Legend table headers", 1)[0]
    except (OSError, IndexError):
        return {d: set(v) for d, v in FIXED_SPEC_LABELS_FALLBACK.items()}

    found = {d: set() for d in DIM_ORDER}
    for raw in _S6_LABEL_RE.findall(body):
        dim = _NUM_TO_DIM.get(raw[0])
        if dim:
            found[dim].add(raw.strip())
    if all(found[d] for d in DIM_ORDER):
        return found
    return {d: set(v) for d, v in FIXED_SPEC_LABELS_FALLBACK.items()}


def classes(attrs):
    """Return the class-token set of an attrs list."""
    for name, value in attrs:
        if name == "class" and value:
            return set(value.split())
    return set()


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #

class PRDParser(HTMLParser):
    """Single pass: tag balance, triads, interaction lists, visible text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []                 # list of frame dicts
        self.balance_errors = []        # (line, message)

        self.anno_wraps = []            # finalised triad records
        self.anno_stack = []            # open .anno-wrap records

        self.inter_items = []           # finalised ol.inter-list <li> records
        self.li_stack = []              # open <li> records inside an inter-list
        self.inter_depth = 0

        self.visible = []               # visible text fragments
        self.styles = []                # contents of <style> blocks
        self.suppress_text = 0          # inside <script>/<style>

        self.toc_labels = []            # (line, label) of .toc anchors
        self.seen = {                   # structural presence flags
            "toc": False, "doc-head": False, "spec-field": False,
        }
        self.mk_total = 0
        self.nbadge_total = 0
        self.nbadge_outside = []        # (line, value) legend rows with no triad

        self.screens = []               # finalised .screen records
        self.screen_stack = []          # open .screen records
        self.specs = []                 # every .spec record, screened or not
        self.spec_stack = []            # open .spec records

    # -- helpers ----------------------------------------------------------- #

    def _push(self, tag, line, cls):
        self.stack.append({"tag": tag, "line": line, "cls": cls,
                           "capture": None, "text": [],
                           "li_record": None, "marker_record": None,
                           "screen_record": None, "spec_record": None})

    def _note_spec_descendant(self, tag, cls, attrs):
        """Record structure of interest inside the innermost open .spec."""
        spec = self.spec_stack[-1]
        if tag == "svg":
            spec["svg"] = True
        if "flow" in cls:
            spec["flow"] = True

        if tag == "table":
            if not spec["tbl_done"] and spec["tbl_depth"] == 0:
                spec["tbl_open"] = True
            spec["tbl_depth"] += 1
        elif spec["tbl_open"]:
            if tag == "tr":
                spec["rows"].append(0)
            elif tag in ("td", "th"):
                span = 1
                for name, value in attrs:
                    if name == "colspan":
                        try:
                            span = max(1, int((value or "1").strip()))
                        except ValueError:
                            span = 1
                if not spec["rows"]:
                    spec["rows"].append(0)
                spec["rows"][-1] += span

    def _pop(self):
        frame = self.stack.pop()
        if frame["capture"]:
            self._emit(frame)
        return frame

    def _emit(self, frame):
        kind = frame["capture"]
        text = "".join(frame["text"]).strip()
        line = frame["line"]
        if kind == "mk":
            self.mk_total += 1
            if self.anno_stack:
                self.anno_stack[-1]["mks"].append((line, text))
            else:
                self.anno_wraps.append({
                    "line": line, "title": "(marker outside any .anno-wrap)",
                    "orphan": True, "mks": [(line, text)], "nbadges": [],
                })
        elif kind == "nbadge":
            self.nbadge_total += 1
            if self.anno_stack:
                self.anno_stack[-1]["nbadges"].append((line, text))
            else:
                self.nbadge_outside.append((line, text))
        elif kind == "anno-title" and self.anno_stack:
            self.anno_stack[-1]["title"] = text[:70]
        elif kind == "toc-link":
            self.toc_labels.append((line, text))
        elif kind == "spec-label" and self.spec_stack:
            # The label is a child of its .spec, so the spec is still open here.
            self.spec_stack[-1]["label"] = text
        elif kind == "screen-title" and self.screen_stack:
            self.screen_stack[-1]["title"] = text[:60]

    def _current_capture_targets(self):
        return [f for f in self.stack if f["capture"]]

    # -- HTMLParser hooks --------------------------------------------------- #

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        cls = classes(attrs)

        closable = AUTO_CLOSE.get(tag)
        if closable:
            while self.stack and self.stack[-1]["tag"] in closable:
                frame = self.stack[-1]
                self._finish(frame)
                self._pop()

        if tag in ("script", "style"):
            self.suppress_text += 1

        # structural / capture bookkeeping (before the void-tag early exit,
        # since none of these are void elements in practice)
        if "toc" in cls:
            self.seen["toc"] = True
        if "doc-head" in cls:
            self.seen["doc-head"] = True
        if "spec" in cls and "field" in cls:
            self.seen["spec-field"] = True

        if "anno-wrap" in cls:
            self.anno_stack.append({
                "line": line, "title": "", "orphan": False,
                "mks": [], "nbadges": [],
            })
            if self.screen_stack:
                self.screen_stack[-1]["annos"] += 1

        if tag == "ol" and "inter-list" in cls:
            self.inter_depth += 1

        if tag in VOID:
            return

        self._push(tag, line, cls)
        frame = self.stack[-1]

        # -- spec-contract bookkeeping -------------------------------------- #
        # Record what the *enclosing* spec contains before opening a new one,
        # so a .spec never counts itself as its own descendant.
        if self.spec_stack:
            self._note_spec_descendant(tag, cls, attrs)

        if "screen" in cls:
            record = {"line": line, "title": "", "annos": 0, "specs": []}
            self.screen_stack.append(record)
            frame["screen_record"] = record

        spec_dims = cls & DIM_SET
        if "spec" in cls and spec_dims:
            record = {
                "line": line,
                # A block written class="spec field cond" is malformed; report
                # every dimension it claims rather than silently picking one.
                "dims": sorted(spec_dims, key=lambda d: DIM_RANK[d]),
                "label": None,
                "svg": False, "flow": False,
                "rows": [],          # cell count per <tr> of the first table
                "tbl_depth": 0, "tbl_open": False, "tbl_done": False,
            }
            self.spec_stack.append(record)
            self.specs.append(record)
            frame["spec_record"] = record
            if self.screen_stack:
                self.screen_stack[-1]["specs"].append(record)

        if "mk" in cls:
            frame["capture"] = "mk"
        elif "nbadge" in cls:
            frame["capture"] = "nbadge"
        elif "anno-title" in cls:
            frame["capture"] = "anno-title"
        elif "spec-label" in cls:
            frame["capture"] = "spec-label"
        elif "screen-title" in cls:
            frame["capture"] = "screen-title"
        elif tag == "a" and any(f["cls"] & {"toc"} for f in self.stack[:-1]):
            frame["capture"] = "toc-link"

        if self.inter_depth and tag == "li":
            record = {"line": line, "markers": [], "tags": []}
            self.li_stack.append(record)
            self.inter_items.append(record)
            frame["li_record"] = record

        if self.li_stack:
            if "marker" in cls:
                marker = {"line": line, "err": "err" in cls, "text": ""}
                self.li_stack[-1]["markers"].append(marker)
                frame["marker_record"] = marker
                frame["capture"] = "marker-text"
            elif "tag" in cls and ("err" in cls or "normal" in cls):
                self.li_stack[-1]["tags"].append(
                    {"line": line, "err": "err" in cls})

    def handle_endtag(self, tag):
        line = self.getpos()[0]

        if tag in ("script", "style"):
            self.suppress_text = max(0, self.suppress_text - 1)

        if tag in VOID:
            return

        names = [f["tag"] for f in self.stack]
        if tag not in names:
            self.balance_errors.append(
                (line, "stray end tag </%s> with no matching open tag" % tag))
            return

        while self.stack:
            frame = self.stack[-1]
            if frame["tag"] == tag:
                self._finish(frame)
                self._pop()
                break
            if frame["tag"] not in OPTIONAL_END:
                self.balance_errors.append(
                    (frame["line"],
                     "<%s> opened here is never closed — </%s> at line %d "
                     "closes over it" % (frame["tag"], tag, line)))
            self._finish(frame)
            self._pop()

    def _finish(self, frame):
        """Close out non-capture bookkeeping for a frame about to be popped."""
        if "anno-wrap" in frame["cls"] and self.anno_stack:
            self.anno_wraps.append(self.anno_stack.pop())
        if frame["tag"] == "ol" and "inter-list" in frame["cls"]:
            self.inter_depth = max(0, self.inter_depth - 1)
        if frame["li_record"] is not None and self.li_stack:
            if self.li_stack[-1] is frame["li_record"]:
                self.li_stack.pop()
        if frame["marker_record"] is not None:
            frame["marker_record"]["text"] = "".join(frame["text"]).strip()
            frame["capture"] = None

        # A </table> closes the row tally of the spec it sits in; the spec frame
        # is still open at this point, so spec_stack[-1] is the right target.
        if frame["tag"] == "table" and self.spec_stack:
            spec = self.spec_stack[-1]
            if spec["tbl_depth"] > 0:
                spec["tbl_depth"] -= 1
                if spec["tbl_depth"] == 0 and spec["tbl_open"]:
                    spec["tbl_open"] = False
                    spec["tbl_done"] = True

        if frame["spec_record"] is not None and self.spec_stack:
            if self.spec_stack[-1] is frame["spec_record"]:
                self.spec_stack.pop()
        if frame["screen_record"] is not None and self.screen_stack:
            if self.screen_stack[-1] is frame["screen_record"]:
                self.screens.append(self.screen_stack.pop())

    def handle_data(self, data):
        if self.suppress_text:
            self.styles.append(data)
            return
        self.visible.append(data)
        for frame in self.stack:
            if frame["capture"]:
                frame["text"].append(data)

    def close(self):
        super().close()
        while self.stack:
            frame = self.stack[-1]
            if frame["tag"] not in OPTIONAL_END:
                self.balance_errors.append(
                    (frame["line"],
                     "<%s> opened here is never closed (EOF)" % frame["tag"]))
            self._finish(frame)
            self._pop()
        while self.anno_stack:
            self.anno_wraps.append(self.anno_stack.pop())
        while self.screen_stack:
            self.screens.append(self.screen_stack.pop())
        self.spec_stack.clear()


# --------------------------------------------------------------------------- #
# Report accumulator
# --------------------------------------------------------------------------- #

class Report:
    def __init__(self, path, strict):
        self.path = path
        self.strict = strict
        self.errors = {}     # check id -> [(line, msg)]
        self.warnings = {}   # check id -> [(line, msg)]
        self.notes = []

    def error(self, check, line, msg):
        self.errors.setdefault(check, []).append((line, msg))

    def warn(self, check, line, msg):
        bucket = self.errors if self.strict else self.warnings
        bucket.setdefault(check, []).append((line, msg))

    @property
    def n_errors(self):
        return sum(len(v) for v in self.errors.values())

    @property
    def n_warnings(self):
        return sum(len(v) for v in self.warnings.values())

    @property
    def ok(self):
        return self.n_errors == 0

    def render(self):
        out = []
        for cid in sorted(CHECK_TITLES):
            errs = self.errors.get(cid, [])
            warns = self.warnings.get(cid, [])
            if errs:
                status = "FAIL (%d)" % len(errs)
            elif warns:
                status = "WARN (%d)" % len(warns)
            else:
                status = "pass"
            title = "[%d] %s" % (cid, CHECK_TITLES[cid])
            out.append("%-52s %s" % (title, status))
            for line, msg in errs:
                out.append("      %s:%d  %s" % (self.path.name, line, msg))
            for line, msg in warns:
                out.append("      %s:%d  warn: %s" % (self.path.name, line, msg))
        for note in self.notes:
            out.append("      note: %s" % note)
        out.append("-" * 66)
        out.append("%s — %d error(s), %d warning(s) in %s"
                   % ("PASS" if self.ok else "FAIL",
                      self.n_errors, self.n_warnings, self.path))
        if not self.ok:
            out.append("A PRD is not done until this exits clean.")
        return "\n".join(out)

    def to_json(self):
        return {
            "file": str(self.path),
            "pass": self.ok,
            "errors": self.n_errors,
            "warnings": self.n_warnings,
            "checks": {
                str(cid): {
                    "title": CHECK_TITLES[cid],
                    "errors": [{"line": l, "message": m}
                               for l, m in self.errors.get(cid, [])],
                    "warnings": [{"line": l, "message": m}
                                 for l, m in self.warnings.get(cid, [])],
                }
                for cid in sorted(CHECK_TITLES)
            },
            "notes": self.notes,
        }


def line_of(src, index):
    return src.count("\n", 0, index) + 1


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_balance(rep, parser):
    for line, msg in parser.balance_errors:
        rep.error(1, line, msg)


def check_triads(rep, parser):
    for wrap in sorted(parser.anno_wraps, key=lambda w: w["line"]):
        label = wrap["title"] or ".anno-wrap"
        if wrap.get("orphan"):
            rep.error(2, wrap["line"],
                      "%s: .mk marker '%s' is not inside any .anno-wrap"
                      % (label, wrap["mks"][0][1]))
            continue

        mks, nbs = wrap["mks"], wrap["nbadges"]
        mk_vals = [t for _, t in mks]
        nb_vals = [t for _, t in nbs]

        for line, val in mks:
            if val not in nb_vals:
                rep.error(2, line, "%s: .mk '%s' has no matching .nbadge row"
                          % (label, val))
        for line, val in nbs:
            if val not in mk_vals:
                rep.error(2, line, "%s: .nbadge '%s' has no matching .mk in the "
                          "mockup" % (label, val))

        for name, vals, items in (("mk", mk_vals, mks), ("nbadge", nb_vals, nbs)):
            seen = {}
            for line, val in items:
                if val in seen:
                    rep.error(2, line, "%s: duplicate .%s '%s' (first at line %d)"
                              % (label, name, val, seen[val]))
                else:
                    seen[val] = line

        nums = []
        for line, val in mks:
            if val.isdigit():
                nums.append(int(val))
            else:
                # Continuity still holds if it has a matching .nbadge; the gold
                # standard uses plain 1..N, so flag the deviation without
                # failing a document whose markers do pair up.
                rep.warn(2, line, "%s: .mk '%s' is not a plain Arabic numeral — "
                         "the marker system is 1..N; circled glyphs are reserved "
                         "for the four spec dimensions" % (label, val))
        if nums:
            expected = list(range(1, len(nums) + 1))
            if sorted(nums) != expected:
                missing = [n for n in expected if n not in nums]
                extra = [n for n in sorted(set(nums)) if n > len(nums)]
                detail = []
                if missing:
                    detail.append("missing %s" % ", ".join(map(str, missing)))
                if extra:
                    detail.append("out of range %s" % ", ".join(map(str, extra)))
                rep.error(2, wrap["line"],
                          "%s: marker sequence is not 1..%d ascending with no "
                          "gaps (%s)" % (label, len(nums),
                                         "; ".join(detail) or "reordered"))


def _mask_comments(src):
    """Blank out HTML comments, preserving offsets and line numbers.

    A comment is authoring scaffolding, not rendered output, so a hint that
    literally says "no <pre> blocks" must not fail the document it is
    explaining.
    """
    def blank(m):
        return "".join("\n" if ch == "\n" else " " for ch in m.group(0))
    return COMMENT_RE.sub(blank, src)


def check_forbidden(rep, src):
    code = _mask_comments(src)

    for m in re.finditer(r"<pre\b", code, re.I):
        rep.error(3, line_of(code, m.start()),
                  "<pre> block — mockups and diagrams must be CSS/SVG, never "
                  "preformatted text")

    # Only fail on constructs that actually render a mermaid diagram. Prose may
    # name mermaid freely — a changelog row recording that a mermaid chart was
    # replaced by inline SVG is a true statement about a compliant document.
    mermaid_hit = False
    for pattern, msg in MERMAID_RENDER_RES:
        for m in pattern.finditer(code):
            mermaid_hit = True
            rep.error(3, line_of(code, m.start()), msg)
    if not mermaid_hit:
        for m in MERMAID_WORD_RE.finditer(code):
            rep.warn(3, line_of(code, m.start()),
                     "the word 'mermaid' appears in the text — fine if this is "
                     "prose about mermaid, a defect if a diagram was meant")

    hits = {}
    for m in BOX_RE.finditer(code):
        hits.setdefault(line_of(code, m.start()), 0)
        hits[line_of(code, m.start())] += 1
    for line in sorted(hits):
        rep.error(3, line, "%d Unicode box-drawing glyph(s) — draw the screen "
                  "with .mock primitives instead" % hits[line])

    # Pure-ASCII box art (+---+ / |   |) draws the same picture out of
    # characters the glyph scan above does not know about, and is exactly what
    # a model falls back to when told "no Unicode box characters".
    # Frame lines alternate with content lines ("+---+" / "| Views |" /
    # "+---+"), so count them across the document rather than looking for a
    # consecutive run.
    frame_lines = []
    for i, raw in enumerate(code.split("\n"), 1):
        stripped = re.sub(r"<[^>]*>", "", raw).rstrip()
        if len(stripped.strip()) >= 8 and ASCII_FRAME_LINE_RE.match(stripped):
            frame_lines.append(i)
    if len(frame_lines) >= 2:
        rep.error(3, frame_lines[0],
                  "%d lines of ASCII box art (lines %s) — draw the screen with "
                  ".mock primitives instead"
                  % (len(frame_lines),
                     ", ".join(map(str, frame_lines[:6]))
                     + ("…" if len(frame_lines) > 6 else "")))

    # ASCII art survives without a <pre> tag by being given `white-space: pre`.
    for m in re.finditer(r"white-space\s*:\s*pre(-wrap)?\b", code, re.I):
        rep.error(3, line_of(code, m.start()),
                  "white-space:pre — preformatted text is how ASCII art gets in "
                  "without a <pre> tag; use .mock primitives instead")


def check_self_contained(rep, src):
    for m in re.finditer(r"""\b(src|href)\s*=\s*["']([^"']*)["']""", src, re.I):
        url = m.group(2).strip()
        low = url.lower()
        if low.startswith("#") or low.startswith("mailto:") or low.startswith("data:"):
            continue
        if low.startswith("http://") or low.startswith("https://") or low.startswith("//"):
            rep.error(4, line_of(src, m.start()),
                      "external %s=\"%s\" — the file must render offline from "
                      "file://" % (m.group(1), url[:70]))
    for m in re.finditer(r"@import", src, re.I):
        rep.error(4, line_of(src, m.start()), "@import in CSS — inline the styles")
    for m in re.finditer(r"""url\(\s*["']?(https?:)?//""", src, re.I):
        rep.error(4, line_of(src, m.start()),
                  "url() pointing at a remote asset — embed it or drop it")
    for m in re.finditer(r"<script[^>]*\bsrc\s*=", src, re.I):
        rep.error(4, line_of(src, m.start()),
                  "<script src> — the only JS allowed is the inline scroll-spy")
    for m in re.finditer(r"""<link[^>]*rel\s*=\s*["']?stylesheet""", src, re.I):
        rep.error(4, line_of(src, m.start()),
                  "<link rel=stylesheet> — all CSS must be inline in <style>")
    # ES-module imports and fetches never appear in a src= attribute, so they
    # slip past the checks above. This is how Mermaid gets in via CDN.
    remote_js = (
        (r"""\bfrom\s*["'](?:https?:)?//""", "ES-module import from a remote URL"),
        (r"""\bimport\s*\(\s*["'](?:https?:)?//""", "dynamic import() of a remote URL"),
        (r"""\bfetch\s*\(\s*["'](?:https?:)?//""", "fetch() of a remote URL"),
    )
    for pattern, label in remote_js:
        for m in re.finditer(pattern, src, re.I):
            rep.error(4, line_of(src, m.start()),
                      "%s — the page must render with the network off" % label)


def check_language(rep, parser, src):
    text = "".join(parser.visible)
    cjk_chars = len(CJK_RE.findall(text))
    latin_words = len(LATIN_WORD_RE.findall(text))
    cjk_words = cjk_chars / CJK_CHARS_PER_WORD
    total = cjk_words + latin_words
    ratio = (cjk_words / total) if total else 0.0
    cjk_dominant = ratio >= 0.5
    rep.notes.append("body script: %s (~%d CJK words from %d chars vs %d Latin "
                     "words, CJK share %.0f%%)"
                     % ("CJK" if cjk_dominant else "Latin", cjk_words,
                        cjk_chars, latin_words, ratio * 100))

    m = re.search(r"<html[^>]*\blang\s*=\s*[\"']([^\"']+)[\"']", src, re.I)
    if not m:
        rep.error(5, 1, "<html> has no lang attribute — set it to the language "
                        "actually written in the body")
        return
    lang = m.group(1).strip().lower()
    line = line_of(src, m.start())
    is_cjk_lang = lang.startswith(("zh", "ja", "ko"))

    if is_cjk_lang and not cjk_dominant:
        rep.error(5, line, "lang=\"%s\" but the body is predominantly Latin "
                  "(CJK share %.0f%%)" % (lang, ratio * 100))
    elif not is_cjk_lang and cjk_dominant:
        rep.error(5, line, "lang=\"%s\" but the body is predominantly CJK "
                  "(CJK share %.0f%%) — set lang to match what you wrote"
                  % (lang, ratio * 100))

    if cjk_dominant:
        css = "".join(parser.styles)
        missing = [f for f in CJK_FONTS if f not in css]
        if missing:
            rep.warn(5, line, "CJK body but the font stack is missing %s — "
                     "Chinese will fall back to a system default"
                     % ", ".join('"%s"' % f for f in missing))


def check_markers(rep, parser):
    for item in parser.inter_items:
        markers = item["markers"]
        tags = item["tags"]
        line = item["line"]
        if not markers:
            if tags:
                rep.error(6, line, "ol.inter-list item has a .tag but no .marker")
            continue
        is_err = any(t["err"] for t in tags)
        for m in markers:
            text = m["text"]
            if is_err:
                if not m["err"]:
                    rep.error(6, m["line"], "异常 item uses a plain .marker — "
                              "every error path takes .marker.err")
                if text != "!":
                    rep.error(6, m["line"], "异常 item marker reads '%s'; it must "
                              "be the literal '!', never a number" % text)
            else:
                if m["err"]:
                    rep.error(6, m["line"], "正常 item uses .marker.err — the red "
                              "'!' marker is reserved for 异常 items")
                elif not text.isdigit():
                    rep.error(6, m["line"], "正常 item marker reads '%s'; it must "
                              "be an Arabic numeral" % text)


def check_structure(rep, parser):
    if not parser.seen["toc"]:
        rep.warn(7, 1, "no .toc sidebar")
    if not parser.seen["doc-head"]:
        rep.warn(7, 1, "no .doc-head metadata card")
    if not parser.seen["spec-field"]:
        rep.warn(7, 1, "no .spec.field block — every page needs at least "
                       "dimension ① 字段、字段说明、数据来源")
    real = [w for w in parser.anno_wraps if not w.get("orphan")]
    if not real:
        rep.warn(7, 1, "no .anno-wrap triad — every page with a UI needs a "
                       "mockup + numbered markers + legend table")
    seen = {}
    for line, label in parser.toc_labels:
        key = label.strip()
        if not key:
            continue
        if key in seen:
            rep.warn(7, line, "duplicate TOC label %r (first at line %d) — TOC "
                     "labels must be readable on their own" % (key, seen[key]))
        else:
            seen[key] = line


def _spec_name(spec):
    dims = spec["dims"]
    return "%s .spec.%s" % ("".join(DIM_NUM[d] for d in dims), "/".join(dims))


def check_spec_contract(rep, parser, fixed_labels):
    """Check group 9 — the shape of the four spec dimensions.

    Calibrated against the gold standard, which is what these rules describe.
    Everything here is a warning: the skill allows omitting a dimension that has
    nothing to say, and a screen may legitimately be a pure triad. --strict
    promotes the lot.
    """
    all_known = set()
    for values in fixed_labels.values():
        all_known |= values

    for screen in sorted(parser.screens, key=lambda s: s["line"]):
        label = screen["title"] or "screen"
        specs = screen["specs"]

        # (4) An empty page block. The gold has a screen whose entire content is
        # a triad (its legend table carries the spec), so a triad counts.
        if not specs and not screen["annos"]:
            rep.warn(9, screen["line"],
                     "%s: .screen has no .spec block and no .anno-wrap triad — a "
                     "page block must specify something" % label)

        # (3) ① -> ② -> ③ -> ④, never reordered.
        prev_rank, prev_dim = -1, None
        for spec in specs:
            rank = min(DIM_RANK[d] for d in spec["dims"])
            if rank < prev_rank:
                rep.warn(9, spec["line"],
                         "%s: %s follows %s — the four dimensions are fixed in "
                         "the order ①→②→③→④" % (label, DIM_NUM[spec["dims"][0]],
                                                 DIM_NUM[prev_dim]))
            else:
                prev_rank, prev_dim = rank, spec["dims"][0]

    for spec in sorted(parser.specs, key=lambda s: s["line"]):
        name = _spec_name(spec)

        if len(spec["dims"]) > 1:
            rep.warn(9, spec["line"],
                     "%s: one .spec claims %d dimensions — each block is exactly "
                     "one of field/cond/state/inter" % (name, len(spec["dims"])))

        # (2) The fixed label strings.
        text = (spec["label"] or "").strip()
        expected = set()
        for dim in spec["dims"]:
            expected |= fixed_labels.get(dim, set())
        if not text:
            rep.warn(9, spec["line"],
                     "%s: no .spec-label — the fixed pill label is the first "
                     "child of every .spec (one of: %s)"
                     % (name, " | ".join(sorted(expected))))
        elif text not in expected:
            hint = ("it is the label of another dimension"
                    if text in all_known else "not a fixed string")
            rep.warn(9, spec["line"],
                     "%s: .spec-label reads %r — %s; design-system.md §6 fixes it "
                     "to one of: %s" % (name, text, hint,
                                        " | ".join(sorted(expected))))

        # (1) ③ needs a picture, not only a table. The gold draws state either as
        # an inline <svg> or as a .flow chain; both are the contract, a bare
        # table is not.
        if "state" in spec["dims"] and not (spec["svg"] or spec["flow"]):
            rep.warn(9, spec["line"],
                     "%s: no inline <svg> and no .flow chain — ③ must *show* the "
                     "state machine, not only tabulate it "
                     "(function-interaction-spec.md)" % name)

        # (5) ② is one single-row, three-column table.
        if "cond" in spec["dims"]:
            rows = spec["rows"]
            if not rows:
                rep.warn(9, spec["line"],
                         "%s: no table — ② is a single-row 3-column table.data "
                         "(前置条件 / 排序机制 / 刷新机制)" % name)
            else:
                widths = {n for n in rows if n}
                if len(rows) > 2:
                    rep.warn(9, spec["line"],
                             "%s: table has %d rows — ② is a header row plus "
                             "exactly one data row; move anything else into ① or "
                             "③" % (name, len(rows)))
                if widths and widths != {3}:
                    rep.warn(9, spec["line"],
                             "%s: table is %s columns wide — ② is exactly 3 "
                             "(前置条件 / 排序机制 / 刷新机制)"
                             % (name, "/".join(str(w) for w in sorted(widths))))

    rep.notes.append(
        "%d .screen block(s), %d .spec block(s) (%s)"
        % (len(parser.screens), len(parser.specs),
           ", ".join("%s%d" % (DIM_NUM[d],
                               sum(1 for s in parser.specs if d in s["dims"]))
                     for d in DIM_ORDER)))


def check_stale(rep, parser):
    wraps = [w for w in parser.anno_wraps if not w.get("orphan")]
    inside = sum(len(w["nbadges"]) for w in wraps)
    outside = parser.nbadge_outside

    rep.notes.append("%d .mk / %d .nbadge (%d in triads, %d outside) across %d "
                     ".anno-wrap block(s)"
                     % (parser.mk_total, parser.nbadge_total, inside,
                        len(outside), len(wraps)))

    if outside:
        rep.warn(8, outside[0][0],
                 "%d .nbadge row(s) sit outside any .anno-wrap (first here) — a "
                 "legend row with no mockup beside it is never continuity-"
                 "checked; keep the legend table inside its .anno-wrap"
                 % len(outside))
    elif parser.mk_total != parser.nbadge_total:
        rep.error(8, 1, "stale markers: %d .mk vs %d .nbadge document-wide"
                  % (parser.mk_total, parser.nbadge_total))


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def verify(path, strict=False):
    src = path.read_text(encoding="utf-8", errors="replace")
    parser = PRDParser()
    parser.feed(src)
    parser.close()

    rep = Report(path, strict)
    check_balance(rep, parser)
    check_triads(rep, parser)
    check_forbidden(rep, src)
    check_self_contained(rep, src)
    check_language(rep, parser, src)
    check_markers(rep, parser)
    check_structure(rep, parser)
    check_stale(rep, parser)
    check_spec_contract(rep, parser, load_fixed_spec_labels())
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Verify a hand-authored annotated HTML PRD.")
    ap.add_argument("path", type=Path, help="path to the .html PRD")
    ap.add_argument("--strict", action="store_true",
                    help="promote structural warnings to failures")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable results")
    args = ap.parse_args(argv)

    if not args.path.is_file():
        sys.stderr.write("verify_prd_html: no such file: %s\n" % args.path)
        return 2

    rep = verify(args.path, strict=args.strict)
    if args.json:
        print(json.dumps(rep.to_json(), ensure_ascii=False, indent=2))
    else:
        print(rep.render())
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
