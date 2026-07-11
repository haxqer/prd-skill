# Annotated HTML Mockups — put the numbered wireframe *inside* the doc

> This is the concrete method for **section 3.2.6 "Page annotations"** when you want the annotated mockup to live
> **inside** the PRD itself, not as a link to an external Figma/wireframe. It pairs a pixel-faithful HTML/CSS
> recreation of a screen with numbered callout markers, and an explanation table keyed to those numbers — so the
> picture and the spec sit together and can never drift apart.
>
> The rest of the skill is **Markdown-first** (author in Markdown, render with `scripts/prd_to_html.py`). This file
> describes the second authoring mode: a **hand-authored, self-contained HTML PRD**. Read *When to use which mode*
> first — most PRDs do **not** need this.

---

## When to use which mode

| | Markdown + `prd_to_html.py` (default) | Hand-authored annotated HTML (this file) |
|---|---|---|
| Reach for it when | Almost every PRD. Structure, tables, E-R / flow / state via Mermaid. | The spec **hinges on high-fidelity UI** with numbered callouts that Mermaid can't express; stakeholders communicate via **redrawn demos / screenshots** you are mirroring; the HTML *is* the final read/share/print artifact. |
| Mockups | Reference an external wireframe by page number (P-01). | Recreate the screen in HTML/CSS and pin numbered markers on it, in-doc. |
| Editing | Edit Markdown, re-render. | Edit HTML directly; verify by hand (see *Verification*). |
| Cost | Low. | Higher — you are hand-building UI. Only pay it when fidelity earns it. |

The two combine: you can embed an annotated-mockup HTML block inside an otherwise Markdown PRD, as long as the page's
`<style>` includes the classes below. But the clean path for a fidelity-heavy PRD is a single self-contained HTML file.
Start from `assets/annotated-html-prd-template.html` — it ships the whole design system plus one worked example of every
component named here.

## The core device: the annotated-mockup triad

Every annotated screen is three coupled pieces. Keep them adjacent and keep their numbers in lockstep.

1. **A titled container** — `.anno-wrap` wrapping a `.mock` "screen" that holds a faithful HTML/CSS recreation of the UI.
2. **Numbered markers pinned on elements** — each callout is `<span class="anno"><span class="mk">N</span>…element…</span>`.
3. **An explanation table keyed to the markers** — a `table.data` whose first column is `<span class="nbadge">N</span>`,
   one row per marker, columns: `标号 / 含义（元素） / 交互 / 逻辑·数据来源` (Number / Meaning / Interaction / Logic·Data source).

Marker `N` on the mockup ↔ row `N` in the table, **one-to-one and continuous**. That correspondence is the whole point:
a reviewer reads a number off the picture and finds its full spec in the row, and vice-versa.

```html
<div class="anno-wrap">
  <span class="anno-title">🖼 Annotation · Overview page <code>#overview</code></span>
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
</div>

<table class="data">
  <tr><th style="width:52px">标号</th><th style="width:190px">含义（元素）</th><th style="width:33%">交互</th><th>逻辑 / 数据来源</th></tr>
  <tr><td class="c"><span class="nbadge">1</span></td><td>子 Tab 切换器</td><td>点击切换两大视图，当前项高亮</td><td>默认进 Overview；前端路由，无数据依赖</td></tr>
  <tr><td class="c"><span class="nbadge">2</span></td><td>Share 按钮</td><td>点击 → 打开分享弹窗</td><td>无快照时禁用；后端 <code>crypto/rand</code> token</td></tr>
  <tr><td class="c"><span class="nbadge">3</span></td><td>平台筛选 chip（单选）</td><td>点某 chip → 指标卡按该平台重取</td><td>All = 全平台汇总；平台归一 <code>LOWER(TRIM)</code></td></tr>
</table>
```

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

- **Faithful to a stakeholder demo / live screenshot** — say so in the `.anno-title` or a `.screen-desc` line
  ("以下 5 块据线上已实现 UI 补齐" / "Demo 仅画到 Performance").
- **Placeholder values** — when you show sample numbers, state it once ("Demo 的 N/A 是占位；正式版空值按 G8 显示
  '—'"). Never let a made-up figure read as a real metric.
- **A number's real source lives in the table's 数据来源 column**, not on the picture. The picture shows *shape*; the
  row shows *truth*.

**Decision-driven, not demo-driven.** The mockup mirrors what will be **built**, not literally what a stakeholder drew.
When a later decision contradicts the demo (a platform is descoped, a control is deferred), **remove it from the
buildable mockup** and record the deferral in the open-questions table (see `iterating-a-live-product.md`) — do not
leave a control on the picture that engineering is not meant to build.

## Component & CSS catalog

The template's `<style>` block is a small, proven design system. Copy it wholesale; don't reinvent it. Classes you will
reach for:

**Layout & chrome**
- `.layout` = sticky `.toc` sidebar + `.content`. `.toc a.active` highlights the current section (scroll-spy script in
  the template). `h2.sec`, `h3`, `h5` are the heading rhythm.
- `.doc-head` + `.meta-table` = the title block (title / owner / version / date).
- `table.data` = every spec table; `td.c` centers; `.tick` (✔) / `.cross` (✘) for matrices.

**Callouts & tags**
- `.callout.info` (blue, context) / `.callout.rule` (green, a binding rule) / `.callout.warn` (amber, a caveat).
- `.pill` variants: `.brand`, `.new` (red "changed/新增"), tier pills `.nano/.micro/.mid/.macro/.mega`, `.m`/`.mir`
  (master/mirrored). Use `.pill.new` to flag what changed in this version.

**The four-dimension spec block** (mirror of the Markdown four dimensions, color-coded)
- `.spec.field` (blue) / `.spec.cond` (teal) / `.spec.state` (purple) / `.spec.inter` (orange), each opened by a
  `.spec-label` chip: `① 字段/数据来源`, `② 前置·排序·刷新`, `③ 状态流转`, `④ 交互（正常+异常）`.
- Interactions use `ol.inter-list > li` with a `.marker` (orange, `.err` = red for abnormal) and a `.tag.normal` /
  `.tag.err` label, so happy-path and error rows are visually distinct on the same list.

**Flow (when Mermaid is overkill)**
- `.flow > .node` (`.term` = green terminal, `.warnn` = amber) joined by `.arw` arrows — a one-line horizontal flow for
  a use-case sequence.

**Mockup primitives** (build the fake UI out of these)
- Cards/metrics: `.mcard`/`.mc-label`/`.mc-val`, `.mgrid`/`.mmetric`. Chips: `.mchip(.active/.new)`. Tabs:
  `.mtab(.active)`, buttons `.mbtn(.ai)`. Tables: `.mtbl`, breakdown `.mbk`. Side nav: `.mock-side`/`.manchor`.
- Overlays: `.drawer` (right side-sheet), `.popcard` (hover preview), `.minichart` (mini bar chart), `.dialog`
  (confirm modal). Metric tiles `.mtile`, `.mtile.ocr` (amber = sourced from image/OCR, not collection).

You do not need to memorize these — open the template, find the component that looks closest, copy its block, and
relabel. The catalog exists so you reuse the proven markup instead of hand-rolling new CSS per PRD.

## Verification (hand-authored HTML has no compiler — you are it)

After **every** batch of edits, run these four checks. They are cheap and they catch the failure modes that a
hand-edited 100 KB HTML file actually hits.

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
no gaps or dupes. Grep the counts per screen and eyeball the sequence; a missing or doubled number means the picture and
the spec have drifted.

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

## Editing hygiene for large HTML

- **Renumber highest-first.** When you insert a marker and must shift 10→11, 11→12, …, edit the **highest** number
  first so an intermediate state never has two of the same number (which would break the unique-match your edit relies
  on). Anchor each edit on distinctive nearby text, not on the number alone.
- **The `file://` hard-cache trap.** The in-app browser caches `file://` aggressively; `location.reload()` can keep
  showing **stale** pre-edit content. The **disk is the source of truth** — trust `grep`/the Python check, not the
  browser, and tell the user to hard-reload (**Cmd+Shift+R**) to see changes. Never report the browser as correct when
  disk differs.
- **One source of truth per fact.** If a rule appears in many places, don't restate it — cite it (see global rules by
  ID in `iterating-a-live-product.md`). Then a change is one edit, not a search-and-replace across the doc.
</content>
</invoke>
