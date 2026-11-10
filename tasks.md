# Deep Agents implementation explorer

## Scope and acceptance

Build a standalone, dependency-free technical learning website for langchain-ai/deepagents at commit c4e2811312718e98b1465b6e67c34997ca72c793. Do not modify the platform applications or existing user changes.

- Guided implementation chapters cover SDK construction, middleware, state, backend protocols, delegation, permissions, context, profiles, Code, Talon, ACP, partner integrations, examples, testing, and operational boundaries.
- Pin source citations to the reviewed revision; distinguish shipped source behavior, dependency responsibilities, and illustrative walkthroughs.
- Include searchable chapter navigation and a browsable source atlas containing repository implementation and tests, with stable source links.
- Include accessible interactive execution walkthroughs, responsive navigation, code-copy controls, and keyboard search.
- Produce editable diagrams and PNG/fit-check/helper evidence; score G1–G9 against rendered output.
- Exercise actual website behavior on desktop and mobile, validate source references and local links, and record verification.

## Implementation sequence

1. Inspect source and author cited technical chapters in independent SDK, backend, and application slices.
2. Build static site shell, source atlas, execution walkthrough, and diagrams.
3. Serve locally; verify browser navigation/search/source selection/walkthrough/accessibility/responsiveness.
4. Run diagram helper checks and visual two-pass review; document usage and evidence.

## Readability acceptance

- Revise every chapter for a technical reader new to Deep Agents: introduce concepts and normal behavior before implementation details and exceptions.
- Add source-grounded illustrative traces; preserve detailed coverage, stable chapter/section identifiers, and existing citation targets.
- Distinguish graph state, model context, output streams, checkpoint storage, and external tool effects.
- Use 16 px chapter prose and readable narrow-screen comparison cards with retained table/header semantics.
- Provide complete, legible narrow-screen layouts for all seven diagram topics without horizontal panning; retain desktop layouts.
- Validate all 23 chapters and 105 sections on the public desktop/mobile website, highlighted example text, code copying, reference disclosures, search, navigation, source links, and walkthroughs.
- Regenerate compact SVG/PNG/fit/margin/geometry evidence; explicitly score both G1–G9 passes and resolve or explain heuristic findings.
- Record exercised verification without claiming upstream provider/model test-suite success.

## Agent-loop and stop-condition acceptance

- Add a dedicated `sdk-agent-loop` chapter/sidebar entry using the existing reading, search, code-copy, source-link, and mobile-table components.
- Verify the Deep Agents constructor handoff and the dependency-owned model/tools routing against an explicitly recorded compatible runtime. Keep the upstream Deep Agents pin unchanged; record exact installed dependency versions separately.
- Run deterministic, credential-free probes through real compiled agents. Label controlled model responses as test fixtures, not genuine model reasoning or provider integration success.
- Cover normal no-call exits, tool-result continuation, multiple calls, direct-return versus mixed tools, structured-output success/recovery and mixed-error exits, middleware routing, tool-issued commands, call-budget policies, rubric outcomes, approval pause/resume decisions, handled and unhandled errors, recursion limits, timeout/cancellation, context overflow, and parent/child completion boundaries. Distinguish runtime-exercised cases from source-only external-service behavior.
- Show the actual graph extracted from the probed configuration, explain that tool handlers are not separate graph nodes, and distinguish that topology from a simplified execution loop.
- Include source-linked scenario tables, message/ID examples, observed routing evidence, reproducible Python verification, and practical diagnostics. Completion is not proof that the requested work is correct.
- Add rendered desktop/mobile loop and outcome diagrams with source, PNG, fit-check, margin/heuristic evidence, and explicit G1–G9 scoring.
- Exercise the new chapter and existing navigation on desktop/mobile; publish through a feature branch and pull request, then verify the deployed GitHub Pages assets and route.

## Memory lifecycle and context acceptance

- Keep the upstream source pin unchanged; distinguish file-based instructions, conversation state, cross-thread storage, semantic retrieval and process RAM.
- Add an Execution Lab memory scenario using the existing walkthrough interface, with explicitly illustrative state and links to offline runtime evidence.
- Explain stale memory caches after native file edits, namespace/storage lifetimes, and the difference between request compaction and raw-state retention.
- Qualify request-budget estimates where memory is injected after the summarization counter; preserve existing chapter and section links.
- Verify walkthrough navigation, chapter search, source citations, responsive tables and desktop/mobile rendering; record only exercised checks.
- Publish through the existing GitHub Pages workflow only after explicit commit approval.



## Content interface

`content/*.json` contains arrays of chapters. Each chapter: `id`, `group`, `title`, `kicker`, `summary`, `readingMinutes`, `sections`. Each section: `id`, `title`, `body` (trusted semantic HTML), `sources` (array of `{path,start,end,label}`). Source paths are repo-relative; lines are 1-based inclusive. Use h3, p, ul, ol, tables (inside div.table-wrap), pre/code, details/summary, and aside.callout. No scripts or inline styles. Every substantive section needs primary implementation/test citations. Code samples must be marked illustrative unless actually executed. Avoid guessed versions/defaults and absolute promises.
