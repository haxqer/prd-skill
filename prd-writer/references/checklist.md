# PRD Pre-Handoff Quality Checklist

Go through each item before handing off to engineering. The one core test: **after reading, would an engineer still need to come back and ask me?** Wherever they would, that's what to fill in.

## 1. Readability (so engineers will actually read it)
- [ ] Is the structure clearly layered, so any content can be located in seconds?
- [ ] Does it carry structured info in tables/flowcharts instead of walls of text?
- [ ] Is it tightly organized and focused, with no filler — whatever the format?
- [ ] Does every page/function have a number (`P0`, `P1`, `P2.1`, ...) that lines up with the mockups?

## 2. Rigorous logic (so engineers stop coming back)
- [ ] Does every field state its meaning, constraints (type/length/required/default), and **data source**?
- [ ] Does every page state its preconditions, sort rules, and refresh rules?
- [ ] For objects/pages with state, is there a state-transition table or diagram covering all states and transitions?
- [ ] Is the normal interaction path complete?
- [ ] Are the **abnormal paths** all covered (empty / error / offline / invalid input / over-limit / no-permission / concurrency & timing / boundary values)?

## 3. What engineers specifically care about
- [ ] Data persisted → is there an E-R diagram with fields and relationships?
- [ ] Multiple roles/permissions → is there a complete role-permission matrix?
- [ ] Are shared controls & states (empty/loading/failed/offline/no-permission) defined once in the global spec and not repeated in the body?
- [ ] Is the business flow decomposed into task flow / page flow?

## 4. Non-functional requirements (don't forget)
- [ ] Analytics: tracking location / event name / trigger timing / reported params?
- [ ] Performance: response time / concurrency / data volume stated (even "no special requirement")?
- [ ] Compatibility: OS versions / device types / browser range stated?

## 5. Maintainability
- [ ] Is there a change-log table (version / date / author / change)?
- [ ] Are the version number, owner, and update date all labeled?

## 6. Iteration (when the product is already live — see `iterating-a-live-product.md`)
- [ ] Iteration/v2: is there a **change-points table** (what changed vs the last version + build **impact**), with "everything else unchanged" stated once?
- [ ] Are recurring calibers defined as **global rules with IDs** and **cited by ID** in modules (not restated, not silently diverging)?
- [ ] Does every **open question carry a default**, and are resolved ones marked **in place** (not deleted), preserving the decision trail?
- [ ] Does the doc encode **decisions** — is any control a demo drew but a decision cut moved to open-questions as *deferred*, not left on the mockup as buildable?

## 7. Format gates (always — this is where the skill most often fails)

The eight items below are not conditional. They apply to every PRD this skill produces, because the default
deliverable is a single self-contained annotated HTML file (see `annotated-html-mockups.md`, `design-system.md`).
The content can be flawless and the document still fail here — that is the exact failure these gates exist to catch.

- [ ] Is it **one** `.html` file with **zero** external requests — no CDN script, no remote font, no remote image, no `@import`?
- [ ] Does `<html lang="…">` match the language actually written in the body?
- [ ] Does **every** page with a UI have an `.anno-wrap` triad, and does every `.mk` have exactly one `.nbadge` row — ascending, no gaps, no duplicates, restarting at 1 per `.anno-wrap`?
- [ ] Are there **zero** `<pre>` blocks, **zero** ASCII box-drawing diagrams, and **zero** Mermaid? (If you drew `┌───┐`, you are in the wrong format.)
- [ ] Are the three numbering systems kept **separate** — Arabic for `.mk`/`.nbadge`; circled ①②③④ only for the four spec dimensions and `.flow` node text; `.marker` Arabic for 正常 / normal items and a literal `!` for **every** 异常 / abnormal item?
- [ ] Are facts carried by **markup rather than sentences** — `.pill new` on every changed item, `.tag err` on every error path, `.callout rule` on every non-negotiable, `.tick`/`.cross` in permission matrices?
- [ ] Are the **TOC labels unique** and readable standalone, or did you dump raw heading text and end up with five entries reading the same thing?
- [ ] Did **`scripts/verify_prd_html.py` exit clean**? Run it after the last edit — hand-authored HTML has no compiler, so this is the compiler.

## Trim reminder
Not every PRD needs every box in sections 1–6 checked. Iterations can skip "Industry overview" and "E-R diagram (when no new entity)"; but the **four-dimension function spec, global states, and abnormal-path coverage** should almost never be dropped from any PRD — and **section 7 is never trimmed**.
