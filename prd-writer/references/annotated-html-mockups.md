# Annotated HTML Mockups — the skill's default document format

> **This file describes how the skill's default deliverable is built.** A PRD is authored as one self-contained
> HTML file, and its signature device is the **annotated-mockup triad**: a pixel-faithful HTML/CSS recreation of a
> screen, numbered callout markers pinned onto its elements, and an explanation table keyed one-to-one to those
> numbers — so the picture and the spec sit together and can never drift apart.
>
> Start from `assets/annotated-html-prd-template.html` (the design system) and `references/design-system.md` (the
> token + component contract). This file is the method.

---

## Mode selection

| | Hand-authored annotated HTML **(default)** | Markdown + `scripts/prd_to_html.py` |
|---|---|---|
| Reach for it when | **Almost every PRD.** Any spec with a UI surface, any iteration on a shipped product, anything a stakeholder will read, share, print, or archive. | The user **explicitly asked for Markdown**, or the change is a one-screen tweak with no UI to annotate. |
| Mockups | Recreate the screen in HTML/CSS and pin numbered markers on it, in-doc. | None available — reference an external wireframe by page number. |
| Diagrams | Inline SVG + `.flow` chains. No network. | Mermaid (loaded from a CDN). |
| Editing | Edit HTML directly; verify with `scripts/verify_prd_html.py` (see *Verification*). | Edit Markdown, re-render. |

**The two modes do not combine.** `scripts/prd_to_html.py` carries a separate, simpler stylesheet: grep its `CSS`
constant and you will find **zero** occurrences of `.mk`, `.nbadge`, `.anno`, `.mock`, `.spec`, `.callout`, `.pill`,
`.drawer`, or `.inter-list`. There is no flag to inject the mockup CSS. Markup pasted into a Markdown PRD renders
**unstyled** — a marker becomes a stray digit, a `.spec` block becomes an unlabelled table. If the doc needs any of
those, it needs the default HTML format, not a hybrid.

## Language

Write the document in **the user's language** — the language of their request and of their existing PRD corpus.
Set `<html lang="…">` to match the body. Keep the CJK font stack (`"PingFang SC","Hiragino Sans GB","Microsoft
YaHei"`) in the template regardless of language, so mixed CJK content always renders. Product names, metric names,
entity names, and code identifiers stay in their original English; only the connective prose is translated.

The design system's **fixed strings** — the four `.spec-label` texts and the four legend table headers — live in
exactly one place: *Fixed strings* in `references/design-system.md`, which gives each one in both Chinese and
English. Copy them from there byte for byte. Pick one language and use it consistently through the whole document
— never paraphrase and never mix. The *two-language reference table itself* is maintained in that one file and is
never duplicated elsewhere; markup examples in these docs quote the individual strings verbatim, which is fine
precisely because they are byte-identical copies.

The order ①→②→③→④ never varies. A page may shorten ④ (`④ 交互` / `④ Interactions`) but may not reorder or renumber.

## The core device: the annotated-mockup triad

Every annotated screen is three coupled pieces. Keep them adjacent and keep their numbers in lockstep.

1. **A titled container** — `.anno-wrap` wrapping a `.mock` "screen" that holds a faithful HTML/CSS recreation of the UI.
2. **Numbered markers pinned on elements** — each callout is `<span class="anno"><span class="mk">N</span>…element…</span>`.
3. **An explanation table keyed to the markers** — a `table.data` whose first column is `<span class="nbadge">N</span>`,
   one row per marker, using the fixed 4-column legend schema above.

Marker `N` on the mockup ↔ row `N` in the table, **one-to-one and continuous**. That correspondence is the whole point:
a reviewer reads a number off the picture and finds its full spec in the row, and vice-versa.

```html
<div class="anno-wrap">
  <span class="anno-title">🖼 功能标注 · Overview 页 <code>#overview</code></span>
  <div class="mock">
    <!-- faithful UI recreation goes here; pin a marker by wrapping the element -->
    <div class="mock-row">
      <span class="anno"><span class="mk">1</span><span class="mtab active">Overview</span></span>
      <span class="mtab">Influencer</span>
      <span class="anno"><span class="mk">2</span><span class="mbtn">Share</span></span>
    </div>
    <span class="anno mchips"><span class="mk">3</span>
      <span class="mchip active">All</span><span class="mchip">Instagram</span><span class="mchip">TikTok</span>
    </span>
  </div>
  <table class="data" style="margin-top:14px">
    <tr><th style="width:52px">标号</th><th style="width:190px">含义（元素）</th><th style="width:33%">交互</th><th>逻辑 / 数据来源</th></tr>
    <tr><td class="c"><span class="nbadge">1</span></td><td>子 Tab 切换器</td><td>点击切换两大视图，当前项高亮</td><td>默认进 Overview；前端路由，无数据依赖</td></tr>
    <tr><td class="c"><span class="nbadge">2</span></td><td>Share 按钮</td><td>点击 → 打开分享弹窗</td><td>无快照时禁用；后端 <code>crypto/rand</code> token</td></tr>
    <tr><td class="c"><span class="nbadge">3</span></td><td>平台筛选 chip（单选）</td><td>点某 chip → 指标卡按该平台重取</td><td>All = 全平台汇总；平台归一 <code>LOWER(TRIM)</code></td></tr>
  </table>
</div>
```

Never substitute ASCII box-drawing, a `<pre>` block, a screenshot link, or a Mermaid diagram for a mockup. ASCII art
does not reflow, cannot be searched, cannot show an active tab or a disabled button, and makes marker↔table continuity
unverifiable. If you find yourself typing `┌───┐`, you are in the wrong format — open the template and copy the closest
component.

## The three numbering systems — keep them separate

This is the rule most often broken, and breaking it makes a document unreadable. There are **three** independent
numbering devices. They never mix, and a diagram never uses two of them without a legend.

**1. `.mk` / `.nbadge` — plain Arabic digits.** Markers on a mockup and their legend rows. Restart at `1` in **every**
`.anno-wrap`. Ascending, no gaps, no duplicates, no circled glyphs, no error markers. Laid out in **visual reading
order** — top-left of the mock first, then down and right — which may differ from DOM order (a right-hand side rail is
numbered where it appears on screen, not where it sits in the source).

**2. Circled numerals ①②③④⑤⑥ — a different device entirely.** Used in exactly three places:
(a) the four `.spec-label` texts, (b) node text inside `.flow` use-case chains, (c) inline prose in `.doc-head` or a
`.callout info` that names the four dimensions. Never on a mockup marker, never in a legend table.

**3. `.marker` inside `ol.inter-list` — a third system.** Sequential Arabic digits in orange circles for **正常 /
normal** items; the literal `!` in a red circle (`.marker.err`) for **every 异常 / abnormal** item — abnormal items are
never numbered. All normal items come first, then all abnormal ones.

```html
<ol class="inter-list">
  <li><span class="marker">1</span><span class="tag normal">正常</span>点击 <b>Report</b> Tab → 加载报表 Overview 页（P1）。</li>
  <li><span class="marker">2</span><span class="tag normal">正常</span>切换平台 chip → 指标卡按该平台重取。</li>
  <li><span class="marker err">!</span><span class="tag err">异常</span>无 <code>CAMPAIGN_REPORT</code> 权限 → Report Tab 不可见（Tab 级门控）。</li>
</ol>
```

Separately, identifier prefixes carry their own sequences and must not be recycled into the above: pages `P0…Pn`
(sub-pages `P2.1`), modules `M1…Mn`, global rules `G1…Gn`, change points `C1…Cn`. The middot `·` always separates an
identifier from its name (`P2.1 · Post Details 抽屉`, `M6 · Posting Timeline`).

## Inline-SVG diagram recipe

E-R diagrams and state machines are **inline SVG**. Zero Mermaid, zero external images — the file must render from a
`file://` URL on a machine with no network.

**The arrowhead is fixed.** Every SVG declares its own marker in `<defs>` with a **unique id per SVG** (the gold uses
`er-a`, `p1a`, `p1b`, `p3a`) so ids never collide across the document:

```html
<defs><marker id="p1a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#94a3b8"/></marker></defs>
```

`#94a3b8` is the stroke colour of **every** arrow and the fill of **every** arrowhead. Do not vary it — the only
coloured paths are dashed derivation edges in an E-R diagram, which take their source entity's stroke colour.

**Boxes.** `rx="8"` always. Height `34` / `38` / `40` for state nodes, `52` / `60` for E-R entities. Fill and stroke
come from this table and nowhere else:

| State / role | fill | stroke | text fill |
|---|---|---|---|
| neutral / idle / empty | `#eef2f7` | `#64748b` | `#475569` |
| loading / generating / purple entity | `#faf5ff` | `#7c5cd6` | `#5a3fb0` |
| success / active / terminal | `#eef7f2` | `#1f9d55` | `#166c3c` |
| error / failed / revoked | `#fdeae8` | `#d84c4c` | `#a83232` |
| warn / stale / expired | `#fdf6ec` (or `#fdeede`) | `#e2802b` | `#9a5b16` |
| primary entity (E-R) | `#eef3ff` | `#2a66e8` | `#1b3a70` |
| teal entity (E-R) | `#f2f9f6` | `#0f9d8f` | `#166c3c` |

**Line semantics.** A **solid** path is a primary transition or a real business relationship. `stroke-dasharray="4 3"`
is a return/retry edge, or a **derived** entity in an E-R diagram (something materialised from another entity rather
than authored directly). Edge labels are `<text font-size="10" fill="#8592a6">` placed by hand beside the path;
E-R cardinality labels are `text-anchor="middle" font-size="10.5" fill="#8592a6"` reading `1:N` / `N:1`.

**An E-R entity box carries two `<text>` lines** — a title (`font-size="13" font-weight="700" fill="#1b3a70"`) and a
sub-caption (`font-size="11" fill="#64748b"`) naming what the entity actually holds.

**A grey caption `<p>` after the diagram is mandatory**, explaining what solid vs dashed means in *this* diagram:

```html
<p style="font-size:12.5px;color:var(--muted)">实线 = 业务实体关系；虚线 = Offer 每日派生的报表侧实体（快照 / 分享 / AI）。</p>
```

Copy-ready state machine, verbatim from the gold (P1 four-state page load):

```html
<div class="diagram">
<svg viewBox="0 0 640 150" width="640" height="150" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p1a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#94a3b8"/></marker></defs>
  <rect x="20" y="58" width="110" height="40" rx="8" fill="#faf5ff" stroke="#7c5cd6"/><text x="75" y="83" text-anchor="middle" font-size="12.5" fill="#5a3fb0">loading 骨架</text>
  <rect x="230" y="10" width="110" height="40" rx="8" fill="#eef7f2" stroke="#1f9d55"/><text x="285" y="35" text-anchor="middle" font-size="12.5" fill="#166c3c">data 正常</text>
  <rect x="230" y="58" width="110" height="40" rx="8" fill="#eef2f7" stroke="#64748b"/><text x="285" y="83" text-anchor="middle" font-size="12.5" fill="#475569">empty 空态</text>
  <rect x="230" y="106" width="110" height="40" rx="8" fill="#fdeede" stroke="#e2802b"/><text x="285" y="131" text-anchor="middle" font-size="12.5" fill="#9a5b16">error 错误</text>
  <rect x="470" y="106" width="130" height="40" rx="8" fill="#faf5ff" stroke="#7c5cd6"/><text x="535" y="131" text-anchor="middle" font-size="12" fill="#5a3fb0">retry → loading</text>
  <path d="M130,72 L228,32" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/><text x="180" y="45" font-size="10" fill="#8592a6">有快照</text>
  <path d="M130,78 L228,78" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/><text x="150" y="70" font-size="10" fill="#8592a6">无快照</text>
  <path d="M130,84 L228,122" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/><text x="150" y="112" font-size="10" fill="#8592a6">失败</text>
  <path d="M340,126 L468,126" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
</svg>
</div>
```

Lay out by hand on a coordinate grid: pick a `viewBox`, place boxes in columns, then draw paths from box edge to box
edge. Straight `L` paths for orthogonal edges; a `C` cubic curve when an edge has to arc around other boxes.

## `.flow` chain recipe

A **linear** flow — a use-case sequence, a pipeline, a state list — is a `.flow` chain of styled spans, not an SVG and
not a Mermaid `flowchart`. It reflows on narrow screens, which an SVG does not.

Three node types, and that is all:

- `.node` — a normal step. Blue.
- `.node.term` — a **terminal / happy end-state**. Green.
- `.node.warnn` — a **branch, frozen, or failure path**. Amber.

Two literal glyphs, both inside `<span class="arw">`: **`→`** for sequence, **`/`** for an alternative branch. A node's
own text may also contain `→` to compress a condition and its result into one box (`有效 → 渲染只读报表`).

```html
<div class="flow">
  <span class="node">打开链接</span><span class="arw">→</span>
  <span class="node">校验 token</span><span class="arw">→</span>
  <span class="node term">有效 → 渲染只读报表</span>
  <span class="arw">/</span>
  <span class="node warnn">过期 / 撤销 / 不存在 → P5 失效页</span>
</div>
```

A **numbered use-case** chain puts circled numerals inside the node text (numbering system 2, never Arabic):

```html
<div class="flow">
  <span class="node">① Report Tab</span><span class="arw">→</span>
  <span class="node">② 生成 AI Summary</span><span class="arw">→</span>
  <span class="node">③ Share 链接</span><span class="arw">→</span>
  <span class="node term">⑥ 筛 Influencer / 导出</span>
</div>
```

Use `.flow` for anything that fits on one or two wrapped lines. Reach for inline SVG only when the shape is genuinely
two-dimensional — a state machine with converging edges, or an E-R graph.

## Density targets

A PRD fails this skill by carrying its facts in **sentences** instead of **markup**. Prose volume is not the measure;
the failure case that motivated this file had 65% *more* text than the gold standard and was far worse. Measure
markup instead.

**Target: ≥1 semantic markup token per ~110 visible characters.** Semantic tokens are `.mk`/`.nbadge`, `.marker`,
`.pill`, `.tag.normal`/`.tag.err`, `.callout.rule/.warn/.info`, `.tick`/`.cross`, `.spec-label`. The gold standard
runs ~340 such tokens against ~27,000 visible characters — roughly one every 79 characters.

**Every page with a UI gets at least one `.anno-wrap`.** No exceptions. A page block with a `.screen-desc` and four
`.spec` tables but no triad is the exact defect this format exists to prevent.

Verified counts in the gold standard (`campaign_report_prd.html`, 1,405 lines), as a calibration reference:

| Element | Count |
|---|---|
| `.mk` markers | 54 |
| `.nbadge` legend rows | 54 (exactly balanced — always) |
| `.anno-wrap` triads / `.mock` screens | 8 |
| `table.data` | 43 |
| `.flow` chains | 6 |
| inline `<svg>` | 4 |
| Mermaid blocks | **0** |
| `<pre>` blocks | **0** |
| external `http(s)` URLs | **0** (the only matches are the SVG XML namespace) |

Do not treat these as quotas — a smaller feature needs fewer. Treat the **ratios** as the target: markers balance
exactly, every UI page has a triad, and the Mermaid / `<pre>` / external-URL rows are hard zeros at any size.

## The one rule that will bite you: marker clipping

`.mk` is absolutely positioned at `top:-11px; left:-11px` — it deliberately **overhangs** the top-left corner of the
element it marks. The `.anno` wrapper is `position:relative` so the marker is measured from *that* element's box. Two
consequences you must respect:

- **`.mock` has `overflow:hidden`.** A marker on an element flush against the mock's top or left edge gets **clipped**
  by the mock. Give the mock enough top/left padding (the template uses `18px 18px 16px 20px`) so overhanging markers
  land *inside* the padding box, not outside it.
- **Horizontally-scrolling inner content must not be the marker's offset parent.** If a wide table needs
  `overflow-x:auto`, put that on an **inner** `<div>`, and keep the `.mk`/`.anno` on the outer, non-clipping element —
  otherwise the scroll container clips the overhang. In tables, markers use the smaller in-cell variant automatically
  (`td .mk { left:-8px; top:-8px }`); wrap the cell's content in `<span class="anno"><span class="mk">N</span>…</span>`.

If a marker looks cut off, it is on (or inside) a clipping ancestor. Move it up to a padded, non-clipping wrapper. The
**clip check** in *Verification* finds these automatically.

## Provenance: label where every pixel and number came from

An annotated mockup is persuasive precisely because it looks real — which makes unlabeled guesses dangerous. Mark the
source of every screen and every number so no one mistakes a placeholder for a decision:

- **Traced from a stakeholder demo / live screenshot** — say so in the `.anno-title`. The gold distinguishes two forms:
  `🖼 Demo 功能标注 · …` for a block redrawn from someone else's demo, plain `🖼 功能标注 · …` for a block the PRD
  author designed. Always keep the leading `🖼`.
- **Placeholder values** — when you show sample numbers, state it once, in a `.callout warn` ("Demo 的 N/A 是占位；正式版
  空值按 G8 显示「—」"). Never let a made-up figure read as a real metric.
- **A number's real source lives in the legend's 逻辑 / 数据来源 column**, not on the picture. The picture shows
  *shape*; the row shows *truth*.

**Decision-driven, not demo-driven.** The mockup mirrors what will be **built**, not literally what a stakeholder drew.
When a later decision contradicts the demo (a platform is descoped, a control is deferred), **remove it from the
buildable mockup** and record the deferral in the open-questions table (see `iterating-a-live-product.md`) — do not
leave a control on the picture that engineering is not meant to build.

## Component & CSS catalog

The template's `<style>` block is a small, proven design system. Copy it wholesale; don't reinvent it. The full token
and component contract lives in `references/design-system.md`. Classes you will reach for:

**Layout & chrome**
- `.layout` = sticky `.toc` sidebar + `.content`. `.toc a.active` highlights the current section (scroll-spy script in
  the template). `h2.sec`, `h3`, `h5` are the heading rhythm.
- `.doc-head` + `.meta-table` = the title block (title / owner / version / date).
- `table.data` = every spec table; `td.c` centers; `.tick` (✔) / `.cross` (✘) for matrices.

**Callouts & tags**
- `.callout.info` (blue, context) / `.callout.rule` (green, a binding rule) / `.callout.warn` (amber, a caveat).
- `.pill` variants: `.brand`, `.new` (red "changed/新增"), tier pills `.nano/.micro/.mid/.macro/.mega`, `.m`/`.mir`
  (master/mirrored). Use `.pill.new` to flag what changed in this version.

**The four-dimension spec block** (color-coded, labels fixed — see *Language* above)
- `.spec.field` (blue) / `.spec.cond` (teal) / `.spec.state` (purple) / `.spec.inter` (orange), each opened by a
  `.spec-label` chip.
- Interactions use `ol.inter-list > li` with a `.marker` (orange, `.err` = red for abnormal) and a `.tag.normal` /
  `.tag.err` label, so happy-path and error rows are visually distinct on the same list.

**Flow & diagrams**
- `.flow > .node` (`.term` = green terminal, `.warnn` = amber) joined by `.arw` arrows — see the recipe above.
- `.diagram` wraps every inline SVG and gives it `overflow-x:auto` on narrow screens.

**Mockup primitives** (build the fake UI out of these)
- Cards/metrics: `.mcard`/`.mc-label`/`.mc-val`, `.mgrid`/`.mmetric`. Chips: `.mchip(.active/.new)`. Tabs:
  `.mtab(.active)`, buttons `.mbtn(.ai)`. Tables: `.mtbl`, breakdown `.mbk`. Side nav: `.mock-side`/`.manchor`.
- Lists & timelines: `.mlb-row`/`.mlb-av`/`.mlb-bar`/`.mlb-fill`/`.mlb-val` (leaderboard), `.mtl`/`.mtl-node`
  (horizontal timeline), `.mtc-row`/`.mtc-card` (content carousel).
- Overlays: `.drawer` (right side-sheet), `.popcard` (hover preview), `.minichart` (mini bar chart), `.dialog`
  (confirm modal). Metric tiles `.mtile`, `.mtile.ocr` (amber = sourced from image/OCR, not collection).

Open the template, find the component that looks closest, copy its block, and relabel. **The catalog is a starting
point, not a ceiling** — if a screen genuinely needs a primitive that does not exist, add a new `m*` class inline,
following the same naming and the same palette (`#d3ddec` avatars, the `#8592a6`/`#64748b`/`#54657f` grey ramp,
`#e6ebf3` card borders). Do not force a UI into a leaderboard because a leaderboard is what the template happens
to ship.

## Verification (hand-authored HTML has no compiler — you are it)

Run `python3 scripts/verify_prd_html.py path/to/prd.html` after **every** batch of edits, and before handing the doc
over. It mechanizes checks 1, 2, 4 and 5 below. Check 3 needs a browser.

**1. Tag balance** — catches a dropped `</td>`/`</div>` that silently wrecks layout:

```python
python3 - <<'PY'
from html.parser import HTMLParser
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.errors=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.stack.append((t,s.getpos()[0]))
    def handle_endtag(s,t):
        if t in VOID: return
        if not s.stack: s.errors.append(f'stray </{t}> @L{s.getpos()[0]}'); return
        if s.stack[-1][0]==t: s.stack.pop()
        else:
            for i in range(len(s.stack)-1,-1,-1):
                if s.stack[i][0]==t:
                    s.errors.append(f'</{t}> @L{s.getpos()[0]} closes over '+','.join(f'{x[0]}@L{x[1]}' for x in s.stack[i+1:])); del s.stack[i:]; break
            else: s.errors.append(f'unmatched </{t}> @L{s.getpos()[0]}')
p=P(); p.feed(open('YOUR_PRD.html').read())
print('unclosed@EOF:', [(t,l) for t,l in p.stack])
print('errors:', p.errors)
PY
```
Both lists empty = clean.

**2. Marker ↔ table continuity** — every `.mk` on a screen has a matching `.nbadge` row, numbering continuous 1..N with
no gaps or dupes, restarting at 1 per `.anno-wrap`. A missing or doubled number means the picture and the spec have
drifted.

**3. Marker clip check** — open the file in the browser and run this (IIFE avoids "illegal return"); it flags any marker
swallowed by an `overflow` ancestor:

```javascript
(function(){
  const bad=[];
  document.querySelectorAll('.mk').forEach(mk=>{
    let el=mk.parentElement;
    while(el){
      const o=getComputedStyle(el).overflow;
      if(o&&o!=='visible'){
        const r=mk.getBoundingClientRect(), c=el.getBoundingClientRect();
        if(r.left<c.left-0.5||r.top<c.top-0.5){ bad.push({num:mk.textContent, host:el.className}); }
        break;
      }
      el=el.parentElement;
    }
  });
  return bad.length?bad:'all markers clear';
})();
```

**4. Stale-string grep** — after any global change (a term removed, a value updated, a "待确认" resolved), grep the old
string and confirm **zero** leftovers. This is how you keep a large doc internally consistent: change a thing, then
prove the old thing is gone everywhere. Example: after descoping a platform, `grep -in 'rednote'` should return only the
intentional "not supported this version" lines, never a stray chip.

**5. Format gates — no `<pre>`, no Mermaid, no external URL.** All three must be hard zeros:

```bash
grep -c '<pre' prd.html                                   # must be 0
grep -ci 'mermaid' prd.html                               # must be 0
grep -oE '(src|href)="https?://[^"]*"' prd.html           # must be empty
grep -oE '@import[^;]*' prd.html                          # must be empty
grep -n '<html lang=' prd.html                            # must match the body language
```

A hit on the first two means a diagram was emitted in the wrong format — rebuild it as inline SVG or a `.flow` chain.
A hit on the URL greps means the file will render broken offline, in print, and after archiving. (`http://www.w3.org/2000/svg`
in an `xmlns` attribute is the one legitimate match — it is a namespace identifier, never fetched.)

## Editing hygiene for large HTML

- **Author block by block.** A full PRD runs 1,000–1,500 lines. Write the shell and the TOC first, then append one
  `.screen` block at a time, verifying as you go. Emitting the whole file in one shot is where tag imbalance and
  marker drift come from.
- **Renumber highest-first.** When you insert a marker and must shift 10→11, 11→12, …, edit the **highest** number
  first so an intermediate state never has two of the same number (which would break the unique-match your edit relies
  on). Anchor each edit on distinctive nearby text, not on the number alone.
- **The `file://` hard-cache trap.** The in-app browser caches `file://` aggressively; `location.reload()` can keep
  showing **stale** pre-edit content. The **disk is the source of truth** — trust `grep`/the Python check, not the
  browser, and tell the user to hard-reload (**Cmd+Shift+R**) to see changes. Never report the browser as correct when
  disk differs.
- **One source of truth per fact.** If a rule appears in many places, don't restate it — cite it by ID (see global rules
  in `iterating-a-live-product.md`). Then a change is one edit, not a search-and-replace across the doc.
