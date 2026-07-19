---
name: prd-writer
description: >
  Write a Product Requirements Document (PRD) that engineers actually love to read. Use this skill whenever the user
  needs to write a PRD, a requirements document, a product spec, a functional spec, or wants to turn a product idea or
  feature into a document that can be handed straight to engineering — even if they never say the letters "PRD". Intents
  like "write up this requirement for the dev team", "put together a spec", "document this feature for engineers",
  "write a requirements doc", "写一份 PRD", "写需求文档", "整理成产品需求文档", "把这个需求写给研发", "功能说明文档",
  or "产品设计文档" should all trigger it. The skill provides a battle-tested PRD structure and writing style that
  minimizes back-and-forth with engineers and is ready for estimation and development (Product intro / Industry
  overview / Version: schedule, product design, non-functional requirements, change log), with emphasis on the details
  engineers actually care about: E-R diagrams, role-permission matrices, layered flowcharts, global states, and
  field-level + interaction specs. Produces a self-contained annotated HTML PRD, written in the user's own language.
---

# PRD Writer — Write a Requirements Doc Engineers Love

Whether a PRD is good is not measured by how many words you wrote. It is measured by whether an engineer, after reading it, can start building with **fewer questions, less guessing, and less rework**. This skill turns that standard into a reusable structure, a writing style, and a document format.

## Core philosophy: write from the engineer's point of view

A PRD usually fails not because it says too little, but because it says things engineers can't use — or leaves out exactly the part they need. Engineers have three real pain points; keep them in view the whole time you write:

1. **The doc gets shelved** — too long, no clear focus, tiring to read, so engineers just stop opening it.
   → Fix: clear, layered structure; carry information in tables, mockups, and diagrams so anything can be located in seconds.
2. **Endless back-and-forth to confirm requirements and edge cases** — the logic has gaps, so engineers have to keep asking.
   → Fix: spell out exceptions, boundaries, state transitions, and data sources up front so the doc answers questions on its own.
3. **What ships is a mess** — vague descriptions and loose logic, discovered only in QA.
   → Fix: describe things precisely at the field and state level; cover both the happy path and the error paths.

**The self-check question for any chunk of a requirement:** if I were the engineer, would I still need to come back and ask me something after reading this? If yes, write in the answer to that question.

## Workflow

Given a requirement or product idea, proceed in this order:

1. **Clarify before writing.** Fill in these facts:
   - What product / feature is this? Who uses it (target users, roles)? What problem does it solve?
   - Is it B2B (internal / back-office) or B2C? A brand-new product, or a feature/iteration on an existing one?
   - What roles and permissions are involved? Are there data entities (does it need an E-R diagram)?
   - Any known performance, compatibility, or analytics (event-tracking) requirements?

   **Ask, or default? Apply this split — never invent silently, and never treat §五 as a way to avoid asking.**

   | Must ASK the user — stop and ask, do not default | May DEFAULT into §五 待确认项 |
   |---|---|
   | Entities, their fields, and their relationships (anything that changes the E-R diagram) | Numeric knobs: intervals, timeouts, page sizes, length/character caps, thresholds, TTLs |
   | Roles, and who can do what (anything that changes the permission matrix) | Sort orders, default filter values, retention windows |
   | Scope: which pages/screens are in this version, and what is explicitly out | Names of tables, enums, permission codes, endpoints, and other identifiers |
   | Whether this is a new product or an iteration, and what shipped already | On-screen copy, empty-state wording, toast text |

   The test: **would guessing wrong force a schema change, a migration, or a re-architecture?** Then ask. Would it be a one-line constant change? Then commit a default, file it as a §五 row, and say so at handoff. A `.md` full of confidently-invented permission codes and table names is the failure this rule exists to stop.
2. **Pick the structure and trim it.** Use the *PRD Structure* below as the skeleton, but **don't apply it blindly** — see "Tailoring by scenario".
3. **Fill in section by section.** Put the most polish into the flowcharts, global states, and function-and-interaction specs inside "Product design" — those decide the engineering experience.
4. **Author the PRD as a single self-contained HTML file.** This is the default deliverable, not an upgrade. Start from `assets/annotated-html-prd-template.html`, which ships the design system, and follow `references/annotated-html-mockups.md` and `references/design-system.md`. One `.html` file, no external requests — every diagram is inline SVG or CSS, every mockup is a pure-CSS recreation of the screen with numbered markers pinned to its elements. Author it `.screen` block by `.screen` block and append, rather than emitting the whole file in one shot. If the user explicitly asks for Markdown, or the change is a one-screen tweak with no UI surface, see *Alternative: lightweight Markdown PRDs* at the end of this file.
5. **Run the quality self-check** against the document you just wrote, and plug every question an engineer would come back to ask.
6. **Run the verification pass last.** `python3 scripts/verify_prd_html.py path/to/prd.html` must exit clean before you hand the file over. Fix and re-run until it does.

## The default format: a self-contained annotated HTML PRD

**Write the PRD as HTML by default.** A PRD's hardest job is making a screen unambiguous, and prose cannot do it — the reader has to see the screen, see a number pinned on the element being specified, and find that number in a table one scroll away. That is the **annotated-mockup triad**: a recreated screen (`.mock`) + numbered markers (`.mk`) + an explanation table keyed one-to-one to them (`.nbadge`). Every page that has a UI gets one.

**Never substitute ASCII box-drawing, a screenshot link, or a Mermaid diagram for a mockup.** ASCII art does not reflow, cannot be searched, cannot show an active tab or a disabled button, and makes marker↔table continuity unverifiable. If you find yourself drawing `┌───┐`, you are in the wrong format — open the template and copy the closest component.

**No external requests.** The HTML file is the artifact people read, share, print, and archive. It must render identically from a `file://` URL on a machine with no network. That rules out CDN scripts (including Mermaid), remote fonts, and remote images. Diagrams are inline SVG; flows are `.flow` chains of styled `<span>`s; screens are CSS.

The shell is fixed: a sticky 270px `.toc` sidebar (3 levels, non-link `.grp` dividers) + `.content` column + `.doc-head` metadata card + `.foot`, plus one ES5 IntersectionObserver scroll-spy and nothing else. Tokens, the component inventory, the SVG state-colour table, and the three numbering systems live in `references/design-system.md`.

Markdown remains available for lightweight cases, and only those: the user asked for Markdown, or the spec is a single-screen change with no UI to annotate.

## Language

**Write in the user's language.** A PRD written in a language the engineering team does not read every day is a PRD that gets shelved, which is the exact failure this skill exists to prevent.

Decide the language in this order, taking the first that applies:

1. **The user said so.** An explicit instruction ("写成中文", "in English") wins over everything below.
2. **Existing PRDs in the repo.** Before writing, glob the output directory and its siblings for prior specs — e.g. `ls` the target directory, then `grep -l` or glob for `*prd*.html`, `*prd*.md`, `*spec*.md`, or a `prd/` or `docs/` directory in the repo root. If you find one, open it and match its prose language. This is one or two tool calls; spend them.
3. **No corpus, or the corpus disagrees with itself?** Use the language the user wrote their request in. Do not deliberate further, and never fall back to English by default.

Set `<html lang="…">` to match the body. When writing Chinese, use `lang="zh-CN"`; **always** keep `"PingFang SC","Hiragino Sans GB","Microsoft YaHei"` in the font stack regardless of document language, so CJK product names and quoted UI strings render correctly. Keep product names, metric names, entity names, and code identifiers in their original English; only the connective prose is translated. The design system's fixed strings — the four spec labels, the legend table headers — follow the document's language and are given in both Chinese and English in `references/design-system.md`; pick one language and never mix them within a document.

## PRD Structure

The canonical outline. Top levels use Chinese numerals (`一、二、三`) or their equivalent in the document's language; second level is `N.N `, third `3.2.N`. Sections marked **[EXT]** are mandatory only when their trigger applies. Full contract — anchor ids, TOC rules, fixed table schemas — in `references/document-outline.md`.

```
文档信息 / Doc info            #info   .doc-head + .meta-table + .callout info「本版定位：」
一、产品简介                   #s1
  1.1 产品定位                         prose ¶ + 3-row table 我是谁 / 有什么用 / 为什么用
  1.2 目标用户与角色                    table 角色 / 场景 / 诉求
  1.3 核心使用场景                      .flow chain, ①…⑥ in the node text
  1.4 名词解释 / Glossary      [EXT]   table 术语 / 含义
二、行业与业务背景              #s2     table 痛点 / 表现 / 本产品对策
三、版本管理                   #s3
  3.1 排期表                   #s31b   table 阶段 / 模块 / 内容 / 依赖
  3.2 产品设计                 #s32    ← the doc's centre of gravity
    3.2.1 实体关系图（E-R）     #s321   inline SVG
    3.2.2 用户角色权限表        #s322   table.data role × capability, .tick / .cross
    3.2.3 业务流程图            #s323   layered, or split by actor
    3.2.4 全局说明             #s324   A. 全局口径规则 G1…Gn · B. 分层/枚举 · C. 通用控件规范
  ★ 3.2.5 需求、功能、交互说明  #s325   banner-styled; P0…Pn blocks below
  3.3 非功能需求               #s33    埋点 / 性能 / 兼容性 / 安全 / 一致性 / 可观测性 / 测试
  3.4 修改记录                 #s34    table 版本 / 日期 / 说明
四、本版变更点            [EXT] #s4     C1…Cn table 现状 / 本版 / 影响面
五、待确认项              [EXT] #s5     table # / 问题 / 默认取值
附录 A / B · <名称>       [EXT] #sb #sc e.g. 接口字段白名单、指标口径字典
```

### 1. Product intro
Make anyone understand the product in 30 seconds. Answer three questions: **who am I** (identity/positioning), **what am I good for** (what it does, what problem it solves), **why choose us** (differentiators). Then one line on **target users** and the **core use scenario**. Facts, not marketing copy.

- **1.4 名词解释 / Glossary [EXT]** — a `术语 / 含义` table. Mandatory whenever the domain has vocabulary collisions or the DB name differs from the UI name (e.g. `Saves` is stored as `Collects`). Without it, every table re-triggers the same question.

### 2. Industry overview
Industry state, trends, competitors — but reframe it as **design justification**: a `痛点 / 表现 / 本产品对策` table beats three paragraphs of market prose.
> **Trim tip:** iterations, internal tools, and single-feature requests usually don't need this — delete the whole section.

### 3. Version
A version corresponds to one shippable scope of development. Label the version number (e.g. v1.2). It contains four parts:

#### 3.1 Schedule
A `阶段 / 模块 / 内容 / 依赖` table confirmed together with engineering. The **依赖** column is what stops a phase silently blocking on another team. Head it with a note that dates are proposals pending engineering estimation. Treat it as a **live tracking surface**, not a static status column: engineers open their own module, see the daily tasks, and mark modules complete as they land — that is what keeps the project from falling behind and blowing up mid-way.

#### 3.2 Product design (the heart of the PRD, and where "engineers love it" is won)
The **function & interaction spec** below is the most detailed part of a PRD and has its own exhaustive deep-dive in `references/function-interaction-spec.md`. Key points:

- **Entity-Relationship (E-R) diagram**: whenever data is persisted, lead with an E-R diagram showing entities and their attribute fields. Database engineers can design the table schema straight from it. Draw it as **inline SVG** — solid edges for business entities, dashed for derived ones, cardinality labels (`1:N`, `N:1`) on every edge.
- **Role-permission matrix**: any time multiple roles/permissions are involved, build a full "role × function/data" matrix as a `table.data` with `.tick`/`.cross` cells and qualifiers in the cell text. Permissions scattered through the prose are the easiest source of bugs.
- **Flowcharts, decomposed layer by layer**: **business flow** (overall logic) → **task flow** (how one task runs) → **page flow** (how pages transition). Splitting by **actor** instead (system-automated pipeline vs. user-operated flow) is equally acceptable — state which decomposition you used. Build them as `.flow` chains, not Mermaid.
- **Global spec**: define shared controls and shared states (empty data, loading, load-failed, network error, no-permission, button loading/disabled, divide-by-zero, data freshness) **once**. Give every recurring calibration rule an **ID** (`G1…Gn`) and cite it inline everywhere as `（G7）` — change the rule once, every citation follows. This is the key trick for keeping a PRD concise and non-self-contradicting.
- **Function & interaction spec**: describe each page/module, and write every one across **four dimensions** (this is the core of stopping the back-and-forth). Order ①→②→③→④ never varies; each renders as a coloured `.spec` block. The headings below name each dimension — the exact `.spec-label` text to emit is a fixed string, written down only in *Fixed strings* in `references/design-system.md`.
  1. **Fields, description, data source** — for each field: what it is, its type/format/length/enum and display rules, and where the value comes from (System-determined / Backend / API endpoint→field / Computed / User input). Format: `| 字段 | 说明 | 数据来源 |`. Group fields into `.module` cards numbered `M1…Mn` when a page has several distinct blocks.
  2. **Preconditions, logic, sorting, and refresh** — what must hold to enter this page; **input validation rules and boundary conditions** (whitelists, length/format limits, what happens at zero/one/max, what an out-of-range value does); how the list is sorted; what resets on a filter change; how it first-loads, paginates, and refreshes. Format: a single-row three-column table `| 前置条件 | 排序机制 | 刷新机制 |`, each cell a `<br>`-separated numbered list. This dimension is about **logic**, not just loading mechanics — validation and edge cases live here, not buried in the error paths of dimension ④.
  3. **State transitions** — how a page or object moves between states under different conditions. A page usually has several states, and each one needs saying. Format: `| From | Trigger / condition | To |`, plus an **inline SVG** state diagram (recipe in `references/annotated-html-mockups.md` — pastel fill + saturated stroke per the state-colour table, solid edges for transitions, dashed for retry/derived).
  4. **Interactions: normal + abnormal** — an `ol.inter-list` where each item is `.marker` + `.tag` + prose: tap/act on each element → result, including confirm dialogs and their branches (e.g. "Cancel order" → confirm dialog → Confirm / Don't cancel yet). Cover the happy path **and** the error paths (invalid input, network failure, empty data, over-limit, no-permission, concurrency conflicts). All 正常 items first, numbered; then all 异常 items, every one carrying a literal `!` in red. Error branches are the most often forgotten and the most bug-prone — they must be written.

  > **This is the single most important and most detailed part of the PRD.** Do not summarize it — spec it. For the exhaustive method — how to fill every column of the canonical field / interaction / state / analytics tables, the full abnormal-path taxonomy, per-component interaction conventions, gestures & keyboard, optimistic UI, permissions and analytics per action, and a fully worked max-detail example — follow `references/function-interaction-spec.md` closely.
- **Annotated mockups**: every page gets a number (`P0`, `P1`, `P2.1`) and a **pixel-faithful in-document recreation** — the annotated-mockup triad in `references/annotated-html-mockups.md`. The mockup lives *inside* the doc, not behind a link to a design tool, so that the spec and the screen can never drift apart. Number every element the spec mentions and give each number a row in the legend table. A link to Figma is a supplement to this, never a replacement. Prefix the block title `🖼 Demo 功能标注 · …` when it traces a stakeholder's own drawing and plain `🖼 功能标注 · …` when you designed it — and put a `.callout warn` on any mock element that is a placeholder rather than specified behaviour, so nobody builds your guess.

#### 3.3 Non-functional requirements
Easy to forget, but both engineering and QA care:
- **Event-tracking (analytics)**: what to capture (page-view rate, button click rate, conversion path). List "tracking location / event name / trigger timing / reported params".
- **Performance**: response time, concurrency, data volume.
- **Compatibility**: OS versions, device types, browser range.
- **Security**: what is exposed publicly, field whitelists, token/permission surfaces, enumeration risk.
- **Consistency**: which numbers must agree with which (same metric shown twice must be equal), single-source-of-truth rules.
- **Observability**: logging, alerting, what a failed job surfaces to whom.
- **Testing**: what must be pinned by unit tests (boundary values, tier cut-offs, formula calibers).

#### 3.4 Change log
A revision-history table: `版本 / 日期 / 说明`. A PRD is a living document — log every edit so engineers know what to re-read.

### 4/5/Appendices [EXT]
- **四、本版变更点** — mandatory for any iteration on a shipped product. A `C1…Cn` table of `现状 / 本版 / 影响面`, so engineers can focus only on what changed. Cite `Cn` inline and mark changed items with a `.pill new` badge.
- **五、待确认项** — a `# / 问题 / 默认取值` table. **Every open question ships a committed default** so it never blocks development; resolved ones get `<span class="pill new">已明确</span>`.
- **附录** — mandatory when there is a security/exposure surface (field whitelist) or formula-defined metrics (metric dictionary).

## Tailoring by scenario (important)

**Don't apply the full structure mechanically.** Add or drop sections by requirement type, or the doc gets bloated and nobody reads it:

| Scenario | Keep | Usually drop |
|----------|------|--------------|
| Brand-new product / proposal | Full structure | — |
| Version iteration / new feature | Change points, product design, non-functional reqs, change log | Industry overview; trim product intro |
| Single feature / small request | Function & interaction spec (four dimensions), global spec, change log | Industry overview, E-R diagram (if no new entity) |
| B2C product | Flowcharts, global states, interaction error paths | Trim role-permission where light |
| B2B / back-office | Role-permission matrix, E-R diagram, state transitions, field specs | Trim industry overview where light |

The core is always the four-dimension function spec + global states + flowcharts inside **3.2 Product design**; everything else is on demand.

**Iterating a live product (v2 / redesign).** When the PRD is a new version of something already shipped — often kicked off by a stakeholder redrawing a few screens — don't re-spec the whole product; spec the **delta**. Lead with a **change-points table** (what changed vs the last version, plus its build **impact**), keep every recurring caliber as a **global rule cited by ID**, and list unknowns in an **open-questions table where each row carries a default** so engineering never blocks. The PRD encodes **decisions**, not whatever a demo happened to draw. See `references/iterating-a-live-product.md`.

## Quality self-check

Before handoff, go through each item (full version in `references/checklist.md`):

- [ ] Would an engineer still need to come back and ask me? Did I write in the answer everywhere they would?
- [ ] Does every field have its meaning, constraints, and **data source**?
- [ ] Are **exceptions/boundaries** (empty, error, over-limit, offline, no-permission, concurrency, divide-by-zero) all covered?
- [ ] Is there an E-R diagram where data is stored? A permission matrix where multiple roles exist?
- [ ] Are shared controls/states defined once in the global spec and cited by rule ID, with no repetition in the body?
- [ ] Are pages numbered, and does the function spec line up with the mockups?
- [ ] Are analytics, performance, compatibility, security, consistency, observability, and testing written (even if "no special requirement")?
- [ ] Is there a change log? Does every open question carry a default? Is the structure clear and quick to navigate?

Then check the **format**, which is where this skill most often fails. These gates apply to the default annotated-HTML deliverable; the Markdown alternative at the end of this file is scoped out of them (it has no triads and permits Mermaid):

- [ ] Is it one HTML file with **zero** external requests — no CDN, no remote fonts, no remote images?
- [ ] Does `<html lang>` match the language actually written in the body?
- [ ] Does **every** page with a UI have an `.anno-wrap` triad, and does every `.mk` have exactly one `.nbadge` row, ascending with no gaps?
- [ ] Are there **zero** `<pre>` blocks, zero ASCII box-drawing diagrams, and zero Mermaid?
- [ ] Are the three numbering systems kept separate — Arabic for `.mk`/`.nbadge`, circled ①②③④ only for the four spec dimensions and `.flow` node text, `.marker` Arabic for 正常 and literal `!` for every 异常?
- [ ] Are facts carried by markup rather than sentences — `.pill new` on every changed item, `.tag err` on every error path, `.callout rule` on every non-negotiable, `.tick`/`.cross` in permission matrices?
- [ ] Are the TOC labels unique and readable on their own, or did you dump raw heading text and end up with five entries reading the same thing?
- [ ] Did `scripts/verify_prd_html.py` exit clean?

## Output conventions

- Lean on **tables** for structured info (fields, permissions, states, tracking) so engineers grasp it at a glance. Aim for facts carried by markup, not sentences — roughly one semantic token (`.pill`, `.tag`, `.tick`, `.marker`, `.callout`) per ~110 visible characters.
- Express flows as `.flow` chains and E-R / state machines as **inline SVG**. In the default HTML format: never Mermaid, never ASCII, never `<pre>`. (The Markdown alternative has no `.flow` or SVG conventions and uses Mermaid instead — see the last section.)
- Prose is terse, declarative, engineer-facing: no marketing, no hedging, no first person. Use `→` for causality, `「」` for literal on-screen strings, `<code>` for identifiers, `<b>` surgically on the one word a developer would otherwise skim. Every data statement ends with its rule code `（Gn）`; prohibitions carry their reason in parentheses.

### Reference map

| Read this | For |
|---|---|
| `references/design-system.md` | CSS tokens, component inventory, SVG state colours, the three numbering systems, fixed strings |
| `references/document-outline.md` | Canonical outline, anchor ids, TOC construction, fixed table schemas |
| `references/annotated-html-mockups.md` | The triad, mock primitives, SVG and `.flow` recipes, the verification pass |
| `references/iterating-a-live-product.md` | v2 / redesign: change points, global rules by ID, open questions with defaults |
| `references/function-interaction-spec.md` | The exhaustive four-dimension method and a fully worked example |
| `references/checklist.md` | The long-form handoff checklist |
| `assets/annotated-html-prd-template.html` | Start here — the design system plus a worked example of every component |

## Alternative: lightweight Markdown PRDs

When the user asks for Markdown, or the spec is a one-screen change with no UI to annotate, author it from `assets/prd-template.md` (worked example: `assets/example-prd.md`) and render with:

```
python3 scripts/prd_to_html.py path/to/prd.md -o path/to/prd.html --lang zh-CN
```

Note that this renderer carries a different, simpler stylesheet: it **cannot** render annotated mockups, `.spec` blocks, pills, or markers. If the doc needs any of those, it needs the default HTML format instead.

**Two consequences of choosing this path, both deliberate:**

- **Diagrams are Mermaid here**, because Markdown has no `.flow` chains and no inline-SVG conventions — which is why `assets/prd-template.md` and `assets/example-prd.md` contain ```` ```mermaid ```` fences. The "zero Mermaid, zero `<pre>`, zero ASCII" rule in the format self-check above is scoped to the default HTML format and does **not** apply to this path.
- **The rendered output is therefore network-dependent.** `prd_to_html.py` loads Mermaid from a CDN, so any Markdown PRD containing a diagram will not render its diagrams offline, in print, or after archiving; the renderer prints a warning saying so. A Markdown PRD with no Mermaid blocks renders fully self-contained. If the artifact must survive `file://` with diagrams intact, use the default HTML format.

Language applies here exactly as it does to the default format: write the document in the user's language, translate the template's headings, and pass the matching `--lang`.
