# Function & Interaction Spec — the method for 3.2.5

This is the method for the PRD's centre of gravity: **3.2.5 需求、功能、交互说明 / Requirements, function & interaction spec**. Everything else in section 3.2 — the E-R diagram, the role matrix, the flowcharts, the global spec — exists to set this section up, so this file covers those first (§1), then the page decomposition (§2), then the four dimensions in full (§3–§6), then one worked page (§7).

**Self-check for every chunk you write:** *if I were the engineer, would I still need to come back and ask?* If yes, you have not finished the sentence. "Show the address" is a question generator (how long? what on overflow? where from?). "Address, 6–20 chars, single line, overflow truncates to `…`, from `GET /orders → items[].address`" is an answer.

Write in the user's language. The four fixed spec labels are given below in both Chinese and English; pick one language and never mix. Product, metric, and entity names stay in their original English either way.

---

## 1. What must exist before 3.2.5

Four artefacts. Each one removes a whole class of follow-up question. All four are **inline SVG or `.flow` chains** — never Mermaid, never ASCII art (recipes in `references/annotated-html-mockups.md`).

### 1.1 E-R diagram (3.2.1)

**Why:** database engineers design the schema without asking "where does this field live, what does it relate to?". Lead with one whenever data is persisted.

**How:** entities as SVG boxes (two `<text>` lines — title + sub-caption), relationships as `marker-end` arrows labelled `1:N` / `N:1`. **Solid** edges = business entities; **dashed** (`stroke-dasharray="4 3"`) = derived/materialised entities (snapshots, share records, AI outputs). Close with the mandatory grey caption `<p>` explaining the line semantics.

For every enum column (`status`, `wash_type`, `platform`), spell out the meaning of each value right there or in the field table — it saves engineering and QA both.

### 1.2 Role-permission matrix (3.2.2)

**Why:** permission logic scattered through prose produces the classic bug "a role that shouldn't see X can see X". Centralise it into one matrix — scannable, and directly testable.

**How:** rows are functions/data items, columns are roles, cells are `.tick` / `.cross` with a qualifier when partial.

| 能力 / Capability | 运营 Ops (`CAMPAIGN_REPORT`) | 客户 Client (anonymous token) | 超管 Admin |
|---|:--:|:--:|:--:|
| View Overview / Influencer | ✔ | ✔ read-only, cropped by toggle | ✔ |
| Generate AI Summary | ✔ | ✘ | ✔ |
| Configure TTL / rollup time | ✘ | ✘ | ✔ |

Actions a role cannot perform are **hidden**, not shown-then-blocked — except where a disabled-and-explained state is clearer (offline, machine busy, no snapshot yet).

### 1.3 Layered flowcharts (3.2.3)

Decompose coarse to fine. Two decompositions are acceptable; **state which one you used**:

- **By zoom:** business flow → task flow → page flow.
- **By actor:** system-automatic pipeline flow vs. user-operation flow. (Preferred when a data pipeline runs without a user.)

Each layer is one `.flow` chain of `.node` / `.node.term` / `.node.warnn` separated by literal `→`, with `/` marking a branch:

```html
<div class="flow">
  <span class="node">打开链接</span><span class="arw">→</span>
  <span class="node">校验 token</span><span class="arw">→</span>
  <span class="node term">有效 → 渲染只读报表</span>
  <span class="arw">/</span>
  <span class="node warnn">过期 / 撤销 / 不存在 → P5 失效页</span>
</div>
```

Numbered use-case chains put circled numerals **inside the node text** (`① Report Tab` → `② 生成 AI Summary` → …).

### 1.4 Global spec (3.2.4)

**Why:** empty data, loading, load failure, offline appear on nearly every page. Writing them per page is verbose and drifts. **Define once, reference everywhere** — this is the single biggest lever on PRD concision.

Three sub-blocks, as `h5` A / B / C:

**A. 全局口径规则 / Global calibration rules** — give each rule an **ID** (`G1…Gn`) and a short name, then cite it inline everywhere as `（G7）` so the single source of truth is one hop away. Example rows: `G6 Engagements = Likes+Comments+Shares+Saves；Saves = Collects`; `G7 比率加权 — 所有 Rate 均为 sum/sum 总量相除，不做逐帖平均，禁止复用 EngRate()`; `G8 除零/空值 — 分母为 0 → 返回 null、前端渲染 "—"，不返回 0/Infinity`.

**B. 分层 / 枚举定义** — tier breakpoints, status enums, platform constants. State that the list is a constant single-source (`加平台只改常量`).

**C. 通用控件规范 / Shared control states:**

| Scenario | Behaviour | Copy / action |
|---|---|---|
| Empty | Purpose-specific empty state with an action, never a blank screen | 「Report data will be generated after the next daily update.」+ disable AI / Share |
| Loading | Skeleton (page-level) or component-level spinner | **Every `catch` branch must reset loading** |
| Load failed / network error | Keep previously good data, add retry | 「Load failed, tap to retry」+ [Retry] |
| Offline | Top banner, cached content read-only | 「No network connection」 |
| No permission | Empty-state page | 「No permission to view, contact your admin」 |
| Request in flight | Button spinner + disabled | Prevents double submit |
| Division by zero / missing input | Render the null placeholder | `"—"`, never `0` / `NaN` / `Infinity` |
| Data staleness | Global `Data as of <snapshot time>` | Identical on logged-in and public views |

In the body you then write "empty list → 见 §3.2.4C 空态" with no repetition.

---

## 2. Page decomposition & numbering

Slice each page top-to-bottom into regions, then components: **navigation** (title bar, back, right-side actions) → **content** (list, form, cards, detail blocks) → **action** (primary/secondary/floating buttons) → **global chrome** (tab bar, toasts, dialogs — reference the global spec, don't repeat it).

Then run each component through the four dimensions. One large screen may decompose into several **modules** (`M1…Mn`), each with its own field table inside a `.module` card.

**Numbering:** pages are `P0`, `P1`, `P2`, sub-pages/drawers `P2.1`, with `·` before the name — `P2.1 · Post Details 抽屉（Post Link 列交互）`. Use the same number in the heading, in every cross-reference ("点击 → 打开抽屉（P2.1）"), and in the annotated mockup. Do **not** use `P-01` style: it is inconsistent with the corpus and blocks sub-page numbering.

Interaction rules are keyed to the numbered markers on the mockup, so every rule points at an exact element in the picture. That coupling is the whole point — see `references/annotated-html-mockups.md` for the `.mk` / `.nbadge` triad.

---

## 3. The four dimensions

Every page and module is written across the same four dimensions, in this order, in these exact `.spec` blocks. **The order ①→②→③→④ never varies.** Omit a dimension only when the page genuinely has nothing to say for it.

| Block | Dimension | Colour |
|---|---|---|
| `.spec.field` | ① fields | blue |
| `.spec.cond` | ② preconditions | teal |
| `.spec.state` | ③ states | purple |
| `.spec.inter` | ④ interactions | orange |

The `.spec-label` text is a **fixed string** in both Chinese and English. It is written down in exactly one place
— *Fixed strings* in `references/design-system.md`. Copy it from there; the headings below are section titles for
this reference, not label text to emit.

### ① Fields, description, data source

One `table.data` per module: `字段 / 说明（含格式）/ 数据来源` (English: `Field / Notes (incl. format) / Data source`), plus a `范围 / Scope` column when scope varies per row.

The **description** cell packs everything about the field into one place. Answer, in order, whatever applies: **type** → **format** (the exact rendered shape: `2016-03-15 19:00`, `¥15`, `14 ( IG 5 , TT 9 )`) → **length / range** → **enum dictionary**, spelled out in full → **display rules** (truncation, rounding, magnitude suffixes, placeholder when empty) → **conditional visibility** → **masking**.

The **data source** cell is the soul of this dimension. Attribute every field to exactly one of:

- **System-determined** — app/business logic sets it.
- **Backend / 后台配置** — configured in the admin console.
- **API `<endpoint> → <field>`** — prefer this over a bare "Backend" whenever you know the endpoint.
- **快照聚合 / Snapshot aggregate** — read from a materialised snapshot, not live.
- **Computed / 计算** — derived; always cite the rule ID, e.g. `Total Engagements ÷ Total Views × 100（G7 加权）`.
- **User input**.
- **OCR / 图片识别** — extracted from an uploaded image; inherently lossy, so state the fallback.

When a field blends sources, say so: `Price = promo_price if present else price (API), rendered client-side`.

**Units, timezone, format** — state once globally, reference per field: money (currency, symbol, decimals, rounding by magnitude); time (store UTC, display timezone, format string); distance; magnitude suffixes (`9.80K` / `1.51M`).

**Masking** — never render full sensitive values. `Phone → 138****1111`, `Card → **** 6411`, full value server-side only. For public/anonymous surfaces, define a **whitelist DTO** and put the un-exposed field list in an appendix.

**Microcopy & i18n** — enum labels are keys, not literals (`status.unused`); never concatenate translated fragments (`"{n} orders"`, not `"orders" + n`); empty-state copy is part of the field row, not a build-time afterthought.

### ② Preconditions, logic, sorting, refresh

**This dimension is 逻辑 (logic), not just loading mechanics.** Validation and edge cases live here — not buried in ④'s error paths.

Format: a **single-row three-column** `table.data` — `前置条件 / 排序机制 / 刷新机制` — each cell a `<br>`-separated numbered list (`1. … ；<br>2. … ；<br>3. …。`).

| Cell | Must cover |
|---|---|
| **前置条件** Preconditions | Auth and permission bit required to enter; data preconditions (「campaign 已生成快照，否则整页空态」); feature flags; **input validation rules** — client layer (format/length/required, disables submit) *and* server layer (source of truth, business rules the client can't know); **whitelists** (「排序列白名单映射防注入」); length and format limits |
| **排序机制** Sorting | Default sort and direction (`默认 Views 降序`); which columns are sortable and where sorting executes (client vs. **服务端排序**); tie-breakers; fixed-order sections (`板块顺序固定 = 锚点顺序`); **what resets on a filter change** (`筛选变更重置到第 1 页`) |
| **刷新机制** Refresh | First load and skeleton; page size and pagination (`page_size ≤ 50`); pull-to-refresh; polling and its stop condition; cache TTL and stale-while-revalidate; silent refresh on返回; **explicitly say when there is no refresh** (`无实时刷新按钮——数据每日凌晨快照更新`); rate limiting |

**Boundary conditions belong in ②.** Walk them explicitly and write the ones that apply: **zero** (empty list, zero denominator, zero budget), **one** (single item — does the leaderboard still render bars?), **max** (page-size cap, list limit, max length, quota), **out-of-range** (negative, over-limit, unknown enum value from the backend → fall back and log), **first/last page**, **edge times** (timezone midnight, TTL expiry boundary). Each gets a stated behaviour, not an assumption.

### ③ State transitions

State is where engineers most easily misunderstand. Give **both** representations:

1. A table — `From / Trigger · condition / To`, extended with `Guard` and `Side effect` columns when they exist. Guards gate a transition (`Unused → Canceled` only while the machine has not started; otherwise the button is hidden). Side effects say what else fires (refund initiated, slot released, billing stopped). Auto-transitions are the ones the *system* fires with no user action (payment timeout, TTL expiry, snapshot refresh marking a summary `stale`) — mark them `(auto)`.

2. An **inline SVG** state diagram. Recipe in `references/annotated-html-mockups.md`: `rx="8"` boxes, pastel fill + saturated stroke per the state-colour table (neutral / loading / success / error / warn), unique `marker` id per SVG, solid edges for primary transitions and `stroke-dasharray="4 3"` for retry / return / derived edges, edge labels as `<text font-size="10" fill="#8592a6">`.

**Never Mermaid.** A Mermaid block is a CDN dependency and renders as a code fence in a `file://` PRD, which is the failure mode this format exists to avoid.

### ④ Interactions (normal + abnormal)

An `ol.inter-list`, one `<li>` per rule, keyed to the mockup markers. Each item is `<span class="marker">n</span><span class="tag normal">正常</span>` then the rule, phrased `<element> → <result>`.

**All 正常 items first, numbered `1, 2, 3…` in orange circles. Then all 异常 items, every one carrying the literal `!` in a red circle (`.marker.err` + `.tag err`) — abnormal items are never numbered.**

Every rule names its target element in `<b>`, its result, and the page it navigates to. Destructive actions state the confirm dialog and quote its exact copy; drop a `.dialog` mock directly under the list. Two dialogs sit side-by-side when a flow double-confirms; the destructive confirm uses `.btn.danger`.

---

## 4. The abnormal-path taxonomy

Anyone can write the happy path; the error paths separate professional from amateur. Walk this taxonomy for **every** interactive page and write each row that applies. This is the only place it is stated — do not re-list it per page.

| Category | What it means | Required handling |
|---|---|---|
| Empty | No data to show | Purpose-specific empty state with an action; disable the actions that need data |
| Error | Request failed (5xx, parse error) | Keep previously good data; show retry; **never blank the screen if stale data exists**; every `catch` resets loading |
| Offline | No network | Offline state; queue or block actions; auto-recover on reconnect |
| Invalid input | Malformed value | Inline validation on blur and submit, block submit, precise message under the field |
| Out-of-bounds / over-limit | Beyond range, list limit, rate limit, non-whitelisted column | Clamp or reject with a clear message; disable the trigger at the boundary |
| Permission | Role lacks rights, session expired, OS permission denied | Hide or disable and explain; on session expiry **preserve intent** — after re-auth, return and resume the action |
| Concurrency & timing | State changed elsewhere between load and act; double-submit | Server detects the conflict and rejects; client toasts and refreshes. Buttons disable on first tap; requests carry an **idempotency key** so a network retry never fires twice |
| Boundary values | 0, 1, max, first/last page, timezone midnight, TTL edge | Specify behaviour at each edge explicitly (see ②) |
| Degraded source | An upstream feed is lossy (OCR, third-party API, partial collection) | State the fallback value, whether the field is excluded by default, and how the user learns it is missing |

---

## 5. Interaction conventions (define once, reuse)

- **Buttons** — states default / pressed / loading / disabled. A primary action enters loading on tap and disables until the request resolves. Never a dead disabled button with no reason: hide it, or explain it.
- **Lists** — tap → navigate; swipe is a shortcut to an existing action, never a delete-without-confirm; long-press reserved for multi-select.
- **Forms** — validate on blur and on submit; on failed submit, scroll to and focus the first invalid field; numeric keypad for phone/code fields.
- **Dialogs** — confirm dialog for every destructive or irreversible action, with two buttons and exact quoted copy. Scrim tap = dismiss, **never** confirm.
- **Toasts** — non-blocking, ~2s, for outcomes needing no acknowledgement. Never for a decision the user must make; that is a dialog.
- **Optimistic UI** — state explicitly whether an action is optimistic or waits for the server, and specify the **rollback**: restore the prior state, restore the buttons, toast the reason.
- **Undo** — where undo is cheap, prefer a 5s "Undo" toast over a confirm dialog. Where it is not, confirm.
- **Accessibility** — accessible label on every actionable element (the trash icon reads "Delete order", not "button"); state conveyed by label + shape, not colour alone; touch targets ≥ 44×44pt; dialogs trap focus and return it on close; cards reflow rather than clip at the largest dynamic type.

**Analytics per interaction** — one row per meaningful interaction, columns matching 3.3's analytics table so they merge cleanly: `Event / Trigger timing / Properties / Notes`.

**Performance budgets** — for the page's key interactions: target latency (p95), the threshold at which a skeleton or spinner appears, and the debounce/throttle rule.

**Acceptance criteria** — optional but powerful for the flows QA will script. Gherkin-style `Given / When / Then`, one scenario per branch including the conflict and double-tap branches.

---

## 6. Worked example — `P2 · Influencer 页` of a campaign report

An analytics/reporting page: a filtered, sortable influencer detail table with a snapshot-backed data source, weighted-ratio metrics, an export drawer, and a public share surface. Adapt the shapes; the domain will differ.

### ① 字段、字段说明、数据来源

```html
<div class="module">
  <h5>M1 · 明细表列 <span class="pill new">本版·Post Link 徽标</span></h5>
```

| 字段 | 说明（含格式） | 数据来源 | 范围 |
|---|---|---|:--:|
| Influencer | avatar / handle / nickname / platform 图标；行 = 达人行（platform, handle），同一达人跨平台分行（G4） | 快照达人行 | — |
| Post Link | `Master n` / `Mirrored n` 计数徽标；无则 `"--"`。hover 出预览卡；点击打开 Post Details 抽屉（P2.1） | 快照 post 聚合 | — |
| Followers | 数字带量级（`9.80K` / `1.51M`）+ tier 徽标；一律取**快照值**（G5） | 快照 followers | M+M |
| Views / Likes / Comments / Shares / Saves | 求和，带量级；`Saves = Collects`（G6）；平台不支持的指标按 0 计并照常显示 0 | 快照聚合 | M+M |
| Engagement Rate | 该行 `ΣEngagements ÷ ΣViews × 100`，**加权**（G7）；分母 0 → `"—"`（G8） | 计算 | M+M |
| Reach | 来自 Posting insight 上传截图的**图片识别**；常缺，缺失显示 `"—"`，导出默认不勾 | OCR（快照固化值） | M+M |

Note what the description cells carry that prose cannot: the exact rendered format, the rule ID behind every computed value, the null behaviour, and the fact that `Saves` is `Collects` in the database. That last one is why the doc needs a `1.4 名词解释` glossary.

### ② 前置条件、排序机制、刷新机制

| 前置条件 | 排序机制 | 刷新机制 |
|---|---|---|
| 1. 已登录 + `CAMPAIGN_REPORT` 权限；<br>2. campaign 已生成快照，否则整页空态且 Share / AI 按钮禁用；<br>3. 公开路径无登录态，org 与 campaign **一律从 token 派生，不信任入参**（G1）。 | 1. 默认 **Views 降序**；<br>2. 点列头切换升 / 降序，**全部服务端排序**，列白名单映射防注入，非白名单列不可排；<br>3. **筛选变更重置到第 1 页**；<br>4. 板块顺序固定（= 锚点顺序）。 | 1. 进入页面自动加载复合接口（一次下发九板块）；<br>2. **无实时刷新按钮**——数据每日凌晨快照更新，页顶展示 `Data as of`；<br>3. 明细分页 `page_size ≤ 50`；公开页 token + IP 基础限流；<br>4. 切换平台 chip 仅本地重取该平台聚合，不重拉整页。 |

Boundary conditions written into the same block: `Followers = 0` → View Rate 分母为 0 → `"—"`（G8），不返回 `0` / `Infinity`；单行结果 → 榜单仍渲染，条形宽度按 100% 处理；空 tier → 列仍显示，值为 `0` / `"—"`；`page_size` 传入 > 50 → 服务端 clamp 到 50 而非报错；未知 platform 值 → 归入 All，记录日志。

### ③ 状态流转

`分享链接生命周期` as inline SVG — five nodes, colour-coded per the state table:

| From | Trigger / condition | To | Guard / side effect |
|---|---|---|---|
| 无链接 | 首次打开 Share 弹窗 | `active` 有效 | 幂等：已有有效 token 直接展示，否则创建；token = `crypto/rand` 128bit |
| `active` | 点击「重新生成链接」→ 二次确认 | 新 `active` | **旧 token 立即撤销**，旧链接失效 |
| `active` | 点击「使链接失效」→ 二次确认 | `revoked` 已撤销 | 使用 `.btn.danger` |
| `active` | 超 TTL（auto） | `expired` 超时 | 系统触发，无用户操作 |
| `revoked` / `expired` | 访问该 token | `P5 失效页` | **不区分原因**——避免枚举探测 |

Render the same machine as an SVG: `无链接` neutral circle → `active` green box → `revoked` red / `expired` amber / 轮换 green, all converging on a neutral `P5 失效页` box, with the retry-style edge dashed. Follow with the grey caption `<p>` naming the popup's own interaction states (初始 / 生成中 / 复制成功 / 轮换二次确认 / 失效二次确认).

### ④ 交互操作（正常 + 异常）

1. `正常` 点击列头 → 切换升 / 降序，服务端重排，页码重置到 1。
2. `正常` 点击 **Download** → 打开 Export Report 抽屉 → 勾选数据点（默认 16 勾，4 个 OCR 项不勾）→ Confirm → **前端用已下发的全量数据生成 xlsx 并触发浏览器下载**；文件名 `campaign_report_influencers_<id>_<yyyyMMdd>.xlsx`。
3. `正常` hover **Post Link** 徽标 → 出预览卡；点击 → 打开 Post Details 抽屉（P2.1）。
4. `!` `异常` 点击非白名单排序列 → 不可排（防注入）。
5. `!` `异常` campaign 无快照 → 整页空态，Share 与 AI Summary 按钮**禁用**。
6. `!` `异常` 接口失败 → 板块级错误态 + 重试按钮；**catch 分支必须复位 loading**（有永久转圈返工史）。
7. `!` `异常` 公开页 Budget 未勾选 → **响应体本身无金额字段**（非前端隐藏），Efficiency 整块不下发。

In the rendered HTML these are `<li>` items — `1`–`3` as `<span class="marker">` + `<span class="tag normal">正常</span>`, `4`–`7` as `<span class="marker err">!</span>` + `<span class="tag err">异常</span>`. Note the shape of a good abnormal row: the trigger, the behaviour, and — where a past incident justifies the constraint — the reason in parentheses.

---

## 7. Per-page self-check

- [ ] Does the page have a number (`P0` / `P2.1`) used in its heading, in every cross-reference, and on the mockup?
- [ ] Does every field have a packed description (type / format / length / enum / display / null behaviour) and exactly one data source?
- [ ] Does every computed value cite its rule ID `（Gn）`?
- [ ] Does ② carry **validation rules, whitelists, and boundary conditions** — zero, one, max, out-of-range, first/last page, edge times — and say what resets on a filter change?
- [ ] Does ② state the refresh mechanism even when the answer is "there isn't one"?
- [ ] Is there a state table with guards, side effects, and auto-transitions, plus an **inline SVG** diagram? Zero Mermaid?
- [ ] Is ④ keyed to the mockup markers, with all 正常 numbered first and every 异常 carrying `!`?
- [ ] Did you walk the full abnormal taxonomy (empty / error / offline / invalid / over-limit / permission / concurrency / boundary / degraded source)?
- [ ] Are confirm dialogs specified for every destructive action, with exact quoted copy and a dismiss branch?
- [ ] Are double-submit/idempotency, optimistic-UI rollback, and session-expiry-with-preserved-intent handled?
- [ ] Are permissions per action tied to the role matrix, with hidden-vs-disabled decided?
- [ ] Is there an analytics row per meaningful interaction, columns matching 3.3?
- [ ] *If I were the engineer, would I still need to ask?* If yes, write the answer in.

**The whole thing in one line:** answer, in the document and ahead of time, every question an engineer would come back to ask — where this field comes from, where this state goes next, what happens at zero, what happens offline, which role can see it. Do that and you have a requirements doc engineers love.
