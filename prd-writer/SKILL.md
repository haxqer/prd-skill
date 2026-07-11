---
name: prd-writer
description: >
  Write a Product Requirements Document (PRD) that engineers actually love to read. Use this skill whenever the user
  needs to write a PRD, a requirements document, a product spec, a functional spec, or wants to turn a product idea or
  feature into a document that can be handed straight to engineering — even if they never say the letters "PRD". Intents
  like "write up this requirement for the dev team", "put together a spec", "document this feature for engineers", or
  "write a requirements doc" should all trigger it. The skill provides a battle-tested PRD structure and writing style
  that minimizes back-and-forth with engineers and is ready for estimation and development (Product intro / Industry
  overview / Version: schedule, product design, non-functional requirements, change log), with emphasis on the details
  engineers actually care about: E-R diagrams, role-permission matrices, layered flowcharts, global states, and
  field-level + interaction specs. Produce all output in English.
---

# PRD Writer — Write a Requirements Doc Engineers Love

Whether a PRD is good is not measured by how many words you wrote. It is measured by whether an engineer, after reading it, can start building with **fewer questions, less guessing, and less rework**. This skill turns that standard into a reusable structure and writing style.

## Core philosophy: write from the engineer's point of view

A PRD usually fails not because it says too little, but because it says things engineers can't use — or leaves out exactly the part they need. Engineers have three real pain points; keep them in view the whole time you write:

1. **The doc gets shelved** — too long, no clear focus, tiring to read, so engineers just stop opening it.
   → Fix: clear, layered structure; carry information in Markdown, tables, and flowcharts so anything can be located in seconds.
2. **Endless back-and-forth to confirm requirements and edge cases** — the logic has gaps, so engineers have to keep asking.
   → Fix: spell out exceptions, boundaries, state transitions, and data sources up front so the doc answers questions on its own.
3. **What ships is a mess** — vague descriptions and loose logic, discovered only in QA.
   → Fix: describe things precisely at the field and state level; cover both the happy path and the error paths.

**The self-check question for any chunk of a requirement:** if I were the engineer, would I still need to come back and ask me something after reading this? If yes, write in the answer to that question.

## Workflow

Given a requirement or product idea, proceed in this order:

1. **Clarify before writing.** Fill in these facts (if any are missing, proactively ask the user — never invent business facts):
   - What product / feature is this? Who uses it (target users, roles)? What problem does it solve?
   - Is it B2B (internal / back-office) or B2C? A brand-new product, or a feature/iteration on an existing one?
   - What roles and permissions are involved? Are there data entities (does it need an E-R diagram)?
   - Any known performance, compatibility, or analytics (event-tracking) requirements?
2. **Pick the structure and trim it.** Use the *PRD Structure* below as the skeleton, but **don't apply it blindly** — see "Tailoring by scenario".
3. **Fill in section by section.** Put the most polish into the flowcharts, global states, and function-and-interaction specs inside "Product design" — those decide the engineering experience.
4. **Run the quality self-check** and plug every question an engineer would come back to ask.
5. Output in **Markdown** with tables and (where useful) flowcharts. Start from `assets/prd-template.md` for a ready-made skeleton.

## PRD Structure

The full skeleton is below. This is the "fully loaded" structure for a brand-new product; for iterations, trim it per "Tailoring by scenario".

```
1. Product intro
2. Industry overview
3. Version vX.Y
    3.1 Schedule
    3.2 Product design
        - Entity-Relationship (E-R) diagram
        - Role-permission matrix
        - Business flow -> task flow -> page flow
        - Global spec (shared controls & states)
        - Function & interaction spec (per page / module, with page numbers)
        - Page annotations
    3.3 Non-functional requirements
        - Event-tracking (analytics) requirements
        - Performance requirements
        - Compatibility requirements
    3.4 Change log
```

### 1. Product intro
Make anyone understand the product in 30 seconds. Answer three questions:
- **Who am I** — the product's identity/positioning in one or two sentences.
- **What am I good for** — what it does, what service it offers, what problem it solves.
- **Why choose us** — the differentiators versus competitors.

Then add one line on **target users** and the **core use scenario**. This section builds shared context for everyone (including newly onboarded engineers). Don't write marketing copy — write facts.

### 2. Industry overview
Cover the industry's current state, trends, and main competitors. Its purpose is to help the team understand *why now, and why this shape*.
> **Trim tip:** iterations, internal tools, and single-feature requests usually don't need this — delete the whole section. It mainly serves brand-new products / project proposals.

### 3. Version
A version corresponds to one shippable scope of development. Label the version number (e.g. v1.2). It contains four parts:

#### 3.1 Schedule
A timeline table confirmed together with engineering: for each module under the version, the owner, estimated dates, and status. This table makes progress visible and trackable; engineers can mark a module done, so the project doesn't "fall behind and blow up mid-way".

#### 3.2 Product design (the heart of the PRD, and where "engineers love it" is won)
Detailed writing guidance with copy-ready tables and flowcharts lives in `references/section-guide.md`. The **function & interaction spec** below is the most detailed part of a PRD and has its own exhaustive deep-dive in `references/function-interaction-spec.md`. Key points:

- **Entity-Relationship (E-R) diagram**: whenever data is persisted, lead with an E-R diagram showing entities and their attribute fields. Database engineers can design the table schema straight from it, sparing the repeated "where does this field live, what does it relate to?".
- **Role-permission matrix**: any time multiple roles/permissions are involved, build a full "role × function/data" matrix. Permissions scattered through the prose are the easiest source of bugs; centralizing them in a table is the safest form.
- **Flowcharts, decomposed layer by layer**: first draw the **business flow** (overall logic) → break it into a **task flow** (how one task runs) → break that into a **page flow** (how pages transition). Layered decomposition lets engineers see both the forest and the trees.
- **Global spec**: define shared controls and shared states (empty data, loading, load-failed, network error, no-permission, button loading/disabled, etc.) **once**, and stop repeating them in the body. This is the key trick for keeping a PRD concise, and it prevents each page from writing its own conflicting version.
- **Function & interaction spec**: describe each page/module, and write every one across **four dimensions** (this is the core of stopping the back-and-forth):
  1. **Fields, descriptions, data sources** — for each field: what it is, its type/format/length/enum and display rules, and where the value comes from (System-determined / Backend / API endpoint→field / Computed / User input). Format: `| Field | Description | Data source |`.
  2. **Precondition, sort rule, load rule** — what must hold to enter this page; how the list is sorted; how it first-loads, paginates ("load more"), and refreshes. Format: `| Precondition | Sort rule | Load rule |`.
  3. **State transitions** — how an object/page moves between states under different conditions. Format: `| From state | Trigger / condition | To state |`, plus a Mermaid state diagram when it clarifies.
  4. **Interactions: normal + abnormal** — a numbered list keyed to the wireframe annotations (①②③…, matching numbers drawn on the mockup): tap/act on each element → result, including confirm dialogs and their branches (e.g. "Cancel order" → confirm dialog → Confirm / Don't cancel yet). Cover the happy path **and** the error paths (invalid input, network failure, empty data, over-limit, concurrency conflicts). Error branches are the most often forgotten and the most bug-prone — they must be written.

  > **This is the single most important and most detailed part of the PRD.** Do not summarize it — spec it. For the exhaustive method — how to fill every column of the canonical field / interaction / state / analytics tables, the full abnormal-path taxonomy, per-component interaction conventions (button/list/form/modal/toast), gestures & keyboard, optimistic UI, permissions and analytics per action, and a fully worked max-detail example — follow `references/function-interaction-spec.md` closely.
- **Page annotations**: give every page/mockup a **number** (e.g. P-01, P-02), and reference those numbers in the function spec, so the doc, the mockups, and the visual designs all line up. When the mockup should live **inside** the doc as a numbered, pixel-faithful recreation (rather than a link to an external design tool), use the annotated-mockup triad in `references/annotated-html-mockups.md`.

#### 3.3 Non-functional requirements
Easy to forget, but both engineering and QA care:
- **Event-tracking (analytics) requirements**: what data to capture (page-view rate, button click rate, conversion path, etc.) for later analysis. List "tracking location / event name / trigger timing / reported params".
- **Performance requirements**: response time, concurrency, data volume, and similar metrics.
- **Compatibility requirements**: supported OS versions, device types (phone/tablet/PC), and browser range.

#### 3.4 Change log
A revision-history table: version / date / author / change. A PRD is a living document — log every edit so engineers know what to re-read.

## Tailoring by scenario (important)

**Don't apply the full structure mechanically.** Add or drop sections by requirement type, or the doc gets bloated and nobody reads it:

| Scenario | Keep | Usually drop |
|----------|------|--------------|
| Brand-new product / proposal | Full structure | — |
| Version iteration / new feature | Product design, non-functional reqs, change log | Industry overview; trim product intro |
| Single feature / small request | Function & interaction spec (four dimensions), global spec, change log | Industry overview, E-R diagram (if no new entity) |
| B2C product | Flowcharts, global states, interaction error paths | Trim role-permission where light |
| B2B / back-office | Role-permission matrix, E-R diagram, state transitions, field specs | Trim industry overview where light |

The core is always the four-dimension function spec + global states + flowcharts inside **3.2 Product design**; everything else is on demand.

**Iterating a live product (v2 / redesign).** When the PRD is a new version of something already shipped — often kicked off by a stakeholder redrawing a few screens — don't re-spec the whole product; spec the **delta**. Lead with a **change-points table** (what changed vs the last version, plus its build **impact**), keep every recurring caliber as a **global rule cited by ID** (change the rule once, every citation follows), and list unknowns in an **open-questions table where each row carries a default** so engineering never blocks. The PRD encodes **decisions**, not whatever a demo happened to draw. See `references/iterating-a-live-product.md`.

## Quality self-check

Before handoff, go through each item (full version in `references/checklist.md`):

- [ ] Would an engineer still need to come back and ask me? Did I write in the answer everywhere they would?
- [ ] Does every field have its meaning, constraints, and **data source**?
- [ ] Are **exceptions/boundaries** (empty, error, over-limit, offline, no-permission, concurrency) all covered?
- [ ] Is there an E-R diagram where data is stored? A permission matrix where multiple roles exist?
- [ ] Are shared controls/states defined once in the global spec, with no repetition in the body?
- [ ] Are pages numbered, and does the function spec line up with the mockups?
- [ ] Are analytics, performance, and compatibility written (even if "no special requirement")?
- [ ] Is there a change log? Is the structure clear and quick to navigate?

## Rendering the PRD to HTML

A PRD is authored and version-controlled as Markdown, but stakeholders often want something nicer to read, share, or print to PDF. Once the Markdown PRD is done, offer to render it to a polished, self-contained HTML page with the bundled script:

```
python3 scripts/prd_to_html.py path/to/prd.md -o path/to/prd.html
```

What it produces: a single HTML file with a sticky table-of-contents sidebar (with scroll highlighting), styled tables, a document header (title / owner / version / date parsed from the top of the doc), rendered **Mermaid** diagrams (E-R, flow, state), status badges, and print styling — so the browser's "Print → Save as PDF" yields a clean document.

Dependency: it uses `python-markdown` when available (`pip install markdown`) for best fidelity, and falls back to a built-in, dependency-free converter otherwise, so it always runs. Mermaid renders in the browser via a CDN script and degrades to the raw diagram source when offline (vendor `assets/vendor/mermaid.min.js` for fully offline rendering).

See `assets/example-prd.md` for a full worked example; running the command above on it produces the reference HTML.

## Annotated HTML mode (high-fidelity, hand-authored)

For most PRDs the Markdown-first flow above is the right one. Reach for a **hand-authored, self-contained HTML PRD** only when the spec **hinges on high-fidelity UI** — numbered callouts pinned on a pixel-faithful screen recreation that Mermaid can't express — typically when a stakeholder communicates by redrawing screens or sending screenshots, and the HTML file itself is the artifact people read, share, and print. It carries the **annotated-mockup triad**: a recreated screen + numbered `.mk` markers + a `.nbadge` explanation table keyed to them, one-to-one. Start from `assets/annotated-html-prd-template.html` (ships the whole design system plus one worked example of every component) and follow `references/annotated-html-mockups.md` — including its four-check **verification** pass (tag balance, marker↔table continuity, marker clip check, stale-string grep), because hand-authored HTML has no compiler and you are it. The two modes combine: you can embed an annotated-mockup block inside a Markdown PRD as long as the rendered page includes the mockup CSS.

## Output conventions

- Default to **Markdown**, and lean on **tables** for structured info (fields, permissions, states, tracking) so engineers grasp it at a glance.
- Express flowcharts and state diagrams as prose + Mermaid (```mermaid```), which version-controls and reviews cleanly — and renders natively in the HTML export.
- Write all output in **English**.
- When you need a ready-made skeleton, start from `assets/prd-template.md`; for the summary of product-design writing, read `references/section-guide.md`; for the exhaustive function & interaction method, read `references/function-interaction-spec.md`; for a complete worked PRD, see `assets/example-prd.md`.
- For a **v2 / redesign** of a shipped product (change-points, global rules by ID, open questions with defaults, decision-driven writing), read `references/iterating-a-live-product.md`. For a **self-contained annotated HTML PRD** (in-doc numbered mockups + verification), read `references/annotated-html-mockups.md` and start from `assets/annotated-html-prd-template.html`.
- When the PRD is finished and the user may want to share or print it, offer to render it to HTML with `scripts/prd_to_html.py` (see *Rendering the PRD to HTML*).
