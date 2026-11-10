# Verification record

The [agent-loop verification](#agent-loop-verification-2026-11-06) is the latest feature and all-chapter responsive check. The [large tool-output clarification](#large-tool-output-clarification-2026-11-05) and [readability acceptance](#current-readability-acceptance) remain historical records, not claims that every earlier integration check was repeated. The permanent publication is **https://chen-gdp.github.io/deepagents-docs/**; older Quick Tunnel URLs below are temporary historical previews.

## Revision and environment

- Upstream repository: https://github.com/langchain-ai/deepagents
- Reviewed revision: `c4e2811312718e98b1465b6e67c34997ca72c793`.
- Actual local clone: `/tmp/deepagents-study-source`.
- Preview: `http://127.0.0.1:8793/`; served from this directory with `/home/christian/miniconda3/bin/python`.
- Atlas generation and integrity probes used the existing Conda Python 3.12.12.
- Diagram/capture helpers used `/tmp/deepagents-diagram-venv/bin/python`, whose `sys.base_prefix` is `/home/christian/miniconda3`. Pillow and Playwright were installed only in that isolated Conda-based environment, not in system Python.
- Browser checks used real Chromium through the browser tool and the Conda-based Playwright environment. These were ad-hoc functional/visual checks, not an upstream test-suite run.

## Agent-loop verification (2026-11-06)

### Runtime and source evidence

- New chapter: [`sdk-agent-loop`](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-agent-loop), 12 sections. Total guide: 24 chapters, 117 sections, 604 valid atlas citation entries.
- Unchanged Deep Agents source pin: `c4e2811312718e98b1465b6e67c34997ca72c793`, installed from the actual local clone at `/tmp/deepagents-study-source/libs/deepagents`.
- Conda CPython 3.12.12 created this repository's `.venv`. Exact runtime: Deep Agents 0.7.32; LangChain 1.4.8/core 1.7.6; LangGraph 1.2.20/prebuilt 1.1.1; checkpoint 4.3.1; Pydantic 2.14.3. Full resolved versions: [`requirements-verification.txt`](requirements-verification.txt).
- [`verify_agent_loop.py`](verify_agent_loop.py) executed **52 cases: 52 passed, 0 failed**. Model responses are deterministic fixtures; graph execution, tool handlers, schema parsing, checkpoints, human-review decisions, limits, and owned async-tool cleanup are real. Each case records whether it executes `create_deep_agent` or isolates `create_agent`.
- [`evidence/agent-loop-runtime.json`](evidence/agent-loop-runtime.json) records model inputs/counts, correlated messages, real tool effects, graph topology, pending destinations, exceptions, and rubric observations. `max_concurrency=1` makes ordered assertions deterministic; it is not a production ordering guarantee.
- The installed LangChain factory byte-matches release commit `5dcec1858191a6b54cd843dd8e54d856e2e007cc`. The retained [dependency source](evidence/langchain-1.4.8-agent-factory.py) has SHA-256 `cc4a7d9a620224558c4eddd4e13edc988a9ac9e328b7a67deeb71ed2c5ec5174`. The harness strictly checks complete-file hashes for that factory, the Deep Agents constructor, and rubric middleware—not every installed module.

Measured distinctions incorporated into the chapter:

1. Text such as “done,” an empty assistant response, provider `finish_reason`, normalized valid calls, and malformed `invalid_tool_calls` are separate observations. A malformed-only response can end the current invocation; startup repair happens on a later invocation.
2. Ordinary tool results return to the model. All-direct batches can end, mixed direct/ordinary batches continue, and a tool's `Command(goto=END)` alone does not suppress the factory's tools-to-model edge.
3. Schema-only ToolStrategy validation/multiple-output recovery can retry. **Mixed schema errors plus ordinary work ended without retry in both probes, with `structured_response=None`.** Corrective schema receipts defaulted to `status="success"`, satisfying the separate tools-router exit guard. Native-format invalid parsing raised rather than implicitly retrying.
4. Middleware jumps and after-agent hooks can change the apparent exit. Call limits have distinct end/error/continue policies; rubric completion has explicit satisfied/failed/cap/grader-error outcomes. Private rubric fields were inspected in checkpoint values, not assumed present in `invoke()` output.
5. Approval/edit/reject/respond pause and resume the same checkpointed thread. Errors, recursion limits, caller timeout, and cancellation are not successful END; pending nodes and completed external effects can remain.
6. Inline child completion returns a correlated report to a continuing parent. Real remote background reconciliation, provider-hosted tools, transport disconnects, provider-side schema enforcement, and external-side-effect cancellation remain unexercised external boundaries.

The deliberate grader-unavailable probe logs its expected exception; its asserted outcome passed. No upstream model/provider/network integration-suite pass or universal task-success claim is made.

### Website exercises

Preview origin: `http://127.0.0.1:8794/`, served from this repository with `/home/christian/miniconda3/bin/python -m http.server 8794 --bind 127.0.0.1`.

| Check | Observed result |
| --- | --- |
| All four content collections | Valid JSON; unique chapter/section IDs; all 604 citation paths and inclusive ranges valid |
| Cited source bundles | All embedded texts in the ten referenced bundles matched manifest SHA-256 values |
| Chapter examples | All 14 blocks parsed: 12 Python blocks with `ast.parse`, two Bash blocks with `bash -n` |
| Application syntax | `node --check` passed for `app.js`, `chapter-diagrams.js`, `syntax.js`, and `walkthrough.js` |
| Probe implementation | Ruff E/F/I/C901 passed with 120-column lines and maximum complexity 15; formatter reported unchanged after the final extension |
| All 24 chapters | 48 rendered views at 1440px and 390px: expected sections, 16px reading font, no document overflow, decoded diagrams, code syntax tokens, mobile table cards |
| Final agent-loop content | Rechecked at 1440px, 390px and 360px; three decoded diagrams, correct compact selection, no overflow, nine structured-output rows with retained header associations |
| Navigation/search | Desktop `return_direct` result selected the direct-return section; mobile menu selected state and new loop chapters and closed; Ctrl+K found malformed-call coverage |
| Search dismissal | A first Escape cleared the nonempty native search field; a second Escape dismissed the dialog |
| Source permalink | New construction citation opened `graph.py` and highlighted all 23 requested lines, 1008–1030, with Python syntax tokens |
| Code copying | All four new Python blocks copied byte-for-byte; automation clipboard permission overrides were cleared between copies |
| Theme/reference | Light/dark/light worked; Python tokens retained five distinct syntax colors in dark mode; source-only boundary disclosure opened |
| Existing execution lab | Selected filesystem step 2; route became `scenario=filesystem&step=1` and state contained the expected user message |
| Page exceptions | None during the recorded exercises; one aborted old diagram request occurred during rapid chapter navigation, with all current diagram images subsequently decoded |

Browser measurements: [`evidence/agent-loop-browser.json`](evidence/agent-loop-browser.json).

Visual/manual evidence inspected:

- [Desktop compiled topology in the actual article](evidence/agent-loop-desktop.png), 1440px viewport.
- [Compact compiled topology and caption](evidence/agent-loop-mobile-graph.png), actual 390px layout, component crop from a taller viewport so the sticky header does not obscure the figure.
- [Mobile mixed-error scenario card](evidence/agent-loop-mobile-scenarios.png), 390×844 viewport.

### Diagram validation: mandatory two passes

Evidence classification: geometry/margin scripts provide script-backed supporting measurements; semantic/composition judgments are script-assisted and visual/manual-only. Evidence sources were all six rendered PNG/fit-check pairs, plus the actual article captures above—not source text alone.

| Desktop/mobile pair | Composition pass: G1, G2, G5, G6, G8, G9 | Mechanical pass: G3, G4, G7 |
| --- | --- | --- |
| `agent-loop-routing` | All pass | All pass |
| `agent-loop-compiled` | All pass | All pass |
| `agent-loop-outcomes` | G1/G2/G6/G8/G9 pass; G5 not applicable to a non-directional comparison | G7 passes; G3/G4 not applicable without connectors |

Each stem under [`diagrams/`](diagrams/) includes editable `.svg`, 2× `.png`, intended-width `.fitcheck.png`, `.heuristics.txt`, `.margin.txt`, and `.fitcheck.margin.txt`; compact stems end in `-mobile`. Fit widths are 660px and 288px. The compiled graph has the measured six nodes/eight edges; labels shorten the two hook names, mapped explicitly in its caption. It is not a universal topology for every configuration.

Retained helper findings, manually resolved from rendered images:

- G4/G5/G8 -> ordinary result-to-model return -> required execution cycle exceeds the generic dogleg heuristic; routed separately, without crossings -> informational.
- G4 -> compiled model self-route -> offset top attachment distinguishes reentry from startup; no merged shafts or obscured node -> informational.
- G4/G5/G8 -> compiled alternate routes -> long doglegs preserve actual conditional bypass/return edges rather than inventing a bus -> informational.
- G1 -> desktop compiled spine -> measured 19.5% left whitespace preserves the centered spine and alternate lanes; fit text remains at least 21px -> informational.

All applicable gates pass. No unresolved red/yellow defect remains. Geometry warnings alone were not treated as proof of a defect or as proof of readability.

## Large tool-output clarification (2026-11-05)

Public preview: **https://doctors-receptor-suzuki-reality.trycloudflare.com/**. The preceding Quick Tunnel stopped resolving and reported `Unauthorized: Tunnel not found`; a replacement HTTP/2 tunnel registered and serves the unchanged Conda-Python origin. Both processes were left running. The public hostname is temporary.

### Scope and source grounding

- Expanded `sdk-filesystem-text-offload` into a worked 400,000-character / approximately 100K-token example, with an explicitly assumed 100K model profile. Token estimates are distinguished from actual tokenization and from the earlier 100,000-character scale.
- Added a Python-highlighted paging argument block, five numbered execution steps, a size comparison, and visible cautions about full-result summarization, exhaustive reading, application memory, failed writes, disabled eviction, non-text media, and storage lifetime.
- Added a cross-linked budget example in `sdk-context-overflow`: 100,000 advertised input tokens, 12,000 configured output tokens, and 5% headroom produce an 83,000-token usable input budget. These are illustrative settings, not universal provider limits.
- Preserved all 23 chapter IDs and 105 section IDs. Added six pinned implementation citations and extended the eviction-exclusion citation through `delete`.

### Exercised checks

| Check | Observed result |
| --- | --- |
| Content and citation validation using Conda Python | All three chapter JSON files parsed; all 572 citation paths/ranges valid against the pinned atlas; section IDs unique |
| Added source references | Six added citation entries matched SHA-256-verified pinned source blobs |
| Example syntax | All ten full snippets parsed: eight Python with `ast.parse`, two Bash with `bash -n`; not model execution |
| Internal chapter references | All four authored chapter/section links resolved to existing content |
| Changed chapters at 1440×1080 and 390×844 | Both offload and context chapters rendered; no document-level overflow |
| New comparisons | Three offload rows and four budget rows; mobile tables fit at 344 CSS px and expose visible field labels; offload cells retain header associations |
| Offload flow and Python block | Five numbered steps; 15 syntax-token spans; Copy placed the exact argument block on the browser clipboard |
| Reference material | Existing offload disclosure opened through its control |
| Linked explanation | Followed offload → context, context → offload, and offload → state-storage links |
| Search | `100K` found both revised sections; selecting the offload result closed the dialog |
| Source atlas | Followed the new preview/paging citation to `_message_eviction.py`, lines 31–52, and observed its source content |
| Page exceptions | None recorded during these browser exercises |
| Published chapter integrity | HTTP 200; public `content/sdk.json` matched local bytes, SHA-256 `b11f57d9fc4eb21c899548fd0540caaec18333609cc96af73639c2b6219aaa26` |

Visual evidence inspected:

- [Desktop offload explanation](evidence/large-output-desktop.png)
- [Mobile size-comparison cards](evidence/large-output-mobile.png)
- [Mobile input-budget example](evidence/large-output-budget-mobile.png)

These were ad-hoc website and content checks, not a permanent test suite or a live 100K-token tool/model run. No diagrams, application JavaScript, or styles changed; earlier diagram scores were not rerun. The browser tab was closed after verification. No commits or GitHub Pages deployment were made.

## Content and provenance checks

| Check | Observed result |
| --- | --- |
| Chapter identifiers and section identifiers | Unique |
| Authored chapter/section counts | 23 chapters / 105 sections |
| Chapter source citations | All 572 paths and inclusive line ranges valid after the large tool-output clarification |
| Walkthrough source citations | All 39 paths and inclusive line ranges valid |
| Embedded source integrity | All 1,705 text blobs matched SHA-256 metadata from the pinned Git archive |
| Python source coverage | All 1,233 `.py` files in the pinned Git tree were present |
| Python indexing | 30,338 definitions; zero parse diagnostics |
| Conda Python 3.12 compatibility probe | Python 3.14 bare exception tuples indexed without modifying source content or definition line numbers |
| Source export behavior | Reads immutable Git archive blobs; does not read mutable working-tree/index source |
| Independent factual checks | SDK/backend/application claims reviewed against implementation, metadata and representative tests; identified corrections integrated |

The revised content mixes short prose, numbered explanations, and comparison tables. Section citations support implementation explanations; they are not a guarantee that every sentence or every upstream behavior has been exhaustively proved.

## Initial browser exercises

| Surface | Exercised behavior | Result |
| --- | --- | --- |
| All 23 chapters, desktop | Correct heading, expected section counts, 540 rendered source links, no document-level horizontal overflow | Passed |
| All 23 chapters, 390×844 | Correct chapter rendering, no document-level horizontal overflow, no page errors | Passed |
| Search | Search `checkpoint`, follow a result to its section, close the dialog after selection | Passed; 22 matching sections observed |
| Keyboard search | `Ctrl K` opens; Escape closes | Passed |
| Skip link | Keyboard activation focuses existing main content without changing the hash route | Passed |
| Theme | Toggle light → dark → light | Passed |
| Mobile navigation | Open, select a chapter, close after selection; Escape restores focus; collapsed sidebar is hidden from keyboard navigation | Passed |
| Copy control | Copy a chapter code block | Passed; `Code copied` observed |
| Execution lab | Visit all 7 file-write, 5 approval and 6 delegation steps | Passed |
| Walkthrough keyboard | Activate Next repeatedly with Enter; focus survives replacement; Next disables at the final step | Passed |
| Numeric route boundary | Fractional walkthrough index normalizes to an integer | Passed |
| Approval projection | All four decisions, including `respond`, visible in the relevant state | Passed |
| Source citation | Follow a chapter citation; correct pinned source and highlighted range | Passed; 62 highlighted lines for a 62-line citation |
| Atlas search/filter | Search `DeepAgentRuntime`, open its Talon source, use package and test filters | Passed |
| Definition jump | Select `create_deep_agent` at line 289 | Passed |
| Source paging | Advance from lines 264–613 to 614–963 | Passed; bounded 350-line window |
| Source numeric boundary | Fractional requested lines render integer line labels | Passed |
| Selected-line visibility | Highlighted line 289 positioned about 80 px below the source viewport top | Passed |
| Empty file | Open `libs/deepagents/tests/__init__.py` | `Empty file · 0 bytes`; no invalid range label |
| Malformed route | Open `#/chapter/%` | Not-found surface rendered without a page error |
| Narrow diagram panels | Panel scrolls horizontally via keyboard; document itself does not overflow | Passed |

Screenshots inspected:

- [Desktop home](evidence/desktop-home.png)
- [Desktop chapter](evidence/desktop-chapter.png)
- [Source atlas](evidence/desktop-source.png)
- [Execution walkthrough](evidence/desktop-walkthrough.png)
- [Mobile home](evidence/mobile-home.png)

A stale in-memory content snapshot was found during authoring and resolved by reloading before the full chapter sweep. Browser-tool raw source-page screenshot calls timed out; the source and walkthrough captures were subsequently produced successfully using Conda-based Playwright. No source-view interaction failure or page exception was observed in those checks. The screenshot limitation is not reported as a passed browser-tool capture.

## GDP Labs diagram validation

**Evidence classification:** geometry/margins are script-backed; G1/G2/G4/G5/G6/G7/G8 are script-assisted where perception is required; architecture meaning and cold-read G9 are visual/manual-only. Visual evidence is the latest rendered PNGs, cropped target-width fit-check PNGs, and live website inspection—not source-only approval.

**Target:** web article diagram at 660 CSS px. The overview also appears at a smaller hero width, with 26 px source detail text and a 360 px minimum image width. Narrow screens use local horizontal scrolling, with an explicit cue and keyboard-focusable panels, rather than unreadably shrinking the diagrams.

**Profile:** canonical `profiles/compact-flow.json`; helper `--fit-width 660`. No relaxed request-specific profile was used.

### Evidence bundle

| Diagram | Editable source | Rendered image | Target-width preview | Helper outputs |
| --- | --- | --- | --- | --- |
| Layering | [layers.svg](diagrams/layers.svg) | [layers.png](diagrams/layers.png) | [layers.fitcheck.png](diagrams/layers.fitcheck.png) | [heuristics](diagrams/layers.heuristics.txt), [margins](diagrams/layers.margin.txt), [fit margins](diagrams/layers.fitcheck.margin.txt) |
| Tool loop | [execution.svg](diagrams/execution.svg) | [execution.png](diagrams/execution.png) | [execution.fitcheck.png](diagrams/execution.fitcheck.png) | [heuristics](diagrams/execution.heuristics.txt), [margins](diagrams/execution.margin.txt), [fit margins](diagrams/execution.fitcheck.margin.txt) |

The canonical fit-check helper preserves a 1,200 px viewport height. Its unused bottom-only whitespace was cropped with Pillow, preserving the 660 px displayed diagram width and 16 px wrapper padding. Final previews are 692×522 and 692×462. All measured final-preview margins are below 10%; all final SVG heuristic warning buckets are zero. The helpers recognized both layer connectors and all four loop connectors, including the return route.

### Pass 1 — Composition

| Rule | Layers | Execution loop | Acceptance evidence |
| --- | --- | --- | --- |
| G1 — Fit/readability | Green | Green | Latest fit previews inspected; legible labels, efficient crop, web minimum widths |
| G2 — Header/text economy | Green | Green | One layer label per card; one harness-boundary title; detail stays outside visuals |
| G5 — Route balance | Green | Green | Centered straight layer arrows; local forward path and secondary return route |
| G6 — Color semantics | Green | Green | Restrained canonical blue/neutral palette; solid directional connectors; labels carry meaning |
| G8 — Alignment/spacing | Green | Green | Stable rails, consistent role heights, no overlap/rail/spacing warnings |
| G9 — Semantic completeness | Green | Green | Layer diagram shows construction/runtime layering, not separate services. Loop shows proposed calls, harness control, actual tool effects, and results returning to the next decision. Backend/API connector is request/response, not a claim of universal sandboxing. |

### Pass 2 — Mechanics

| Rule | Layers | Execution loop | Acceptance evidence |
| --- | --- | --- | --- |
| G3 — Geometry/arrowheads | Green | Green | Straight/orthogonal routes, compact solid markers; zero diagonal/marker warnings |
| G4 — Anchoring/clearance | Green | Green | Anchored endpoints, no title/label collisions, traceable return path; helper and visual inspection |
| G7 — Containment/padding | Green | Green | No overflow warnings; text visibly contained in latest fit-check images |

### Resolved findings from validation rounds

- `G7 -> layer and execution labels -> inherited text anchoring was invisible to the heuristic parser, and several execution labels were too long -> high; resolved with explicit anchors and shorter labels, then re-rendered and checked.`
- `G8 -> layer cards -> unequal heights for equal-role two-line cards -> medium; resolved with equal heights.`
- `G8 -> execution boundary -> unused lower container slack -> medium; resolved by tightening the boundary and return route.`
- `G1 -> fit-check previews -> helper viewport introduced excessive blank space below the diagram -> medium; resolved by bottom-only crop, preserving target width, and fresh margin reports.`

No red/yellow findings remain in the latest artifacts. These rules validate visual communication; source grounding is a separate check.

## Authored-code checks

Executed from this directory:

```bash
node --check app.js
node --check walkthrough.js
ruff check build_source_index.py
ruff format --check build_source_index.py
ruff check --select C901 build_source_index.py
```

All passed after the exporter import-order fix. The exporter itself was run successfully against the actual clone and produced the delivered manifest/bundles. The integrity and compatibility probes were executed with Conda Python without importing upstream application code.

## Limits

- No Deep Agents upstream unit, integration, evaluation, model-provider, sandbox-provider, MCP-server or deployed-service suite was executed. No pass is claimed for those systems.
- Walkthrough values and code snippets are labeled illustrative; the lab is not a live agent or a fabricated execution transcript.
- The guided text is not a line-by-line explanation of every source file. Full tracked Python implementation and test source is available in the atlas for deeper investigation.
- The pinned revision does not update automatically with upstream `main`.
- The origin binds only to loopback. A temporary, unauthenticated Cloudflare Quick Tunnel exposes the site publicly while both processes and this workstation remain running; this is not a production deployment or uptime guarantee.

## Initial readability and syntax-highlighting revision

### Content checks

- All 23 chapters / 105 sections retained their IDs, titles, group, ordering, metadata and existing citations.
- The native-streaming section gained two verified implementation references for the explicit event-contract table. Chapter citations now total 542; the 39 walkthrough references are unchanged.
- All four authored example blocks are text-identical to the previous version: three Python, one Bash.
- 101 sections now include numbered explanations. Fifteen comparison tables remain across the chapter collections; the four sections without ordered lists use reference/comparison tables.
- The longest explanatory paragraph measured 55 words; the longest numbered point measured 70 words. These are structure/length checks, not a readability certification by themselves.
- Manual spot checks compared the original and revised pagination, exact-edit, compaction/recovery, backend-capability and application-process descriptions. Combined code tokens such as `next_offset=end_line` and `file_path=None` retain the original edge-case semantics.

### Exercised syntax behavior

- All four authored code blocks rendered colored tokens with their explicit language labels; every original example text matched the displayed code after highlighting.
- All 18 walkthrough states rendered as highlighted, parseable JSON rather than being mislabeled Python.
- Python source view retained 350-line windows, definition/line links, and highlighting after paging.
- A window beginning inside `graph.py`'s multiline docstring kept nonblank line 403 inside a string token, not keyword tokens.
- A source round-trip probe preserved newlines, Unicode non-breaking space, Python f-string text, and `<script>` literally without introducing a script element.
- The largest Python source file, `libs/code/deepagents_code/app.py` (1,439,000 bytes / 33,320 lines), rendered the requested 350-line colored window with 843 token spans. This is not a performance benchmark or latency guarantee.
- Code copying still produced the observed `Code copied` confirmation through the public HTTPS site.
- Public source inspection confirmed 350 rendered lines, 485 token spans and the expected docstring token. A timed selector wait on that public source view expired once; subsequent direct inspection confirmed it loaded without a page exception. Large package bundles can take longer to transfer through a temporary tunnel.
- `node --check` passed for `app.js`, `syntax.js`, `chapter-diagrams.js`, `walkthrough.js`, and the vendored grammar bundle.

### Revised website smoke checks

Fresh Chromium scans at both 1440×1000 and 390×844 visited every chapter:

- 23 chapters and all 105 section containers rendered at each width.
- All five newly embedded chapter diagrams loaded at each width.
- No document-level horizontal overflow and no page errors were observed.
- The public Cloudflare route was exercised across all chapters, event-contract content, copying, and colored Python source.

Latest visually inspected captures:

- [Readable desktop chapter](evidence/readable-chapter.png)
- [State/data-flow chapter](evidence/state-flow-chapter.png)
- [Python highlighting](evidence/python-highlight.png)
- [Readable mobile chapter](evidence/mobile-readable-chapter.png)

### New diagram evidence and two-pass scoring

Evidence classification: script-backed geometry/margins; script-assisted fit, padding and layout; visual/manual-only semantic cold-read. Visual evidence is each latest rendered PNG and 660 px fit-check plus the live chapter surface.

All new diagrams use the canonical compact-flow profile with `--fit-width 660`. Fit previews use 8 px wrapper padding; the helper's unused viewport below the image was cropped without resizing the displayed diagram. Final margins are below 10%, and all SVG heuristic warning buckets are zero.

| Diagram | Source | Render | Fit check | Helper evidence |
| --- | --- | --- | --- | --- |
| Construction | [SVG](diagrams/construction.svg) | [PNG](diagrams/construction.png) | [Fit](diagrams/construction.fitcheck.png) | [Geometry](diagrams/construction.heuristics.txt), [margins](diagrams/construction.margin.txt), [fit margins](diagrams/construction.fitcheck.margin.txt) |
| State/data cycle | [SVG](diagrams/state-flow.svg) | [PNG](diagrams/state-flow.png) | [Fit](diagrams/state-flow.fitcheck.png) | [Geometry](diagrams/state-flow.heuristics.txt), [margins](diagrams/state-flow.margin.txt), [fit margins](diagrams/state-flow.fitcheck.margin.txt) |
| Inline delegation | [SVG](diagrams/delegation.svg) | [PNG](diagrams/delegation.png) | [Fit](diagrams/delegation.fitcheck.png) | [Geometry](diagrams/delegation.heuristics.txt), [margins](diagrams/delegation.margin.txt), [fit margins](diagrams/delegation.fitcheck.margin.txt) |
| Backend routing | [SVG](diagrams/routing.svg) | [PNG](diagrams/routing.png) | [Fit](diagrams/routing.fitcheck.png) | [Geometry](diagrams/routing.heuristics.txt), [margins](diagrams/routing.margin.txt), [fit margins](diagrams/routing.fitcheck.margin.txt) |
| Code process split | [SVG](diagrams/code-processes.svg) | [PNG](diagrams/code-processes.png) | [Fit](diagrams/code-processes.fitcheck.png) | [Geometry](diagrams/code-processes.heuristics.txt), [margins](diagrams/code-processes.margin.txt), [fit margins](diagrams/code-processes.fitcheck.margin.txt) |

**Pass 1 — Composition:** G1, G2, G5, G6, G8 and G9 are green for all five new diagrams. Labels are legible at fit width; headers and category colors are restrained; related boxes are aligned; each figure answers a distinct question. The state cycle is explicitly conceptual rather than the compiled graph topology, routing explicitly chooses one branch, and the backend in the Code figure is not falsely labeled a separate process.

**Pass 2 — Mechanics:** G3, G4 and G7 are green for all five new diagrams. Routes are straight/orthogonal with compact markers, anchored endpoints and no label collisions or text overflow in the final renders.

Resolved validation findings:

- `G5 -> state-cycle return -> long two-bend return dominated a vertical layout -> medium; replaced by a compact clockwise cycle with direct connectors.`
- `G8 -> routing rows -> unequal phase spacing exaggerated the branch gap -> medium; balanced the row gaps and regenerated the render.`
- `G1 -> state and Code fit previews -> wrapper/canvas margin slightly exceeded 10% -> low; tightened fit wrapper padding, preserved 660 px diagram width, and reran margin checks.`

No red/yellow findings remained in that 660 px diagram set. The original layer/tool-loop figures were unchanged by that formatting pass; current narrow-screen acceptance follows below.

## Current readability acceptance

### Content and factual validation

- All 23 chapters were meaningfully revised; all 105 section IDs remain. Existing citation targets and substantive baseline coverage were retained. Sections were reordered where necessary to teach the concept before its implementation.
- The state chapter now defines state, reducers and checkpoints before delta-channel mechanics, includes message-ID before/after examples, and moves context projections earlier. Streaming introductions are separated from advanced adapter contracts.
- Concrete illustrative examples cover file reads/offload, child inputs and reports, background thread/run identities, skill disclosure, compaction, storage lifetimes, routing, permissions, configuration precedence and application ownership.
- Independent source-based reviews covered all 105 sections. Integrated corrections include invocation-time virtual-file seeding, shared checkpoint-storage requirements across ACP rebuilds, headless shell rules versus exposed file tools, and the content-builder YAML mapping shape.
- All 566 final chapter citations have existing source paths and valid inclusive line ranges. The upstream pin and source atlas were not changed.
- Seven Python examples passed Conda Python AST parsing; two Bash examples passed `bash -n`. These were syntax-only checks, not model executions.

### Actual public website verification

Public preview: **https://higher-preferred-postings-generation.trycloudflare.com/**.

The old temporary hostname stopped resolving and its tunnel failed to reconnect after a network interruption. A replacement HTTP/2 tunnel registered successfully and serves the existing Conda-Python origin at `127.0.0.1:8793`. The replacement tunnel and origin were left running. Quick Tunnels remain temporary and require these processes and network connectivity.

| Exercise | Observed result |
| --- | --- |
| All chapters at 1440×1080 and 390×844 | 46 successful chapter views; expected section IDs; 16 px chapter prose; no page exceptions or document overflow |
| All 26 comparison tables | No table overflow; header associations and visual field labels present; narrow-screen rows become readable cards |
| All nine example blocks | Highlighted tokens and original authored text preserved at both widths |
| Seven diagram topics at 360 px and 768 px | All 14 views selected the compact source, preserved its aspect ratio, and fit without panel or document overflow |
| Reference disclosure | Opened and closed through its actual control |
| Search | Searched `memory_contents`, followed the result to the memory section, and observed dialog closure |
| Theme | Toggled dark and light |
| Copy | Clipboard text exactly matched the complete Python constructor example |
| Mobile navigation | Selected a chapter and observed the menu collapse |
| Narrow table semantics | Table, rowgroup, columnheader and cell roles retained; duplicate visual labels are hidden from the accessibility tree |
| Source citation | Opened `graph.py` and observed all four requested source lines highlighted |
| Execution lab | Exercised all 18 steps across the three illustrative scenarios |
| Public asset integrity | All 13 changed application/content/compact-SVG assets matched local SHA-256 content |
| Authored JavaScript | `node --check` passed for app, diagram metadata, syntax helper and walkthrough modules |

Full browser captures/contact sheets were inspected across all chapters. Representative durable captures:

- [Concept-first state introduction](evidence/revised-state-desktop.png)
- [Complete mobile state cycle](evidence/revised-state-mobile.png)
- [Mobile provider-comparison cards](evidence/revised-table-mobile.png)
- [Highlighted example with seeded virtual file](evidence/revised-constructor-code.png)
- [Machine-readable checks](evidence/readability-revision-checks.json)

The chapter capture sweep used reduced-motion preferences to avoid screenshots of in-progress smooth scrolling. This was an ad-hoc website smoke/visual run, not a new permanent test suite or a learner usability study.

### Compact diagram evidence and scoring

**Evidence classification:** geometry, effective text size and margins are script-backed; fit/layout judgment is script-assisted; conceptual meaning is visual/manual-only. Evidence is the rendered PNGs, 288 px fit previews, and actual website screenshots at desktop and narrow widths.

Each compact SVG has a 320 px source canvas and 18–20 px essential labels. At the conservative 288 px fit width, the smallest labels are 16.2 px. The fit helper's unused 1200 px viewport surplus was cropped to the complete source-canvas aspect ratio without resizing its displayed contents. Source and fit-preview margin reports have no warnings.

| Topic | Source | Render | Fit preview | Supporting reports |
| --- | --- | --- | --- | --- |
| Layers | [SVG](diagrams/layers-mobile.svg) | [PNG](diagrams/layers-mobile.png) | [Fit](diagrams/layers-mobile.fitcheck.png) | [Geometry](diagrams/layers-mobile.heuristics.txt), [margins](diagrams/layers-mobile.margin.txt), [fit margins](diagrams/layers-mobile.fitcheck.margin.txt) |
| Tool loop | [SVG](diagrams/execution-mobile.svg) | [PNG](diagrams/execution-mobile.png) | [Fit](diagrams/execution-mobile.fitcheck.png) | [Geometry](diagrams/execution-mobile.heuristics.txt), [margins](diagrams/execution-mobile.margin.txt), [fit margins](diagrams/execution-mobile.fitcheck.margin.txt) |
| Construction | [SVG](diagrams/construction-mobile.svg) | [PNG](diagrams/construction-mobile.png) | [Fit](diagrams/construction-mobile.fitcheck.png) | [Geometry](diagrams/construction-mobile.heuristics.txt), [margins](diagrams/construction-mobile.margin.txt), [fit margins](diagrams/construction-mobile.fitcheck.margin.txt) |
| State cycle | [SVG](diagrams/state-flow-mobile.svg) | [PNG](diagrams/state-flow-mobile.png) | [Fit](diagrams/state-flow-mobile.fitcheck.png) | [Geometry](diagrams/state-flow-mobile.heuristics.txt), [margins](diagrams/state-flow-mobile.margin.txt), [fit margins](diagrams/state-flow-mobile.fitcheck.margin.txt) |
| Delegation | [SVG](diagrams/delegation-mobile.svg) | [PNG](diagrams/delegation-mobile.png) | [Fit](diagrams/delegation-mobile.fitcheck.png) | [Geometry](diagrams/delegation-mobile.heuristics.txt), [margins](diagrams/delegation-mobile.margin.txt), [fit margins](diagrams/delegation-mobile.fitcheck.margin.txt) |
| Routing | [SVG](diagrams/routing-mobile.svg) | [PNG](diagrams/routing-mobile.png) | [Fit](diagrams/routing-mobile.fitcheck.png) | [Geometry](diagrams/routing-mobile.heuristics.txt), [margins](diagrams/routing-mobile.margin.txt), [fit margins](diagrams/routing-mobile.fitcheck.margin.txt) |
| Code ownership | [SVG](diagrams/code-processes-mobile.svg) | [PNG](diagrams/code-processes-mobile.png) | [Fit](diagrams/code-processes-mobile.fitcheck.png) | [Geometry](diagrams/code-processes-mobile.heuristics.txt), [margins](diagrams/code-processes-mobile.margin.txt), [fit margins](diagrams/code-processes-mobile.fitcheck.margin.txt) |

**Pass 1 — Composition:** G1, G2, G5, G6, G8 and G9 are green. Entire flows are visible without sideways panning; labels remain readable; exclusive routing is explicit; the tool loop retains its harness boundary; the Code backend is a capability boundary rather than necessarily a third process.

**Pass 2 — Mechanics:** G3, G4 and G7 are green. Orthogonal connectors, compact arrowheads, anchored endpoints and internal label padding passed rendered inspection. No text-overflow, collision, diagonal or effective-text warnings remain.

Heuristic dispositions, not suppressed warnings:

- `G4/G5/G8 -> execution-mobile feedback return -> helper flags the long two-bend route -> informational, accepted after visual review.` It represents the real tool-result return, occupies a dedicated clear rail, and is visually secondary.
- `G4/G5/G8 -> state-flow-mobile iteration return -> helper flags the long two-bend route -> informational, accepted after visual review.` It represents the real next-iteration cycle rather than a layout-only bus; removing it would lose the loop relationship.
- `G7 -> routing-mobile option label -> conservative text estimate flagged a long single line -> resolved by wrapping the label and regenerating all routing evidence.`
- `G1 -> narrow fit previews -> unused helper viewport created excessive bottom whitespace -> resolved by cropping only surplus viewport area and rerunning margin reports.`

No unresolved red/yellow visual findings remain in the compact set. The seven desktop source diagrams were retained unchanged.

### Verification boundary

The source-grounded examples remain illustrative. No upstream model/provider/integration suite was run, and no upstream application success or universal learner-comprehension claim is made. No commits were created.

## Memory lifecycle addition — 2026-11-10

### Source and runtime evidence

- The source pin remains `c4e2811312718e98b1465b6e67c34997ca72c793` (DeepAgents 0.7.32).
- [Research report](evidence/memory-research.md) and [six passing offline scenarios](evidence/memory-runtime.json) distinguish native file memory, checkpointed thread state, cross-thread store access, semantic retrieval, context projection and RAM.
- Native file edits and external writes did not refresh the existing thread's memory cache; fresh threads loaded updated shared files.
- Custom-threshold compaction retained 10 conversation messages in raw state while the model fixture received 4 messages including its system message.
- A recording counter saw caller system text but not memory injected later; the actual model request included that memory. This verifies ordering/visibility, not a provider overflow failure.
- Real native graphs, filesystem tools, memory hooks, stores and checkpoints ran; provider responses and summary text were deterministic fixtures. No external provider, restart-durability test or RAM profile is claimed.

### Website smoke and visual checks

- Added five cited sections while preserving existing chapter/section IDs: 24 chapters, 122 sections.
- Exercised all six memory walkthrough steps and five new sections at desktop (1440×1000) and mobile (390×844): 22 successful views.
- Checked Next/Previous, scenario switching, chapter search into the new cache section, and local source navigation with 82 requested lines highlighted.
- Checked 404 citations backed by the pinned DeepAgents package for valid line ranges; this is a structural citation check, not a fresh audit of every authored claim.
- Observed no document overflow in the final 22 views; table roles, header associations and responsive cards remained intact. Additional runtime checks at 320 px and 360 px also fit.
- Reproduced and fixed a 2 px mobile overflow caused by the scenario selector's intrinsic width. Its width is now constrained to the available container; verified against a fresh stylesheet response.
- No page exceptions were recorded. `node --check walkthrough.js` passed. Evidence files returned HTTP 200 from the local preview.
- Inspected actual desktop/mobile screenshots for readable labels, numbered explanations and table/card layout. No diagram source was changed; no new diagram scoring is claimed.

Evidence: [browser checks](evidence/memory-website.json), [desktop chapter](evidence/memory-types-desktop.png), [mobile chapter](evidence/memory-types-mobile.png), [mobile walkthrough](evidence/memory-walkthrough-mobile.png), [budget caveat](evidence/memory-budget-desktop.png).

The user explicitly approved committing and publishing after these local checks. Live deployment was not yet verified when this record was authored; post-merge deployment evidence belongs in the publication PR.
