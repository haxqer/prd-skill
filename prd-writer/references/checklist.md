# PRD Pre-Handoff Quality Checklist

Go through each item before handing off to engineering. The one core test: **after reading, would an engineer still need to come back and ask me?** Wherever they would, that's what to fill in.

## 1. Readability (so engineers will actually read it)
- [ ] Is the structure clearly layered, so any content can be located in seconds?
- [ ] Does it carry structured info in tables/flowcharts instead of walls of text?
- [ ] Is it organized in Markdown, focused, with no filler?
- [ ] Does every page/function have a number (P-01, ...) that lines up with the mockups?

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

## 6. Iteration & annotated-HTML mode (when applicable — see `iterating-a-live-product.md`, `annotated-html-mockups.md`)
- [ ] Iteration/v2: is there a **change-points table** (what changed vs the last version + build **impact**), with "everything else unchanged" stated once?
- [ ] Are recurring calibers defined as **global rules with IDs** and **cited by ID** in modules (not restated, not silently diverging)?
- [ ] Does every **open question carry a default**, and are resolved ones marked **in place** (not deleted), preserving the decision trail?
- [ ] Does the doc encode **decisions** — is any control a demo drew but a decision cut moved to open-questions as *deferred*, not left on the mockup as buildable?
- [ ] Annotated HTML: does every mockup **marker** have a matching **explanation-table row**, numbered 1..N continuously?
- [ ] Annotated HTML: did you run the four checks (tag balance · marker↔table continuity · clip check · stale-string grep) after the last edit?

## Trim reminder
Not every PRD needs every box checked. Iterations can skip "Industry overview" and "E-R diagram (when no new entity)"; but the **four-dimension function spec, global states, and abnormal-path coverage** should almost never be dropped from any PRD.
