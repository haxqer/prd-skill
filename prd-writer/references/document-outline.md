# Document outline contract

The canonical section tree, numbering scheme, anchor ids, TOC rules, and fixed table schemas for an annotated
HTML PRD. Load this together with `references/design-system.md` before you start authoring.

Section names are given in Chinese with an English gloss. **Write the headings in the document's language** (see
*Language* in `SKILL.md`) — a Chinese PRD uses `一、产品简介`, an English one uses `1. Product Overview`. The
anchor ids, numbering formats, and table schemas below are **language-independent and never change**.

---

## 1. The outline tree

Article-derived sections are always mandatory. Sections marked **[EXT]** are gold-derived extensions that are
mandatory *when their trigger applies* — the trigger is stated on the line.

```
文档信息 / Document info                #info    .doc-head + .meta-table + closing .callout info「本版定位：」
                                                title, version, date, status, source, related docs, data source,
                                                and a self-declaration of the four-dimension paradigm

一、产品简介 / Product overview          #s1
  1.1 产品定位 / Positioning                     prose ¶ + 3-row table 我是谁 / 有什么用 / 为什么用
                                                (who am I / what is it for / why use it)
  1.2 目标用户与角色 / Users & roles              table 角色 / 场景 / 诉求 (role / scenario / need)
  1.3 核心使用场景 / Core scenario                .flow chain, circled ①…⑥ inside the node text
  1.4 名词解释 / Glossary          [EXT]         table 术语 / 含义 — MANDATORY WHEN the domain has vocabulary
                                                collisions or DB-vs-UI naming drift (gold needed 10 terms
                                                because UI「Saves」is `Collects` in the database)

二、行业与业务背景 / Background          #s2       prose ¶ naming the pain-point count, then a table
                                                痛点 / 表现 / 本产品对策 (pain / how it shows / our answer).
                                                Reframe "industry overview" as design justification.

三、版本管理 / Version management        #s3      the h2 that opens the section carries #s3 (gold: #s31)
  3.1 排期表 / Schedule                #s31b     table 阶段 / 模块 / 内容 / 依赖 [EXT: 依赖 column].
                                                Preceded by .callout info「时间为建议排期，最终以研发评估为准」.
                                                A live tracking surface engineers tick off, not a status column.
  3.2 产品设计 / Product design         #s32      ← the document's centre of gravity
    3.2.1 实体关系图（E-R）             #s321     inline SVG. Solid = business entities, dashed = derived
                                                entities; cardinality labels 1:N / N:1; grey caption <p> below
    3.2.2 用户角色权限表 / Role matrix   #s322    table.data role × capability, .tick/.cross plus qualifiers
    3.2.3 业务流程图 / Flowcharts        #s323    layered. The gold splits by ACTOR (数据管道流（系统自动）/
                                                用户操作流) rather than by zoom level; either decomposition is
                                                fine — state which one you used in an h5
    3.2.4 全局说明 / Global rules        #s324    A. 全局口径规则 G1…Gn [EXT: rule IDs, cited inline as（G7）]
                                                B. 分层 / 枚举定义 (tiers, enums, breakpoints)
                                                C. 通用控件规范 (空态 / 加载 / 异常 / 除零 / 数据时效)
  ★ 3.2.5 需求、功能、交互说明（核心）   #s325    banner-styled h4 (dark→brand gradient). P-blocks below.
      P0 · 入口 / Entry point           #p0      each P-block is one .screen:
      P1 · <页名>                       #p1        h4.screen-title → .screen-desc → 0..n .anno-wrap
      P2 · <页名>                       #p2        → .spec field → .spec cond → .spec state → .spec inter
      P2.1 · <抽屉 / 子页>               #p2d       (omit a .spec only when the dimension has nothing to say)
      P3 … Pn                          #p3…#pn
  3.3 非功能需求 / Non-functional       #s33      table 类别 / 要求. 埋点 / 性能 / 兼容性
                                                [EXT: + 安全 / 一致性 / 可观测性 / 测试]
  3.4 修改记录 / Change log             #s34      table 版本 / 日期 / 说明

四、本版变更点 / This version's deltas  [EXT] #s4   C1…Cn table — MANDATORY FOR ANY ITERATION on a shipped
                                                product. Opens with .callout info「供研发聚焦，仅列需要改动的项」.
五、待确认项 / Open questions           [EXT] #s5   table # / 问题 / 默认取值 —「均给默认值，不阻塞开工」.
                                                Every open question ships a committed default so nothing
                                                blocks development; resolved ones get
                                                <span class="pill new">已明确</span> appended to the question.
附录 A · <名称> / Appendix A           [EXT] #sb   e.g. 公开接口字段白名单 — MANDATORY WHEN there is a
                                                security or data-exposure surface (public DTO, anonymous token)
附录 B · <名称> / Appendix B           [EXT] #sc   e.g. 指标口径字典 — MANDATORY WHEN the product has
                                                formula-defined metrics
```

**Anchor scheme (fixed):** `info, s1, s2, s3, s31b, s32, s321…s325, p0…pn (+p2d for a sub-page), s33, s34, s4,
s5, sb, sc`. Extra appendices continue `sd, se`. Anchor ids are always lowercase ASCII, never localized.

---

## 2. Numbering scheme (normative)

| Level | Format | Example |
|---|---|---|
| Top level | Chinese numeral + `、` (or `1.` in an English doc) | `一、产品简介` · `四、本版变更点` |
| Second level | `N.N ` — space, no punctuation after the number | `1.4 名词解释` · `3.1 排期表` |
| Third level | `3.2.N` | `3.2.5 需求、功能、交互说明（核心）` |
| Lettered sub-block | `A. / B. / C.` inside an `h5` | `A. 全局口径规则（单一事实源…）` |
| Pages | `P0…Pn`, sub-pages `P2.1` | `P2.1 · Post Details 抽屉（Post Link 列交互）` |
| Modules (inside ①) | `M1…Mn` | `M6 · Posting Timeline` |
| State machines (inside ③) | **no identifier** — a bare `h5` naming the machine | `AI Summary 状态机（五态）` |
| Global rules | `G1…Gn` + short name | `G7 比率加权` · `G10 时区` |
| Change points | `C1…Cn` | `C3 · Influencer 页 Geo 筛选` |
| Open questions | plain `1…n` | rows of §五 |
| Appendices | `附录 A · <名称>` as an `h2.sec` | `附录 A · 公开接口字段白名单（PublicCampaignReportRsp）` |

`·` (middot) is the **universal separator between an identifier and its name** — `P2.1 · Post Details 抽屉`,
`M1 · Overview 指标卡`, `附录 A · 脱敏白名单`. Full-width `（）` for all inline qualifiers in a Chinese doc.

**`P-01` style is FORBIDDEN.** It was the failed document's form. It is inconsistent with the corpus and, more
importantly, it structurally blocks sub-pages: there is no sane `P-01.1`. Use `P0`, `P1`, `P2`, `P2.1`.

The `P` prefix is deliberately reused in 3.1 排期表 for delivery phases (`P4 / Share + 公开页`). That is the one
allowed collision — schedule phases and page blocks never appear in the same table.

### 2.1 State machines are named, not numbered

**Every state machine gets its own `h5` naming it.** This is the one identified construct that carries *no*
letter-plus-number code: the gold has six machines across four `③ 状态流转` blocks and numbers none of them.
Do not invent an `S1…Sn` scheme — the heading text *is* the identifier, and `·` never appears in these headings
because there is no identifier to separate from the name.

One `.spec.state` block holds **as many `h5` machines as the page actually has**, and each `h5` owns everything
under it until the next `h5`. Every machine carries **exactly one** visual, and the `h5` is its caption:

- **`.diagram > svg`** when the machine branches, loops, or has a retry/derived edge (`页面加载状态`,
  `AI Summary 状态机`, `分享链接生命周期`).
- **`.flow`** chain when the machine is strictly linear or a simple fan-out (`表格加载状态`, `导出状态`,
  `token 校验闸门`).

A `| From | Trigger / condition | To |` table may accompany the visual when the transitions carry conditions too
wordy to letter onto an edge; it belongs **under** that machine's `h5`, never as a substitute for the `h5`. The
gold ships the visual alone in all six machines. What is always wrong is an **unlabelled** table sitting directly
under the `③ 状态流转` label — it leaves the reader unable to tell where one machine ends and the next begins.

**Naming shape.** Name the *thing that changes state*, not the page it lives on, so the h5 outline reads as a
state inventory: `页面加载状态` / `AI Summary 状态机` / `分享链接生命周期` / `token 校验闸门` / `导出状态`. Two
optional qualifiers, both in full-width `（）`:

- **Scope**, when one page runs several machines and the heading alone would be ambiguous —
  `页面加载状态（Overview 整页）`.
- **Arity**, when the state count is itself contractual and an engineer must implement exactly that many —
  `AI Summary 状态机（五态）`. The gold uses arity on 1 machine of 6; it is a deliberate emphasis marker, **not**
  a suffix to append to every heading. If the count is obvious from the diagram, leave it off.

These `h5`s are **not** TOC entries (§3) — only sections and P-blocks are.

---

## 3. TOC construction rules

Three levels, matching the design system's classes:

- bare `<a>` = lv1 — top sections and `3.x`
- `.lv2` = the `3.2.x` tier
- `.lv3` = the P-blocks

Plus non-link `.grp` dividers, named with the Chinese numeral and a short label: `一 · 概述` / `三 · 版本管理` /
`附`. The core section gets `<b>★ …</b>` inside its anchor.

**Labels are ABBREVIATIONS, not verbatim heading dumps.** `3.2.2 角色权限表` for a heading that actually reads
`3.2.2 用户角色权限表`; `附录 A · 脱敏白名单` for `附录 A · 公开接口字段白名单（PublicCampaignReportRsp）`. A TOC
entry has ~200px to work in.

**Never emit duplicate TOC labels.** This is a hard rule, not a preference. The failed document had 20 of its 58
entries ambiguous — five entries reading `元素标注图`, four reading `① 字段…` — disambiguated only by invisible
`-1`/`-2` anchor suffixes, which makes the sidebar useless for navigation. If two entries would read the same,
the label is wrong: qualify it with the page it belongs to (`P2 标注 · Influencer 表格`), or the entry should not
be in the TOC at all. Annotation blocks and `.spec` blocks are **not** TOC entries — only the sections and
P-blocks listed in §1 are.

---

## 4. Fixed table schemas

Never invent columns for these. Header wording is part of the contract.

| Table | Schema |
|---|---|
| `.meta-table` (in `.doc-head`) | row 1 `需求来源 / 文档状态`; row 2 `关联文档 / 数据源` (paths in `<code>`); row 3 `编写范式` with `colspan="3"`, spelling out ①②③④ in their four token colours |
| 排期表 3.1 | `阶段 / 模块 / 内容 / 依赖` |
| 全局口径规则 3.2.4A | `编号 / 规则` — 编号 cell is `G<n> <短名>` |
| 修改记录 3.4 | `版本 / 日期 / 说明` |
| 本版变更点 四 | `# / 变更点 / <旧版>现状 / <本版>（来源）/ 影响面` — `#` cell is `C<n>` |
| 待确认项 五 | `# / 问题 / 默认取值` — every row has a committed default |
| Annotation legend | 4 columns; headers are fixed strings — copy them from *Fixed strings* in `references/design-system.md`, which is the only place they are written down. First column always `width:52px` |
| ② spec block | single-row 3-column `前置条件 / 排序机制 / 刷新机制`, each cell a `<br>`-separated numbered list |
| ① module table | `字段 / 说明（含格式）/ 数据来源`, plus a `范围` column when scope varies per field |
| 权限表 3.2.2 | `能力` + one column per role, cells `class="c tick"` / `class="c cross"` |
| 非功能需求 3.3 | `类别 / 要求` |
| 名词解释 1.4 | `术语 / 含义` |
| 行业背景 二 | `痛点 / 表现 / 本产品对策` |

---

## 5. Prose conventions

Terse, declarative, engineer-facing. No marketing language, no hedging, no first person. Short sentences,
clause-chained.

- **Bilingual by design.** Product names, metric names, entity names, and code identifiers stay in their original
  English (`Overview`, `Engagement Rate`, `master post`, `snapshot`); only the connective tissue is in the
  document's language. Identifiers always go in `<code>`.
- **`<b>` is surgical** — on the one word a developer would otherwise skim past: `<b>禁止</b>`, `<b>仅 master</b>`,
  `<b>纯前端</b>`.
- **`「」`** wraps literal on-screen strings: `空态「No influencers found」`. `"—"` is the null placeholder.
- **`——`** introduces an explanatory aside.
- **`→`** carries causality in prose, not only in diagrams: `未配置 → 显示 "—"`, `点击 → 打开 Share 弹窗（P3）`.
- **Every data statement ends with its rule code** `（Gn）` so the single source of truth is one hop away.
  Cross-references are by code, never by section number: `（G7 加权）`, `（§3.2.4B）`, `（见 <a class="inline"
  href="#p2d">P2.1</a>）`.
- **Prohibitions carry their reason in parentheses**: `<b>禁止</b>复用 <code>EngRate</code>（隐式口径且 IG 不算）`.
- **Constraints justified by a past incident are worth annotating**: `（有永久转圈返工史）`,
  `（大小写混存是已知坑）`. They stop an engineer from "simplifying" the constraint away.
- **Formula-then-constraint** is the standard shape for a metric: `= <公式>；<边界条件> → <行为>`.
