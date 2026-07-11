#!/usr/bin/env python3
"""Render a finished PRD Markdown file into ONE polished, self-contained HTML page.

This is the companion renderer for the "prd-writer" skill. A PRD is authored and
version-controlled as Markdown, but stakeholders often want something nicer to read,
share, or print to PDF. This script turns the Markdown into a single self-contained
HTML document with:

  - a sticky table-of-contents sidebar (with scroll-spy active highlighting),
  - a styled document header (title / owner / version / last-updated parsed from the top),
  - GitHub-style tables (sticky header, zebra rows, horizontal scroll for wide tables),
  - automatic status badges for common words (Done / In progress / Unused / In use / ...),
  - rendered Mermaid diagrams (E-R, flow, state) via CDN with an offline fallback,
  - blockquote callouts, code styling, heading hover-anchors, and print styling.

Dependency strategy (robustness):
  - It PREFERS `python-markdown` (`pip install markdown`) when importable, for best fidelity.
  - If that is not installed, it FALLS BACK to a built-in, dependency-free converter in
    this file that still handles headings, tables, fenced code, lists, task lists,
    blockquotes, inline formatting, links, and horizontal rules.
  - The script therefore works with ZERO third-party dependencies. It never pip-installs
    anything, and it prints to stderr which conversion path was used.

Usage:
    python3 scripts/prd_to_html.py INPUT.md [-o OUTPUT.html] [--title "Custom Title"]

The default OUTPUT is INPUT with its extension swapped to .html.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys


# --------------------------------------------------------------------------- #
# Mermaid handling
# --------------------------------------------------------------------------- #
# Fenced ```mermaid blocks are extracted BEFORE Markdown conversion (so neither
# converter mangles them) and re-inserted afterwards as <pre class="mermaid">.
# A unique placeholder token stands in for each block in the meantime.
_MERMAID_TOKEN = "\x00MERMAID_BLOCK_{0}\x00"
_MERMAID_RE = re.compile(
    r"^[ \t]*```+[ \t]*mermaid[ \t]*\r?\n(.*?)\r?\n[ \t]*```+[ \t]*$",
    re.DOTALL | re.MULTILINE,
)


def extract_mermaid(text: str):
    """Replace each ```mermaid fenced block with a placeholder token.

    Returns (text_with_tokens, list_of_raw_mermaid_sources).
    """
    blocks = []

    def _sub(match):
        blocks.append(match.group(1))
        return _MERMAID_TOKEN.format(len(blocks) - 1)

    return _MERMAID_RE.sub(_sub, text), blocks


def reinsert_mermaid(html_text: str, blocks) -> str:
    """Swap mermaid placeholder tokens for <pre class="mermaid"> nodes.

    The raw diagram source is preserved verbatim (HTML-escaped) so that, offline,
    the source still shows even when Mermaid cannot render.
    """
    for idx, source in enumerate(blocks):
        token = _MERMAID_TOKEN.format(idx)
        node = '<pre class="mermaid">{0}</pre>'.format(html.escape(source))
        # The token may have been wrapped in <p>...</p> by a converter; strip that.
        html_text = html_text.replace("<p>" + token + "</p>", node)
        html_text = html_text.replace(token, node)
    return html_text


# --------------------------------------------------------------------------- #
# Document header (title + meta bar) parsing
# --------------------------------------------------------------------------- #
_META_KV_RE = re.compile(r"^\s*([^:]+?)\s*:\s*(.+?)\s*$")


def parse_header(text: str):
    """Pull the first H1 as the title and an optional meta blockquote as chips.

    A metadata line such as:
        > Owner: Jane | Version: v1.2 | Last updated: 2026-07-11
    appearing near the top is rendered as a styled meta bar of chips.

    Returns (title, meta_chips, remaining_markdown) where the H1 and the meta
    line are removed from the remaining markdown (they are rendered in the custom
    header banner instead).
    """
    lines = text.split("\n")
    title = None
    meta_chips = []
    title_idx = None
    meta_idx = None

    # Find the first ATX H1.
    for i, line in enumerate(lines):
        m = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if m:
            title = m.group(1).strip()
            title_idx = i
            break

    # Look for a meta blockquote within the few lines after the H1.
    if title_idx is not None:
        window_end = min(len(lines), title_idx + 8)
        for j in range(title_idx + 1, window_end):
            raw = lines[j]
            if not raw.strip():
                continue
            if raw.lstrip().startswith(">") and "|" in raw:
                body = raw.lstrip()[1:].strip()
                # Skip HTML-comment-only blockquote hint lines.
                if body.startswith("<!--"):
                    continue
                for part in body.split("|"):
                    part = part.strip()
                    if not part:
                        continue
                    kv = _META_KV_RE.match(part)
                    if kv:
                        meta_chips.append((kv.group(1).strip(), kv.group(2).strip()))
                    else:
                        meta_chips.append((None, part))
                meta_idx = j
                break
            # A non-blockquote, non-blank line before any meta -> stop looking.
            if not raw.lstrip().startswith(">"):
                break

    # Remove the consumed lines from the body.
    drop = set()
    if title_idx is not None:
        drop.add(title_idx)
    if meta_idx is not None:
        drop.add(meta_idx)
    remaining = "\n".join(l for k, l in enumerate(lines) if k not in drop)
    return title, meta_chips, remaining


# --------------------------------------------------------------------------- #
# Markdown conversion — preferred path (python-markdown)
# --------------------------------------------------------------------------- #
def convert_with_python_markdown(text: str):
    """Convert using python-markdown. Returns (html, True) or None if unavailable."""
    try:
        import markdown  # type: ignore
    except ImportError:
        return None

    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "sane_lists",
            "attr_list",
            "def_list",
        ],
        output_format="html5",
    )
    return md.convert(text), True


# --------------------------------------------------------------------------- #
# Markdown conversion — fallback path (dependency-free, built in)
# --------------------------------------------------------------------------- #
def _slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)  # strip any inline tags
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "section"


def _inline(text: str) -> str:
    """Inline formatting: code, links, bold, italic, strikethrough.

    Inline code spans are protected first so their contents are not re-formatted.
    """
    # Protect inline code spans with placeholders.
    code_spans = []

    def _stash_code(m):
        code_spans.append(m.group(1))
        return "\x00CODE{0}\x00".format(len(code_spans) - 1)

    text = re.sub(r"`([^`]+)`", _stash_code, text)

    # Escape the remaining text.
    text = html.escape(text, quote=False)

    # Links: [label](url)
    def _link(m):
        label, url = m.group(1), m.group(2)
        url = url.strip()
        return '<a href="{0}">{1}</a>'.format(html.escape(url, quote=True), label)

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)

    # Bold (** or __), then italic (* or _), then strikethrough (~~).
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_(?!\s)(.+?)(?<!\s)_(?!_)", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)

    # Restore protected code spans (escaped).
    def _restore_code(m):
        idx = int(m.group(1))
        return "<code>{0}</code>".format(html.escape(code_spans[idx], quote=False))

    text = re.sub(r"\x00CODE(\d+)\x00", _restore_code, text)
    return text


def _is_table_sep(line: str) -> bool:
    line = line.strip()
    if "|" not in line and "-" not in line:
        return False
    cells = [c for c in line.strip().strip("|").split("|")]
    if not cells:
        return False
    for c in cells:
        if not re.match(r"^\s*:?-+:?\s*$", c):
            return False
    return True


def _split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # Split on unescaped pipes.
    cells = re.split(r"(?<!\\)\|", line)
    return [c.replace("\\|", "|").strip() for c in cells]


def _render_table(header, aligns, rows):
    def align_style(i):
        if i < len(aligns) and aligns[i]:
            return ' style="text-align:{0}"'.format(aligns[i])
        return ""

    out = ['<div class="table-wrap"><table>']
    out.append("<thead><tr>")
    for i, cell in enumerate(header):
        out.append("<th{0}>{1}</th>".format(align_style(i), _inline(cell)))
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        for i in range(len(header)):
            cell = row[i] if i < len(row) else ""
            out.append("<td{0}>{1}</td>".format(align_style(i), _inline(cell)))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _parse_aligns(sep_line):
    aligns = []
    for c in _split_row(sep_line):
        c = c.strip()
        left = c.startswith(":")
        right = c.endswith(":")
        if left and right:
            aligns.append("center")
        elif right:
            aligns.append("right")
        elif left:
            aligns.append("left")
        else:
            aligns.append("")
    return aligns


def _render_list(items):
    """items: list of (marker, content, checkbox) where marker in {'ul','ol'}."""
    if not items:
        return ""
    kind = items[0][0]
    tag = "ul" if kind == "ul" else "ol"
    cls = ""
    out = []
    lines_out = []
    for _marker, content, checkbox in items:
        if checkbox is not None:
            cls = ' class="task-list"'
            box = (
                '<input type="checkbox" disabled checked> '
                if checkbox
                else '<input type="checkbox" disabled> '
            )
            lines_out.append("<li>{0}{1}</li>".format(box, _inline(content)))
        else:
            lines_out.append("<li>{0}</li>".format(_inline(content)))
    out.append("<{0}{1}>".format(tag, cls))
    out.extend(lines_out)
    out.append("</{0}>".format(tag))
    return "".join(out)


def convert_with_fallback(text: str):
    """Dependency-free Markdown -> HTML. Returns (html, False)."""
    lines = text.split("\n")
    n = len(lines)
    i = 0
    out = []
    seen_ids = {}

    def unique_id(base):
        base = base or "section"
        if base not in seen_ids:
            seen_ids[base] = 0
            return base
        seen_ids[base] += 1
        return "{0}-{1}".format(base, seen_ids[base])

    while i < n:
        line = lines[i]

        # Mermaid / other placeholder token on its own line -> pass through.
        if line.strip().startswith("\x00MERMAID_BLOCK_"):
            out.append(line.strip())
            i += 1
            continue

        # Blank line.
        if not line.strip():
            i += 1
            continue

        # Fenced code block.
        fence = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker = fence.group(1)[0]
            lang = fence.group(2).strip()
            code_lines = []
            i += 1
            while i < n and not re.match(
                r"^[ \t]*" + re.escape(marker) + r"{3,}[ \t]*$", lines[i]
            ):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            cls = ' class="language-{0}"'.format(html.escape(lang, quote=True)) if lang else ""
            code = html.escape("\n".join(code_lines), quote=False)
            out.append("<pre><code{0}>{1}</code></pre>".format(cls, code))
            continue

        # Horizontal rule.
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # Heading.
        h = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if h:
            level = len(h.group(1))
            content = _inline(h.group(2))
            hid = unique_id(_slugify(h.group(2)))
            out.append(
                '<h{0} id="{1}">{2}<a class="anchor" href="#{1}" aria-label="Link to this section">#</a></h{0}>'.format(
                    level, hid, content
                )
            )
            i += 1
            continue

        # Blockquote.
        if line.lstrip().startswith(">"):
            quote_lines = []
            while i < n and lines[i].lstrip().startswith(">"):
                q = lines[i].lstrip()[1:]
                if q.startswith(" "):
                    q = q[1:]
                quote_lines.append(q)
                i += 1
            inner = convert_with_fallback("\n".join(quote_lines))[0]
            out.append("<blockquote>{0}</blockquote>".format(inner))
            continue

        # Table: header row followed by a separator row.
        if "|" in line and i + 1 < n and _is_table_sep(lines[i + 1]):
            header = _split_row(line)
            aligns = _parse_aligns(lines[i + 1])
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                if not lines[i].strip():
                    break
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(_render_table(header, aligns, rows))
            continue

        # Lists (ordered / unordered / task).
        list_item = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if list_item:
            items = []
            while i < n:
                m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
                if not m:
                    # Allow blank line then continuation? Keep it simple: stop.
                    if not lines[i].strip():
                        # peek: if next is a list item, treat blank as separator
                        if i + 1 < n and re.match(
                            r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i + 1]
                        ):
                            i += 1
                            continue
                    break
                bullet = m.group(2)
                kind = "ol" if re.match(r"\d+[.)]", bullet) else "ul"
                content = m.group(3)
                checkbox = None
                cb = re.match(r"^\[([ xX])\]\s+(.*)$", content)
                if cb:
                    checkbox = cb.group(1).lower() == "x"
                    content = cb.group(2)
                items.append((kind, content, checkbox))
                i += 1
            out.append(_render_list(items))
            continue

        # Paragraph: gather consecutive non-structural lines.
        para_lines = [line]
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            if re.match(r"^(#{1,6})\s+", nxt):
                break
            if re.match(r"^[ \t]*(`{3,}|~{3,})", nxt):
                break
            if nxt.lstrip().startswith(">"):
                break
            if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", nxt):
                break
            if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", nxt):
                break
            if "|" in nxt and i + 1 < n and _is_table_sep(lines[i + 1]):
                break
            if nxt.strip().startswith("\x00MERMAID_BLOCK_"):
                break
            para_lines.append(nxt)
            i += 1
        para = "<br>\n".join(_inline(pl) for pl in para_lines)
        out.append("<p>{0}</p>".format(para))

    return "\n".join(out), False


# --------------------------------------------------------------------------- #
# Post-processing: heading ids (for TOC) and status badges
# --------------------------------------------------------------------------- #
_HEADING_RE = re.compile(
    r"<h([1-6])(?P<attrs>[^>]*)>(?P<inner>.*?)</h\1>", re.DOTALL | re.IGNORECASE
)


def ensure_heading_ids(html_text: str):
    """Make sure every heading has an id; collect (level, id, label) for the TOC."""
    seen = {}
    headings = []

    def uid(base):
        base = base or "section"
        if base not in seen:
            seen[base] = 0
            return base
        seen[base] += 1
        return "{0}-{1}".format(base, seen[base])

    def repl(m):
        level = int(m.group(1))
        attrs = m.group("attrs")
        inner = m.group("inner")
        # Existing id?
        id_match = re.search(r'id="([^"]+)"', attrs)
        # Label as plain text: drop the anchor link, strip tags, and unescape
        # entities so the TOC carries raw text (build_toc escapes exactly once,
        # otherwise "&" in a heading double-escapes to a literal "&amp;").
        label = re.sub(r'<a class="anchor".*?</a>', "", inner, flags=re.DOTALL)
        label = re.sub(r"<[^>]+>", "", label).strip()
        label = html.unescape(label)
        if id_match:
            hid = id_match.group(1)
            new_attrs = attrs
        else:
            hid = uid(_slugify(label))
            new_attrs = attrs + ' id="{0}"'.format(hid)
        headings.append((level, hid, label))
        # Add a hover anchor if none present.
        if 'class="anchor"' not in inner:
            inner = (
                inner
                + '<a class="anchor" href="#{0}" aria-label="Link to this section">#</a>'.format(
                    hid
                )
            )
        return "<h{0}{1}>{2}</h{0}>".format(level, new_attrs, inner)

    new_html = _HEADING_RE.sub(repl, html_text)
    return new_html, headings


# Status word -> badge modifier class.
_BADGE_MAP = {
    "done": "ok",
    "in progress": "warn",
    "not started": "muted",
    "yes": "ok",
    "no": "muted",
    "required": "warn",
    "optional": "muted",
    "unused": "info",
    "in use": "warn",
    "used": "ok",
    "canceled": "danger",
    "cancelled": "danger",
}

_TD_RE = re.compile(r"(<td[^>]*>)(.*?)(</td>)", re.DOTALL | re.IGNORECASE)


def add_status_badges(html_text: str) -> str:
    """Wrap table cells whose entire content is a known status word in a badge chip."""

    def repl(m):
        open_tag, content, close_tag = m.group(1), m.group(2), m.group(3)
        plain = re.sub(r"<[^>]+>", "", content).strip()
        key = plain.lower()
        if key in _BADGE_MAP:
            badge = '<span class="badge badge-{0}">{1}</span>'.format(
                _BADGE_MAP[key], html.escape(plain, quote=False)
            )
            return open_tag + badge + close_tag
        return m.group(0)

    return _TD_RE.sub(repl, html_text)


# --------------------------------------------------------------------------- #
# Table of contents
# --------------------------------------------------------------------------- #
def build_toc(headings):
    """Build a nested nav list from h2/h3 headings."""
    items = [h for h in headings if h[0] in (2, 3)]
    if not items:
        return ""
    parts = ['<nav class="toc" aria-label="Table of contents"><div class="toc-title">On this page</div><ul>']
    for level, hid, label in items:
        cls = "toc-h2" if level == 2 else "toc-h3"
        parts.append(
            '<li class="{0}"><a href="#{1}">{2}</a></li>'.format(
                cls, hid, html.escape(label, quote=False)
            )
        )
    parts.append("</ul></nav>")
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Mermaid script (CDN with offline vendored fallback)
# --------------------------------------------------------------------------- #
def mermaid_script(script_dir: str) -> str:
    """Return the <script> block that renders Mermaid diagrams.

    If a vendored copy exists at assets/vendor/mermaid.min.js (relative to the
    skill root, i.e. the parent of scripts/), it is INLINED for fully offline
    rendering. Otherwise a CDN module import is used, which degrades gracefully
    to showing the raw diagram source when offline.
    """
    # To vendor Mermaid for offline use, download the UMD build and save it as:
    #   assets/vendor/mermaid.min.js
    # e.g.  curl -L https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js \
    #            -o assets/vendor/mermaid.min.js
    # When that file is present it is inlined below instead of loading from a CDN.
    skill_root = os.path.dirname(script_dir)
    vendor_path = os.path.join(skill_root, "assets", "vendor", "mermaid.min.js")
    if os.path.isfile(vendor_path):
        try:
            with open(vendor_path, "r", encoding="utf-8") as fh:
                lib = fh.read()
            return (
                "<!-- Mermaid inlined from assets/vendor/mermaid.min.js (offline) -->\n"
                "<script>\n" + lib + "\n</script>\n"
                "<script>\n"
                "  if (window.mermaid) {\n"
                "    mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });\n"
                "    window.addEventListener('DOMContentLoaded', function () {\n"
                "      try { mermaid.run({ querySelector: '.mermaid' }); } catch (e) {}\n"
                "    });\n"
                "  }\n"
                "</script>"
            )
        except OSError:
            pass
    # CDN fallback: raw diagram source stays visible offline.
    return (
        "<!-- Mermaid via CDN. For offline rendering, save the UMD build to\n"
        "     assets/vendor/mermaid.min.js and it will be inlined instead. -->\n"
        '<script type="module">\n'
        "  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';\n"
        "  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });\n"
        "  try { await mermaid.run({ querySelector: '.mermaid' }); } catch (e) {}\n"
        "</script>"
    )


# --------------------------------------------------------------------------- #
# Page assembly (CSS + scroll-spy JS all inlined)
# --------------------------------------------------------------------------- #
CSS = r"""
:root {
  --accent: #2563eb;
  --accent-soft: #eff4ff;
  --fg: #1f2933;
  --fg-muted: #64748b;
  --bg: #ffffff;
  --bg-alt: #f8fafc;
  --border: #e2e8f0;
  --code-bg: #f5f7fa;
  --sidebar-w: 264px;
  --measure: 860px;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--fg);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial,
    "Apple Color Emoji", "Segoe UI Emoji", sans-serif;
  font-size: 16px;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
.layout { display: flex; align-items: flex-start; max-width: 1240px; margin: 0 auto; }

/* Sidebar / TOC */
.sidebar {
  width: var(--sidebar-w);
  flex: 0 0 var(--sidebar-w);
  position: sticky;
  top: 0;
  align-self: flex-start;
  height: 100vh;
  overflow-y: auto;
  padding: 28px 16px 40px 24px;
  border-right: 1px solid var(--border);
}
.toc-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--fg-muted);
  margin-bottom: 10px;
}
.toc ul { list-style: none; margin: 0; padding: 0; }
.toc li { margin: 0; }
.toc a {
  display: block;
  padding: 4px 10px;
  border-radius: 6px;
  color: var(--fg-muted);
  text-decoration: none;
  font-size: 13.5px;
  line-height: 1.4;
  border-left: 2px solid transparent;
}
.toc a:hover { color: var(--fg); background: var(--bg-alt); }
.toc .toc-h3 a { padding-left: 22px; font-size: 13px; }
.toc a.active {
  color: var(--accent);
  background: var(--accent-soft);
  border-left-color: var(--accent);
  font-weight: 600;
}

/* Content */
.content {
  flex: 1 1 auto;
  min-width: 0;
  max-width: var(--measure);
  padding: 40px 40px 96px;
  margin: 0 auto;
}

/* Document header banner */
.doc-header {
  margin-bottom: 28px;
  padding-bottom: 22px;
  border-bottom: 2px solid var(--border);
}
.doc-header h1 {
  margin: 0 0 12px;
  font-size: 30px;
  line-height: 1.25;
  letter-spacing: -.01em;
}
.meta-bar { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--bg-alt);
  border: 1px solid var(--border);
  font-size: 13px;
  color: var(--fg);
}
.chip .chip-k { color: var(--fg-muted); font-weight: 600; }

/* Headings */
.content h2, .content h3, .content h4, .content h5, .content h6 {
  scroll-margin-top: 20px;
  line-height: 1.3;
  position: relative;
}
.content h2 {
  margin: 40px 0 14px;
  padding-bottom: 6px;
  font-size: 23px;
  border-bottom: 1px solid var(--border);
}
.content h3 { margin: 30px 0 10px; font-size: 19px; }
.content h4 { margin: 24px 0 8px; font-size: 16.5px; }
.content h1 { font-size: 27px; margin: 32px 0 14px; }
.anchor {
  margin-left: 8px;
  color: var(--border);
  text-decoration: none;
  font-weight: 400;
  opacity: 0;
  transition: opacity .12s ease;
}
h1:hover .anchor, h2:hover .anchor, h3:hover .anchor,
h4:hover .anchor, h5:hover .anchor, h6:hover .anchor { opacity: 1; }
.anchor:hover { color: var(--accent); }

.content p { margin: 12px 0; }
.content a { color: var(--accent); text-decoration: none; }
.content a:hover { text-decoration: underline; }
.content ul, .content ol { padding-left: 26px; margin: 12px 0; }
.content li { margin: 4px 0; }
ul.task-list { list-style: none; padding-left: 4px; }
ul.task-list li { display: flex; align-items: flex-start; gap: 8px; }
ul.task-list input { margin-top: 6px; }
hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

/* Blockquote callouts */
blockquote {
  margin: 16px 0;
  padding: 12px 18px;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 8px 8px 0;
  color: var(--fg);
}
blockquote p { margin: 6px 0; }

/* Code */
code {
  font-family: "SF Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .9em;
  background: var(--code-bg);
  padding: .15em .4em;
  border-radius: 5px;
  border: 1px solid var(--border);
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
  overflow-x: auto;
  margin: 16px 0;
}
pre code { background: none; border: none; padding: 0; font-size: 13.5px; line-height: 1.55; }

/* Tables */
.table-wrap { overflow-x: auto; margin: 18px 0; border: 1px solid var(--border); border-radius: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
thead th {
  position: sticky;
  top: 0;
  background: var(--bg-alt);
  text-align: left;
  font-weight: 700;
  color: var(--fg);
  border-bottom: 2px solid var(--border);
  z-index: 1;
}
th, td { padding: 9px 14px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); vertical-align: top; }
th:last-child, td:last-child { border-right: none; }
tbody tr:nth-child(even) { background: var(--bg-alt); }
tbody tr:hover { background: var(--accent-soft); }

/* Status badges */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12.5px;
  font-weight: 600;
  line-height: 1.5;
  white-space: nowrap;
}
.badge-ok     { background: #e7f6ec; color: #1a7f37; }
.badge-warn   { background: #fef4e5; color: #b7791f; }
.badge-info   { background: #e7f0fd; color: #1d4ed8; }
.badge-danger { background: #fdecec; color: #c0392b; }
.badge-muted  { background: #eef1f5; color: #64748b; }

/* Mermaid */
pre.mermaid {
  background: var(--bg);
  border: 1px solid var(--border);
  text-align: center;
  padding: 18px;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --accent: #60a5fa;
    --accent-soft: #17233a;
    --fg: #e5e9f0;
    --fg-muted: #97a3b6;
    --bg: #0f141b;
    --bg-alt: #161d27;
    --border: #2a3441;
    --code-bg: #161d27;
  }
  .badge-ok     { background: #14331f; color: #6ee7a0; }
  .badge-warn   { background: #33290f; color: #f4c66b; }
  .badge-info   { background: #16263f; color: #7fb0f7; }
  .badge-danger { background: #3a1a1a; color: #f19a92; }
  .badge-muted  { background: #232b36; color: #97a3b6; }
  pre.mermaid { background: #f8fafc; }
}

/* Responsive: hide sidebar on narrow screens */
@media (max-width: 900px) {
  .sidebar { display: none; }
  .content { padding: 28px 20px 72px; max-width: 100%; }
}

/* Print: clean single-column PDF */
@media print {
  .sidebar { display: none !important; }
  .content { max-width: 100%; padding: 0; }
  .anchor { display: none; }
  a { color: inherit; text-decoration: none; }
  body { font-size: 12pt; }
  pre, blockquote, .table-wrap, table, tr, img { page-break-inside: avoid; }
  thead th { position: static; }
  h2, h3, h4 { page-break-after: avoid; }
}
"""

SCROLLSPY_JS = r"""
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (!links.length) return;
  var map = {};
  var targets = [];
  links.forEach(function (a) {
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    var el = document.getElementById(id);
    if (el) { map[id] = a; targets.push(el); }
  });
  function clear() { links.forEach(function (a) { a.classList.remove('active'); }); }
  var observer = new IntersectionObserver(function (entries) {
    // Pick the entry closest to the top that is intersecting.
    var visible = entries.filter(function (e) { return e.isIntersecting; });
    if (!visible.length) return;
    visible.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
    var id = visible[0].target.id;
    if (map[id]) {
      clear();
      map[id].classList.add('active');
      map[id].scrollIntoView({ block: 'nearest' });
    }
  }, { rootMargin: '0px 0px -75% 0px', threshold: 0 });
  targets.forEach(function (t) { observer.observe(t); });

  // Fallback / first-paint: highlight the nearest heading above the viewport top.
  function syncOnScroll() {
    var best = null, bestTop = -Infinity;
    targets.forEach(function (t) {
      var top = t.getBoundingClientRect().top;
      if (top <= 120 && top > bestTop) { bestTop = top; best = t; }
    });
    if (best && map[best.id]) { clear(); map[best.id].classList.add('active'); }
  }
  window.addEventListener('scroll', function () {
    window.requestAnimationFrame(syncOnScroll);
  }, { passive: true });
  syncOnScroll();
})();
"""


def render_meta_bar(meta_chips) -> str:
    if not meta_chips:
        return ""
    chips = []
    for key, value in meta_chips:
        if key:
            chips.append(
                '<span class="chip"><span class="chip-k">{0}</span><span>{1}</span></span>'.format(
                    html.escape(key, quote=False), html.escape(value, quote=False)
                )
            )
        else:
            chips.append('<span class="chip">{0}</span>'.format(html.escape(value, quote=False)))
    return '<div class="meta-bar">{0}</div>'.format("".join(chips))


def assemble_page(title, meta_chips, toc_html, body_html, mermaid_js) -> str:
    header_parts = ['<header class="doc-header">']
    header_parts.append("<h1>{0}</h1>".format(html.escape(title, quote=False)))
    header_parts.append(render_meta_bar(meta_chips))
    header_parts.append("</header>")
    header_html = "".join(header_parts)

    sidebar = '<aside class="sidebar">{0}</aside>'.format(toc_html) if toc_html else ""

    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>{title}</title>\n"
        "<style>{css}</style>\n"
        "</head>\n<body>\n"
        '<div class="layout">\n'
        "{sidebar}\n"
        '<main class="content">\n{header}\n{body}\n</main>\n'
        "</div>\n"
        "{mermaid}\n"
        "<script>{spy}</script>\n"
        "</body>\n</html>\n"
    ).format(
        title=html.escape(title, quote=False),
        css=CSS,
        sidebar=sidebar,
        header=header_html,
        body=body_html,
        mermaid=mermaid_js,
        spy=SCROLLSPY_JS,
    )


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def convert(markdown_text: str, title_override=None, script_dir=None):
    """Full pipeline: Markdown text -> complete HTML document string."""
    if script_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Parse the document header (title + meta bar) and strip it from the body.
    parsed_title, meta_chips, body_md = parse_header(markdown_text)
    title = title_override or parsed_title or "Product Requirements Document"

    # 2. Extract Mermaid blocks so the converter cannot touch them.
    body_md, mermaid_blocks = extract_mermaid(body_md)

    # 3. Convert Markdown -> HTML (preferred path, then fallback).
    result = convert_with_python_markdown(body_md)
    if result is None:
        body_html, used_lib = convert_with_fallback(body_md)
        sys.stderr.write(
            "[prd_to_html] python-markdown not found; using built-in dependency-free converter.\n"
        )
    else:
        body_html, used_lib = result
        sys.stderr.write("[prd_to_html] using python-markdown for conversion.\n")

    # 4. Re-insert Mermaid blocks as <pre class="mermaid">.
    body_html = reinsert_mermaid(body_html, mermaid_blocks)

    # 5. Ensure heading ids + collect them for the TOC.
    body_html, headings = ensure_heading_ids(body_html)

    # 6. Auto status badges in table cells.
    body_html = add_status_badges(body_html)

    # 7. Build TOC and Mermaid script, then assemble the page.
    toc_html = build_toc(headings)
    mermaid_js = mermaid_script(script_dir)
    return assemble_page(title, meta_chips, toc_html, body_html, mermaid_js)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render a PRD Markdown file into one polished, self-contained HTML page.",
    )
    parser.add_argument("input", help="Path to the input Markdown (.md) file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output HTML file (default: input with a .html extension).",
    )
    parser.add_argument(
        "--title",
        help="Override the document title (default: parsed from the first H1).",
    )
    args = parser.parse_args(argv)

    if not os.path.isfile(args.input):
        parser.error("input file not found: {0}".format(args.input))

    output = args.output
    if not output:
        base, _ = os.path.splitext(args.input)
        output = base + ".html"

    with open(args.input, "r", encoding="utf-8") as fh:
        markdown_text = fh.read()

    html_doc = convert(markdown_text, title_override=args.title)

    with open(output, "w", encoding="utf-8") as fh:
        fh.write(html_doc)

    sys.stderr.write(
        "[prd_to_html] wrote {0} ({1} bytes).\n".format(output, len(html_doc.encode("utf-8")))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
