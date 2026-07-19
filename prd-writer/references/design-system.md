# Design system contract

Everything here is verbatim from the reference PRD and is **normative**: these are the tokens, classes, colours,
and fixed strings you use when authoring an annotated HTML PRD. Do not invent a parallel palette, rename a
class, or paraphrase a fixed label.

Read this file when you need the contract. Read `assets/annotated-html-prd-template.html` when you need a
worked HTML block to copy.

---

## 1. `:root` tokens — all 15, verbatim

```css
:root{
  --brand:#2a66e8; --brand-weak:#eef3ff; --ink:#1f2937; --ink-soft:#475569;
  --line:#e5e9f0; --bg:#f5f7fb; --card:#ffffff; --muted:#7a8698;
  --blue:#2a66e8; --teal:#0f9d8f; --purple:#7c5cd6; --orange:#e2802b; --red:#d84c4c; --green:#1f9d55;
  --radius:12px;
}
```

| Token | Carries |
|---|---|
| `--brand` | TOC h1, active TOC pill, `.screen-title` gradient start, `.mk`, `.nbadge`, `.flow .node` border, `.mtitle` bar, `.manchor/.mchip/.mtab.active`, `.btn.primary`, `a.inline` |
| `--brand-weak` | TOC hover, `.callout.info` bg, `.pill.brand` bg |
| `--ink` / `--ink-soft` | body text, `h5`, `.dialog .dt` / TOC link default, `.meta-table` labels, `.screen-desc` |
| `--line` | **every** 1px border in the shell |
| `--bg` / `--card` | `body` and `.mseg` bg / `.doc-head` bg |
| `--muted` | `.toc .ver`, `.doc-head .sub`, `.foot`, every small grey footnote `<p>`, inactive `.manchor/.mchip/.mtab` |
| `--blue` | **spec dimension ①** |
| `--teal` | **spec dimension ②** |
| `--purple` | **spec dimension ③**; `.mbtn.ai`; loading/generating SVG state |
| `--orange` | **spec dimension ④**; `.marker` circle; `.flow .node.warnn`; stale state; `.mtile.ocr` family |
| `--red` | `.cross`, `.marker.err`, `.tag.err`, `.pill.new`, `.btn.danger`, failed/revoked SVG |
| `--green` | `.tick`, `.tag.normal`, `.flow .node.term`, success/active SVG |
| `--radius` | `.doc-head` only; every other component hard-codes 8/9/10/12/14px |

> **`--blue`/`--teal`/`--purple`/`--orange` are bound 1:1 to spec dimensions ①②③④ and must NEVER be
> reassigned.** The reader learns the four colours once in the `.doc-head` 编写范式 row and then navigates the
> document by them; reassigning one silently breaks every page block below.

## 2. Non-tokenised palette — must ship too

| Hex | Role |
|---|---|
| `#132a56` | deep navy — `h2.sec`, `.doc-head .title`, `.callout b`, `.anno-title` bg, 3.2.5 banner gradient start |
| `#1b3a70` | `h3`, the inline-styled `3.2.x` `h4`, `.mtitle`, `.mc-val`, `.flow .node` text, SVG entity titles |
| `#33456b` / `#eff3fa` | `table.data th` text / bg |
| `#fafbfe` | `table.data tr:nth-child(even) td` zebra |
| `#eef1f6` | `<code>` bg, `.dialog` bg, `table.data td` bottom hairline |
| `#e9eef6` / `#dde4ef` | `.mock` canvas bg / border |
| `#d3ddec` | **all** avatar placeholders — `.mava`, `.mlb-av`, `.mtl-av`, `.dk-av` |
| `#8592a6` `#7a8698` `#64748b` `#54657f` `#c0c7d3` | grey ramp for mock labels, values, captions |
| `#94a3b8` | **every** SVG arrow `stroke` and every `marker-end` `fill` (20 of the gold's 23 stroked paths; the 3 exceptions are semantically-coloured E-R edges) |

---

## 3. Component inventory — all 128 class tokens

### Layout & chrome
| Class | Purpose | Nesting |
|---|---|---|
| `.layout` | flex shell, `max-width:1500px` | child of `<body>`; holds `.toc` + `.content` |
| `.toc` | sticky 270px sidebar, `height:100vh` | `<aside>` in `.layout` |
| `.ver` | product subtitle under the TOC `<h1>` | in `.toc` |
| `.grp` | non-link section divider (`一 · 概述`) | in `.toc`; **never** an `<a>` |
| `.lv2` / `.lv3` | TOC level 2 (the `3.2.x` tier) / level 3 (P-blocks) | on `.toc a`; bare `<a>` = level 1 |
| `.active` | current TOC entry (set by JS); also used by `.mtab/.mchip/.manchor/.mseg>span` | — |
| `.content` | main column, `padding:34px 46px 120px` | `<main>` in `.layout` |
| `.doc-head` `.title` `.sub` `.meta-table` | metadata card / 26px-800 title / version·date·status line / odd-even key→value grid | `<section id="info">`, first child of `.content`; `.meta-table` appears **only** here |
| `.foot` | closing grey footer note | last child of `.content` |

### Typography
| Class | Purpose | Nesting |
|---|---|---|
| `.sec` | top-level section, blue 2px rule above | `h2.sec`, child of `.content` |
| `.screen-title` | page-block header, brand gradient | `h4.screen-title`, **first** child of `.screen` |
| `.inline` | in-prose cross-reference link | `a.inline` |
| *(no class)* | `h3` = `N.N` sub-sections · `h5` = module / diagram sub-labels · `code` = identifiers and paths | — |

The `3.2.x` tier and the starred core section are **inline-styled `h4`s, not classes**:

```html
<h4 id="s321" style="font-size:15px;color:#1b3a70;margin-top:24px">3.2.1 实体关系图（E-R）</h4>
<h4 id="s325" style="font-size:16px;color:#fff;background:linear-gradient(90deg,#132a56,#2a66e8);padding:12px 18px;border-radius:10px;margin-top:34px">★ 3.2.5 需求、功能、交互说明（核心）</h4>
```
(`margin-top:24px` for the first `3.2.x`, `28px` for subsequent ones.)

### Tables
| Class | Purpose | Nesting |
|---|---|---|
| `.data` | every content table | `table.data`; **never** uses `<thead>`/`<tbody>` — the header row is just the first `<tr>` of `<th>`, which is what makes the `tr:nth-child(even)` zebra land right |
| `.c` `.tick` `.cross` | centre-align / green ✔ / red ✘ | on `td`; matrices use `class="c tick"`, `class="c cross"` |

Column widths go **inline on the `<th>`**: `<th style="width:110px">`, `<th style="width:33%">`.

### Callouts
| Class | Colour | Use |
|---|---|---|
| `.callout` + `.rule` | `#f2f9f6` / `#bfe6d6` green | non-negotiable engineering rule |
| `.callout` + `.warn` | `#fdf6ec` / `#f3d9a8` amber | trap, risk, dependency, placeholder caveat; often opens `<b>⚠ 依赖：</b>` |
| `.callout` + `.info` | `var(--brand-weak)` / `#c9dcfb` blue | framing, scope, positioning |

`.callout b` is `#132a56`.

### Pills
| Class | Value |
|---|---|
| `.pill` | base, `border-radius:999px` |
| `.brand` | `#eef3ff` / `#2a66e8` — neutral emphasis |
| `.nano` `.micro` `.mid` `.macro` `.mega` | five tiers: `#eef2f7/#64748b` · `#e4f0ff/#2a66e8` · `#e7e2fb/#6b4fc9` · `#efe3fb/#8b4fd0` · `#26314a/#fff` |
| `.m` / `.mir` | `#e4f0ff/#2a66e8` primary·master / `#fdeede/#c07a2a` mirrored·derived |
| `.new` | `#fde8e8` / `#d84c4c` — **the change-marker vocabulary**: 本版新增 / 本版改造 / 已明确 |

`.pill.new` sits inline right after the thing it annotates: `<td>Geo 筛选 <span class="pill new">本版新增</span></td>`

### Tags
| Class | Value | Nesting |
|---|---|---|
| `.tag` + `.normal` / `.err` | `#e8f5ee`/green · `#fde8e8`/red | **only** inside `ol.inter-list > li`, immediately after `.marker`; carries the literal word 正常 / 异常 |

### Screens
| Class | Purpose |
|---|---|
| `.screen` | one page block, `id="p0"…"pn"`, child of `.content` |
| `.screen-body` | padding wrapper; second child of `.screen` |
| `.screen-desc` | one-paragraph "where this lives" prose; `<p>`, first child of `.screen-body` |

Fixed child order in `.screen-body`: `.screen-desc` → 0..n `.anno-wrap` → `.spec field` → `.spec cond` →
`.spec state` → `.spec inter`. Omit a `.spec` only when the dimension has nothing to say; never reorder.

### Spec blocks
| Class | Dimension | Contains |
|---|---|---|
| `.spec` `.field` | ① blue | `.module` cards, or a `table.data` |
| `.spec` `.cond` | ② teal | **one** single-row 3-column `table.data` |
| `.spec` `.state` | ③ purple | a `table.data` + a `.diagram` SVG |
| `.spec` `.inter` | ④ orange | `ol.inter-list`, optionally `.dialog`s |
| `.spec-label` | the fixed pill label, white on the dimension colour | **first** child of `.spec` |
| `.module` | white card grouping one module inside ① | starts `<h5>M<n> · <name></h5>` |

### Interaction lists
| Class | Purpose |
|---|---|
| `.inter-list` | `ol.inter-list` inside `.spec.inter` |
| `.marker` / `.marker.err` | 26px orange circle, Arabic digit / red circle, literal `!` — **first** child of `li` |

```html
<li><span class="marker">1</span><span class="tag normal">正常</span>点击 <b>Report</b> Tab → 加载 Overview 页（P1）。</li>
<li><span class="marker err">!</span><span class="tag err">异常</span>无 <code>CAMPAIGN_REPORT</code> 权限 → Tab 不可见。</li>
```

All 正常 items first, then all 异常. `counter-reset:step` is declared but unused — numbers are hand-written so
the verifier can check them.

### Flow chains
| Class | Purpose |
|---|---|
| `.flow` | flex-wrap row of steps |
| `.node` / `.term` / `.warnn` | blue step `#eef3ff` · green terminal `#eef7f2` · amber branch·failure `#fdf3e7`; `<span>` in `.flow` |
| `.arw` / `.lbl` | the literal `→` glyph (or `/` for a branch), `#9aa6b8` 18px / small grey edge label `#8592a6` |

### Diagram
| Class | Purpose |
|---|---|
| `.diagram` | `overflow-x:auto` card, `#fbfcfe` bg, wrapping one `<svg>`; `.diagram svg{display:block}` |

Always follow with a grey caption: `<p style="font-size:12.5px;color:var(--muted)">实线 = …；虚线 = …。</p>`

### The triad
| Class | Purpose | Nesting |
|---|---|---|
| `.anno-wrap` | the whole triad card, `#fbfcff` | in `.screen-body`; children in order: `.anno-title`, `.mock`, legend `table.data` (`style="margin-top:14px"`), then **optionally** one trailing `.callout warn` |
| `.anno-title` | 🖼-prefixed navy label | first child of `.anno-wrap` |
| `.mock` | the grey `#e9eef6` device canvas | second child |
| `.anno` | `position:relative` **only** — the positioning context | an **extra** class on a mock element (`class="anno mcard"`) or a wrapping `<span class="anno">` |
| `.mk` | 22px brand marker at `left:-11px;top:-11px` | **first** child of its `.anno` |
| `.nbadge` | same badge, `inline-flex`, no shadow/ring | in `<td class="c">` of the legend |

**The provenance caveat is the fourth child, inside the card.** When any pixel in the mock is a placeholder
rather than specified behaviour, close the `.anno-wrap` with one `.callout warn` **after** the legend table and
**before** `</div>` — not outside the card, and never before the legend. This is what
`assets/annotated-html-prd-template.html` ships and it is the binding form: the caveat has to travel with the
mock it disclaims, because a reader who scrolls past the card must not be able to see the mock without it.
Exactly one such callout per `.anno-wrap`; fold every placeholder in that mock into it rather than emitting
several. Anywhere else in the document — inside a `.module`, between spec blocks — a `.callout warn` is an
ordinary sibling and this rule does not apply.

`.anno` combinations used in the gold: `anno mcard`, `anno mchips`, `anno mc-date`, `anno mmetric rate`,
`anno mock-side`, `anno mseg`, `anno mlb-val`, `anno mtc-meta`, `anno mtile`, `anno mtile ocr`, `anno drawer`,
`anno popcard`, `anno minichart`.

**Three marker overrides that are easy to lose — ship all of them:**

```css
td .mk{left:-8px;top:-8px;width:19px;height:19px;font-size:10.5px}
.mtc-meta .mk{left:6px;top:-14px}
.mseg>span:not(.mk){padding:4px 12px;border-radius:9px;font-size:11.5px;color:#7a8698}
```

The `:not(.mk)` guard is mandatory — without it a marker inside a segmented control renders as a segment.

### Mock primitives
| Class | Renders | Nesting |
|---|---|---|
| `.mock-row` | flex row of chrome elements | in `.mock` |
| `.mock-cols` `.mock-main` `.mock-side` | two-column body / main column / 148px right rail | `.mock-cols` holds the other two |
| `.manchor` `.manchor.active` | right-rail anchor nav item | in `.mock-side` |
| `.mtab` `.mtab.active` | pill sub-tab | in `.mock-row` |
| `.mbtn` `.mbtn.ai` | toolbar button; `.ai` purple `#7c5cd6` | in `.mock-row` |
| `.mtitle` | section title with a 4px blue left bar | in `.mock` / `.mock-main` |
| `.mcard-row` `.mcard` `.mc-label` `.mc-val` `.mc-date` | KPI card row / card / 11px label / 19px-800 value (`small` = suffix) / date-range chip | in that order |
| `.mchips` `.mchip` `.mchip.active` `.mchip.new` | filter chip group / chip | `.mchip` in `.mchips` |
| `.mgrid` `.mmetric` `.mmetric .l` `.mmetric .v` `.mmetric.rate` | 3-col grid / tile / label / value; `.rate` tints the value `#a99adf` | `.mmetric` in `.mgrid` |
| `.mtbl` (+ its `th`/`td`) `.mava` `.mhandle` | 11.5px data-grid mock / 22px avatar dot / `@handle` | `.mava`/`.mhandle` in `.mtbl td` |
| `.minfo` | ⓘ caliber-tooltip affordance — always literally `<span class="minfo">i</span>` | inline after a label; see the placement rule below |
| `.mseg` `.mseg>span` `.mseg>span.active` | segmented dimension switcher | spans in `.mseg` |
| `.mlb-row` `.mlb-av` `.mlb-crown` `.mlb-bar` `.mlb-fill` `.mlb-val` | leaderboard bar row | all in `.mlb-row`; `.mlb-crown` in `.mlb-av`; `.mlb-fill` in `.mlb-bar` |
| `.mbk` `.val` | tier breakdown matrix, centred cells, first column left on `#f9fbfe` | `table.mbk`; wrap in `<div style="overflow-x:auto">` when wide |
| `.mtl` `.mtl-node` `.mtl-av` `.mtl-date` | horizontal timeline, 104px, `min-width:520px` | `.mtl-node` absolutely positioned in `.mtl` |
| `.mtc-row` `.mtc-card` `.mtc-cover` `.mtc-ico` `.mtc-meta` | top-content card strip | nested in that order |
| `.metric-grid` `.mtile` `.mtile .l` `.mtile .v` `.mtile.ocr` | drawer metric tiles; `.ocr` = `#fff6ed`/`#f4dcc0`, label `#b5762a`, meaning OCR-sourced | `.mtile` in `.metric-grid` |
| `.minichart` `.mc-bars` `.mc-bars i` `.mc-bars i.cur` | 250px hover trend popover; bars `#9fd6ff`, current `#2a66e8` | `i` in `.mc-bars` in `.minichart` |

`.mlb-fill` background darkens down the ranking, hand-set inline: `#9ecbf3 → #6ba9e6 → #5a90d8 → #3f6fd0 → #1e3a8a`.

**When to use `.minfo` — it is a promise, not decoration.** A `.minfo` says *there is a caliber behind this
label and you are not allowed to guess it.* The gold pins one on **every** `.mtitle` of an author-designed
section mock (5 of 5) and on every derived-metric label (`CPM`/`CPV`/`CPE` in `.mc-label`). The rule:

- **Attach** it to a `.mtitle` whose section shows computed or snapshot-derived numbers, and to any
  `.mc-label` / `.mtile .l` / mock column header carrying a rate, ratio, or otherwise non-raw-count value.
- **Omit** it on a title that is a pure navigational landmark inside a Demo-traced full-page mock — the gold's
  two bare `.mtitle`s (`Overview`, `Performance`) are exactly this case: they name where you are, not what a
  number means.
- **Never** attach it to a raw count, a name, a date, or a status badge.

Every `.minfo` obliges a matching caliber statement — either the `逻辑 / 数据来源` cell of that element's
legend row, or its row in the ① field table. A `.minfo` with no formula written anywhere is the one defect no
script can catch and every engineer will file a question about.

### Overlays
| Class | Renders | Nesting |
|---|---|---|
| `.popcard` `.pc-head` `.pc-url` `.pc-cover` | 230px hover preview card | the `pc-*` in `.popcard` |
| `.drawer` `.drawer-head` `.drawer-body` `.dk-av` `.dcover` | 340px right-side detail drawer | `.dk-av`/`.dcover` in `.drawer-body` |
| `.dialog` `.dt` `.db` `.da` `.btn` `.ghost` `.primary` `.danger` | confirm dialog mock | `.dt` title → `.db` body → `.da` right-aligned row of `.btn`s |

Two `.dialog`s sit side by side (they are `inline-block`) directly under the ④ list when a flow has a double
confirm. Destructive confirms use `.btn.danger`.

Two rules are declared but unused in the gold — `.mchip.new` and `.flow .lbl`. Keep them. Conversely
`flow-arw` appears once as an inline-styled one-off with **no CSS rule**; it is not part of the system — use
`.arw`.

**The catalog is a starting point, not a ceiling.** When a screen needs a primitive that does not exist, add a
new `m*` class inline, following the same naming (`m` + short noun), the same palette, and the same
white-card-on-grey-canvas convention. Do not force a UI into a leaderboard because a leaderboard exists.

---

## 4. SVG diagram recipe

Every diagram is inline SVG inside `.diagram`. No Mermaid, no images, no `<pre>`.

```html
<div class="diagram">
<svg viewBox="0 0 640 150" width="640" height="150" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <defs><marker id="p1a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#94a3b8"/></marker></defs>
  <rect x="20" y="58" width="110" height="40" rx="8" fill="#faf5ff" stroke="#7c5cd6"/>
  <text x="75" y="83" text-anchor="middle" font-size="12.5" fill="#5a3fb0">loading 骨架</text>
  <path d="M130,72 L228,32" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
  <text x="180" y="45" font-size="10" fill="#8592a6">有快照</text>
</svg>
</div>
```

**Arrowhead, fixed:** `markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"`, path
`M0,0 L9,4.5 L0,9 z`, fill `#94a3b8`. **Unique marker id per SVG** (`er-a`, `p1a`, `p1b`, `p3a`) — ids are
document-global and a duplicate silently breaks the second diagram.

**Edges:** solid `stroke="#94a3b8"` = primary transition; `stroke-dasharray="4 3"` = return / retry / derived.
Edge labels are `<text font-size="10" fill="#8592a6">` placed manually beside the path.

**Boxes:** always `rx="8"`. Heights **34 / 38 / 40** for state nodes, **52 / 60** for E-R entities. Pastel fill
+ saturated stroke, matched to the state family:

| Family | fill | stroke | text |
|---|---|---|---|
| neutral / idle / empty | `#eef2f7` | `#64748b` | `#475569` |
| blue / in-progress / primary entity | `#eef3ff` | `#2a66e8` | `#1b3a70` |
| teal / awaiting-other-party / teal entity | `#f2f9f6` | `#0f9d8f` | `#166c3c` |
| purple / loading / generating | `#faf5ff` | `#7c5cd6` | `#5a3fb0` |
| success / active / terminal | `#eef7f2` | `#1f9d55` | `#166c3c` |
| error / failed / rejected / revoked | `#fdeae8` | `#d84c4c` | `#a83232` |
| warn / stale / expired / overdue | `#fdf6ec` (also `#fdeede`) | `#e2802b` | `#9a5b16` |

Node text is `font-size="12.5"` centred in the row's text colour.

### 4a. The business-state ramp — for enums with more than four states

Four families (neutral / success / error / warn) cover a UI state machine. They do **not** cover a business
enum: real workflows routinely run six or eight states, and the author is left picking a colour by feel. The
blue and teal families above — introduced by the gold for E-R entities — are hereby **also** sanctioned for
state nodes, and the seven families are assigned to lifecycle slots by one question:

> **Who holds the ball?**

| Slot | Holder | Family | Typical state |
|---|---|---|---|
| 1 | nobody yet — queued, unclaimed | **neutral** | 待接单 · unassigned · draft · queued |
| 2 | the actor who started it | **blue** | 进行中 · in progress · editing · assigned |
| 3 | a *different* party — review, approval, acceptance | **teal** | 待验收 · pending review · awaiting approval |
| 4 | a machine — generating, uploading, computing | **purple** | generating · uploading · syncing · loading |
| 5 | nobody — finished well (terminal) | **success** | 已验收 · approved · published · settled |
| 6 | nobody — finished badly, or bounced back | **error** | 已打回 · rejected · failed · revoked |
| 7 | the clock — no human acted and time degraded it | **warn** | 已逾期 · expired · stale · timed out |

Slots 5–7 are terminal or near-terminal; 1–4 are live. Read down the list and take the **first** slot that
fits — the order is the tie-break, so two authors converge. Worked example, the 6-state task enum that
motivated this rule:

| State | Slot | fill / stroke / text |
|---|---|---|
| 待接单 | 1 nobody yet | `#eef2f7` / `#64748b` / `#475569` |
| 进行中 | 2 the assignee | `#eef3ff` / `#2a66e8` / `#1b3a70` |
| 待验收 | 3 the reviewer | `#f2f9f6` / `#0f9d8f` / `#166c3c` |
| 已验收 | 5 terminal good | `#eef7f2` / `#1f9d55` / `#166c3c` |
| 已打回 | 6 bounced back | `#fdeae8` / `#d84c4c` / `#a83232` |
| 已逾期 | 7 the clock | `#fdf6ec` / `#e2802b` / `#9a5b16` |

Three traps:

- **Purple is for machines, not for waiting.** `待验收` is a person waiting on a person → teal, not purple.
  Reserve purple for a state a human cannot exit by acting.
- **Blue does not mean "entity" — and it does not mean "spec dimension ①" — inside a state diagram.** The
  `--blue`/`--teal` 1:1 binding to spec dimensions ①② in §1 governs `.spec-label` chrome, and the entity
  reading governs E-R diagrams. Neither is violated here: a state node lives inside a `.spec.state` block that
  is already labelled ③ purple, an E-R diagram never contains state nodes, and no SVG node ever carries a
  circled numeral. The three readings never share a surface. This is the only place the hexes do double duty —
  do not extend the pattern anywhere else.
- **Do not introduce an eighth hue.** If an enum needs more than seven, two of its states are the same slot at
  different granularity — merge them in the diagram and split them in the ③ table, which has rows, not colours.
  Every hex above is already in the gold; grep before you type a new one.

### 4b. Coordinate grid — mandatory for state machines with more than four nodes

Up to four nodes, place boxes by eye against the gold's own small diagrams. Beyond four, hand-solving the
layout produces crossed edges and arithmetic-verified curves. Use the grid.

**Columns** — a node's column index `n` is its distance in transitions from the initial state:

```
x = 30 + 200·n        box width 130   (→ a constant 70px gutter, the gold's own state-node gutter)
```

**Ranks** — three fixed `y` values, chosen by *what causes* the transition into that node, not by mood:

| Rank | `y` | height | Holds |
|---|---|---|---|
| ↑ above | `30` | 40 | branch outcomes a **user** chose: rejection, cancel, alternate terminal |
| → main | `130` | 40 | the happy path, strictly left→right, one node per column |
| ↓ below | `250` | 40 | **auto / system** transitions: timeout, expiry, scheduled job, retry sink |

```
viewBox = "0 0 W 320"    W = 200·N − 10        (N = number of columns)
```
`W` is `30 + 200(N−1) + 130 + 30`: left margin 30, `N` columns, right margin 30. N=4 → 790, N=5 → 990,
N=6 → 1190. `.diagram` is `overflow-x:auto`, so a wide machine scrolls rather than shrinking its type.

**Why auto-transitions get their own rank:** an expiry or timeout edge fires from *several* happy-path states
into *one* sink. Left on the main rank, those edges pass straight through intervening boxes. On rank ↓ every
one of them is a clean diagonal.

**Edge routing, in order of preference:**

1. **Adjacent, same rank** — horizontal: `M {x+130},{y+20} L {x_next−4},{y+20}`. The `−4` leaves room for the
   arrowhead; the gold uses a 2–4px standoff everywhere.
2. **Rank change, adjacent column** — straight diagonal from the source's right edge to the target's left
   edge, offsetting the source `y` by ±8 so multiple edges leaving one box fan out instead of overlapping
   (the gold does exactly this: `L228,32` / `L228,78` / `L228,122` from one box).
3. **Backward or column-skipping** — cubic `C`, **dashed** (`stroke-dasharray="4 3"`), bulging *away* from the
   ranks so it never crosses a box. Anchor it on a box edge at both ends and keep both control points outside
   the `y` band of every box it passes.

Only rule 3 needs arithmetic; rules 1 and 2 are pure substitution. If you find yourself verifying a straight
edge by arithmetic, it is on the wrong rank.

**Worked example — 6 nodes, 4 columns, 8 edges** (the enum from §4a; `viewBox="0 0 790 320"`):

| Node | col `n` | rank | `x` | `y` |
|---|---|---|---|---|
| 待接单 | 0 | → | 30 | 130 |
| 进行中 | 1 | → | 230 | 130 |
| 待验收 | 2 | → | 430 | 130 |
| 已验收 | 3 | → | 630 | 130 |
| 已打回 | 2 | ↑ | 430 | 30 |
| 已逾期 | — | ↓ | 330 | 250 |

`已逾期` is a sink fed by three different columns, so it is not on the column grid — centre it under the span
of its sources (here midway between columns 1 and 2). Sinks are the one sanctioned exception to `x = 30+200n`.

```html
<!-- rule 1: happy path, three horizontals -->
<path d="M160,150 L226,150" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<path d="M360,150 L426,150" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<path d="M560,150 L626,150" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<!-- rule 2: 待验收 → 已打回, one column up -->
<path d="M495,128 L495,74" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<!-- rule 2: three sources → the 已逾期 sink on rank ↓ -->
<path d="M100,172 L328,246" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<path d="M290,172 L372,246" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<path d="M470,172 L426,246" stroke="#94a3b8" fill="none" marker-end="url(#p1a)"/>
<!-- rule 3: 已打回 → 进行中, backward, dashed, bulging left through the empty band above rank → -->
<path d="M428,50 C370,50 300,78 295,124" stroke="#94a3b8" fill="none" stroke-dasharray="4 3" marker-end="url(#p1a)"/>
```

Every horizontal here is `y = 130 + 20 = 150` and every column boundary is `30 + 200n ± 4` — verifiable by
reading, which is the whole point of fixing the grid. E-R entity boxes carry two `<text>` lines —
title `font-size="13" font-weight="700" fill="#1b3a70"`, sub-caption `font-size="11" fill="#64748b"`.
Cardinality labels are `text-anchor="middle" font-size="10.5" fill="#8592a6"` reading `1:N` / `N:1`.

**Mandatory:** a grey caption `<p>` after every diagram stating what solid vs dashed means in *that* diagram.

---

## 5. The three numbering systems — never mix them

| System | Glyphs | Where | Rule |
|---|---|---|---|
| **Triad markers** | plain Arabic `1…n` | `.mk` in a `.mock`, `.nbadge` in its legend | Restart at `1` in **every** `.anno-wrap`. Ascending, no gaps, no duplicates. Laid out in **visual reading order** (top-left first, then down and right), not DOM order. Every `.mk` has exactly one `.nbadge` row and vice versa. |
| **Spec dimensions** | circled `①②③④` (`⑤⑥` in flows) | the four `.spec-label` strings; `.flow .node` text in use-case chains; inline prose in `.doc-head`/`.callout info` naming the dimensions | Never on a mock marker. Never in an interaction list. |
| **Interaction markers** | Arabic for 正常, literal `!` for 异常 | `.marker` / `.marker.err` in `ol.inter-list` | 正常 numbered `1, 2, 3…` in orange. **Every** 异常 item carries `!` in red — abnormal items are never numbered. All 正常 first, then all 异常. |

Mixing these — `⑴⑵⑶` alongside `①②③` in one diagram, or circled numerals on mock markers — is the single most
common failure. If you need a fourth kind of pointer, use a letter and give it a legend.

---

## 6. Fixed strings — never paraphrase

Emit these in the **document's language** (see *Language* in `SKILL.md`). Both forms are given so either
language renders consistently; do not invent a third wording.

> **This section is the single source of truth for these strings.** No other file in the skill restates them —
> `annotated-html-mockups.md`, `document-outline.md`, and `function-interaction-spec.md` all point here. If you
> are about to type a spec label or a legend header, copy it from the tables below, byte for byte.

### The four spec labels — order ①→②→③→④ never varies

| Class | Chinese | English |
|---|---|---|
| `.spec.field` | `① 字段、字段说明、数据来源` | `① Fields, description, data source` |
| `.spec.cond` | `② 前置条件、排序机制、刷新机制` | `② Preconditions, sorting, refresh` |
| `.spec.state` | `③ 状态流转` | `③ State transitions` |
| `.spec.inter` | `④ 交互操作（正常 + 异常）` | `④ Interactions (normal + abnormal)` |

Two sanctioned short forms when a page's ④ is trivial: `④ 交互` / `④ Interactions`, and `④ 交互 / 状态` /
`④ Interactions / states`.

### Legend table headers — first column is always `width:52px`

```html
<tr><th style="width:52px">标号</th><th style="width:190px">含义（元素）</th><th style="width:33%">交互</th><th>逻辑 / 数据来源</th></tr>
```

| Slot | Chinese | English | Width |
|---|---|---|---|
| 1 | `标号` | `No.` | **`52px`, always** |
| 2 | `含义（元素）` | `Element` | `150px` / `170px` / `190px` / `200px` |
| 3 | `交互` | `Interaction` | `28%` or `33%` |
| 4 | `逻辑 / 数据来源` | `Logic / data source` | unset |

The fourth header is `逻辑 / 数据来源`, with spaces around the slash — not `逻辑·数据来源`.

### `.anno-title` prefix — encodes provenance

Always starts with `🖼 `.

| Form | Meaning |
|---|---|
| `🖼 Demo 功能标注 · …` / `🖼 Demo annotations · …` | traced from a **stakeholder's demo or drawing** |
| `🖼 功能标注 · …` / `🖼 Annotations · …` | **designed by the PRD author** |

This is load-bearing: it tells engineers which pixels are a commitment and which are the author's proposal.
Never collapse the two. Where a mock element is a placeholder rather than specified behaviour, add a
`.callout warn` saying so. Optional trailing anchor slug:
`<code style="margin-left:8px;font-size:11px">#…overview-timeline</code>`.

### Interaction-list tags

`正常` / `Normal` on `.tag.normal`; `异常` / `Error` on `.tag.err`. The literal word, nothing else.

---

## 7. Required JavaScript — exactly one block

One ES5 IIFE, the TOC scroll-spy. There is **no other JS in the document** — no tab logic, no collapsibles, no
theme toggle. Smooth scrolling is CSS (`html{scroll-behavior:smooth}`), not JS.

```html
<script>
  // TOC 滚动高亮
  (function(){
    var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
    var map = {};
    links.forEach(function(a){
      var id = a.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if(el) map[id] = a;
    });
    var targets = Object.keys(map).map(function(id){return document.getElementById(id);});
    var obs = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){
          links.forEach(function(l){l.classList.remove('active');});
          var a = map[e.target.id];
          if(a){a.classList.add('active');
            a.scrollIntoView({block:'nearest'});
          }
        }
      });
    },{rootMargin:'-10% 0px -80% 0px',threshold:0});
    targets.forEach(function(t){obs.observe(t);});
  })();
</script>
```

`rootMargin:'-10% 0px -80% 0px'` is the scroll-spy band — an element becomes "current" when it enters the
10%–20% viewport strip. `a.scrollIntoView({block:'nearest'})` keeps the active entry visible in the sidebar's
own scroll container. Keep ES5 syntax (`var`, `function`, `Array.prototype.slice.call`).

## 8. Media queries — exactly two

```css
@media(max-width:980px){
  .toc{display:none}.content{padding:22px}
}
@media print{
  .toc{display:none}.content{padding:0}.screen{break-inside:avoid}
}
```

That is the entirety of the responsive and print styling — no `@page`, no colour-adjust, no page-break-before.
`break-inside:avoid` on `.screen` is what keeps a page block from splitting across printed pages; do not drop it.

## 9. Font stack — always includes CJK

```css
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
```

Keep the three CJK faces **regardless of the document's language**. They cost nothing in an English document
and are the difference between a readable and an unreadable Chinese one. Code uses
`"SF Mono",Menlo,Consolas,monospace`. No `@font-face`, no remote font — a PRD must render from `file://` with
no network.
