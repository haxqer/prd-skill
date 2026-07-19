# Iterating a Live Product — global rules by ID, change-points, and open questions

> Most real PRDs are **not** greenfield — they are v2 of something already shipped, often kicked off by a stakeholder
> redrawing a few screens or sending screenshots. This file adds four disciplines that keep an *iteration* PRD tight,
> consistent, and un-blocked. They are **format-agnostic** — use them in a Markdown PRD or a hand-authored HTML one.
>
> They compose with the rest of the skill: the four-dimension function spec still governs each module; these are the
> connective tissue that stops a large evolving doc from contradicting itself.

---

## 1. Global rules by ID — one source of truth for every cross-cutting caliber

The *Global spec* (section 3.2.4) already says "define shared **states** once." Extend the same idea to shared
**calibers / metric rules** — the caliber decisions that recur in module after module: how a ratio is computed, what
counts as "engagement," how division-by-zero renders, which timezone, which currency, what data is even eligible.
Data- and metrics-heavy PRDs (reports, dashboards, billing) live or die on these staying identical everywhere.

**Give each one a stable ID and cite it inline instead of restating it.**

```
| ID  | Rule |
|-----|------|
| G6  | Engagements = Likes + Comments + Shares + Saves (Saves = Collects). |
| G7  | All ratios are weighted: Σnumerator ÷ Σdenominator, never an average of per-row ratios. |
| G8  | Division by zero renders "—", never 0 or NaN. |
| G10 | All dates/times are UTC (GMT+0); campaign and browser-local timezones are disabled. |
| G11 | Only Posting-verified post links feed any count, metric, chart, or link column. |
```

Then in any module you write "ER% = ΣEng ÷ ΣViews (**G7**), div-by-zero → "—" (**G8**)". The payoff is decisive:

- **A caliber change is one edit.** When the boss says "make it UTC," you edit **G10** and every `(G10)` citation is
  already correct. No search-and-replace, no missed corner.
- **Contradictions become impossible to hide.** Two modules can't quietly disagree about weighting if both cite G7.
- **Reversals stay clean.** This is what let a mid-flight "actually, don't support RedNote" ripple through a whole doc
  safely — the rule moved, the citations didn't have to.

Number them `G1..Gn`, keep them in one table near the top, and treat that table as authoritative. If you catch yourself
re-explaining a caliber in a module, stop — promote it to a G-rule and cite it.

## 2. The change-points table — for a v2, spec the *delta*, not the whole product

For an iteration, engineers do not want to re-read the entire product. They want exactly what changed. Lead the version
with a **change-points table** and state, once, "anything not listed keeps its v1 behavior."

| # | Change point | v1.0 today | v2.0 (this version) | Impact surface |
|---|--------------|-----------|---------------------|----------------|
| C1 | Platform display | Three columns side-by-side (YT/IG/TT) | Single-select platform chips, one metric-card set | **Frontend only** (platform set unchanged) |
| C2 | Overview date range | none | Show min~max `posted_at` under Posts Published | Snapshot adds min/max; frontend adds display |
| C3 | Influencer Geo filter | none | New Geo dropdown (influencer `Profile.country`) | Detail API adds filter + option list |

The **Impact surface** column is the one people skip and the one that earns its place. It is where frontend/backend
scope becomes visible — and it is load-bearing during churn. When a change point is later cut (e.g. a new platform is
descoped), its impact often **collapses**: "backend: add platform constant + per-platform aggregation" becomes "pure
frontend, platform set unchanged." Updating that cell re-scopes the work truthfully in one place. Keep the change-points
table and the *Change log* (3.4) distinct: change-points describe **what differs from the last shipped version and its
build impact**; the change log records **edits to the document over time**.

## 3. Open questions — every one carries a default, so nothing blocks the start

Unresolved does not mean unwritten. List open questions in a dedicated table, and give **every** one a **default value**
so engineering can start against the default while the decision is pending. An open question with no default is a
blocker; an open question with a sensible default is just a footnote.

| # | Question | Default (build against this unless overridden) |
|---|----------|-----------------------------------------------|
| 1 | Does the new platform support every metric? | Unsupported metrics count 0 and display 0. |
| 2 | Geo filter granularity — influencer country or campaign geos? | Influencer `Profile.country`. |

As decisions land, **don't delete the row — resolve it in place**: mark it 已明确 / Resolved and replace the default with
the confirmed answer. That preserves the decision trail (why the build is the way it is) and doubles as a lightweight
decision log. A row that reads "Resolved: influencer `Profile.country` (not campaign geos)" answers the next reviewer's
question before they ask it — which is the whole standard of this skill.

When a change reverses a prior plan, the open-questions table is where the reversal is recorded: flip the row to
Resolved with the new decision, and make the body consistent (remove the descoped control from mockups per
`annotated-html-mockups.md` §Provenance). The default keeps anyone who read the earlier version from being surprised.

## 4. Decision-driven, not source-driven

A stakeholder's redrawn demo, a screenshot, a Slack thread — these are **inputs**, not the spec. The PRD states what
will be **built**, which is the set of **decisions**, and decisions can and do diverge from any single input:

- The demo drew a control that a later call cut → the PRD does **not** show it as buildable; it goes to open questions
  as "deferred," with the reason.
- A screenshot shows a "Refresh" button, but the report is a frozen nightly snapshot → the spec says the button is
  **not an operation on this page**, and points at the module that actually owns refresh. (Mirroring a screenshot
  pixel-for-pixel without its behavior is how a wrong capability gets built.)
- Two inputs conflict → the PRD picks one, cites the decision, and records the other as considered-and-rejected in open
  questions.

The test is the same one this whole skill runs on: *if I were the engineer, would I build the wrong thing by trusting
the picture?* If yes, write the decision — and its divergence from the input — explicitly.

---

## In one line

For an iteration: cite calibers by **G-ID** so a rule change is one edit; lead with a **change-points table** whose
**impact** column re-scopes truthfully as things churn; keep an **open-questions table** where every row has a
**default** and resolves in place; and remember the PRD encodes **decisions**, not whatever a demo happened to draw.
