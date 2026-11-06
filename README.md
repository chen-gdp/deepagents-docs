# Deep Agents implementation field guide

A standalone, source-linked website for studying `langchain-ai/deepagents` at revision `c4e2811312718e98b1465b6e67c34997ca72c793`.

## Read online

**Website:** https://chen-gdp.github.io/deepagents-docs/

- [Start reading](https://chen-gdp.github.io/deepagents-docs/#/)
- [State, messages, and event contracts](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-state)
- [Agent loop and stop conditions](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-agent-loop)
- [100K-token tool-output walkthrough](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-filesystem?section=sdk-filesystem-text-offload)
- [Source repository](https://github.com/chen-gdp/deepagents-docs)

This is an independent educational guide, not an official LangChain site. GitHub Pages serves the published files without requiring the author's computer, a Python server, or a Cloudflare tunnel to remain running. Availability depends on GitHub Pages and this repository remaining published.

## Preview locally

From this directory, with your existing Conda environment activated:

```bash
python -m http.server 8793 --bind 127.0.0.1
```

Open **http://127.0.0.1:8793/**. No npm installation, build step, model keys, or backend services are needed. Do not open `index.html` directly with `file://`; browsers restrict JSON/module loading in that mode. Keep the directory structure intact. Bind the preview to loopback unless you deliberately intend to expose it.

## Publish updates

GitHub Pages publishes the **`main` branch, repository root (`/`)**. Changes merged into `main` trigger publication. Review changes on a feature branch and merge them through a pull request; no custom Actions workflow or deployment secret is needed.

Keep `.nojekyll` at the repository root. It disables Jekyll processing so the site is served unchanged, including dot-prefixed source-atlas bundles such as `source/.github.json`. Assets and hash routes are relative, allowing the same site to work under `/deepagents-docs/`.

The standalone local checkout is `~/Projects/deepagents-docs`. Do not push the surrounding private platform repository or its history into this repository.

## What is included

- 24 technical chapters and 117 cited sections, with concept-first introductions, concrete illustrative traces, short prose, meaningful numbered steps, and detailed implementation references.
- SDK construction and public parameters; middleware ordering; state/reducers/checkpoints/streaming; filesystem and tool offload; isolated, forked, compiled and background delegation; memory/skills; compaction; model/profile-dependent behavior; rubric iteration.
- A dedicated agent-loop chapter: actual compiled topology, ordered router guards, message/call correlation, direct returns, structured output, middleware policies, human-review pauses, failures, cancellation, and parent/child boundaries. All 52 credential-free probes exercise real compiled graphs; provider responses are controlled fixtures.
- Backend protocols, storage lifetimes, host filesystem/shell boundaries, composite routing, remote providers, Context Hub, path permissions, human review and security caveats.
- Deep Agents Code, Talon, ACP, all five partner packages, examples, evaluation infrastructure and contributor workflows.
- A local source atlas: 1,705 text files, including all 1,233 tracked Python files in the pinned tree, with 30,338 class/function/method definitions. Binary assets, lockfiles, agent instructions and openwiki pages are intentionally excluded. Source is lazy-loaded by package; a large package bundle can be several megabytes.
- Three deterministic execution walkthroughs: state-backed file write, approval, and inline subagent delegation. These are teaching projections, **not live model executions or captured traces**.
- Search, desktop/mobile navigation, code copying, source-range permalinks, package/test filters, definition jumps, dark/light theme, keyboard search (`Ctrl/Cmd K`), and print styling.
- Ten GDP Labs diagram topics: layering, the tool loop, construction, state/data flow, inline delegation, backend routing, Code's client/server split, ordinary-loop routing, measured compiled topology, and completion/pause/failure outcomes. Each has desktop and compact narrow-screen SVG layouts, rendered PNGs, target-width fit previews, and helper reports.
- Python-aware syntax colors in examples and source files, with JSON/Bash and other source formats highlighted according to their actual language. The pinned PrismJS 1.30.0 bundle is local; no CDN requests or npm installation are needed to view the website.
- An event-contract ownership table distinguishes LangGraph stream modes, native v3 projections, Code transport tuples, and beta async-subagent notifications.
- A worked 100K-token tool-output example distinguishes token estimates from characters, follows write/preview/paged retrieval, and links to a complete-request budget calculation plus storage and failure limits.

Source citations have local links plus adjacent pinned GitHub links. The source browser displays 350-line windows to keep large files responsive; use Earlier/Later lines or Jump to a definition.

Chapter prose uses 16 px text. At viewport widths up to 980 px, comparison tables become labeled, full-width row cards while retaining table/header semantics, and diagrams select compact layouts that show complete flows without horizontal panning. Long code lines remain scrollable, with a visible narrow-screen hint and Copy control.

Normal behavior is explained before implementation exceptions. Advanced reference material remains available in expandable sections and is included in chapter search. The fourteen full chapter code blocks retain language-aware highlighting. Model/provider examples remain illustrative; separately recorded runtime probes identify exactly what was executed.

## Source provenance and reproducibility

The inspected clone is `/tmp/deepagents-study-source`. A clone in `/tmp` may be removed by normal OS cleanup; the generated atlas is self-contained and does not depend on that clone at runtime.

To create a separate durable clone if needed:

```bash
git clone https://github.com/langchain-ai/deepagents.git /path/to/deepagents
git -C /path/to/deepagents checkout c4e2811312718e98b1465b6e67c34997ca72c793
```

Rebuild the atlas from that local clone, using your active Conda environment:

```bash
python build_source_index.py /path/to/deepagents
```

The exporter rejects a different HEAD and reads **immutable Git archive blobs**, not working-tree/index content. It never imports or executes upstream Python. Python 3.14 bare exception-tuple headers are adapted only in the AST indexing input for compatibility with the existing Conda Python 3.12; embedded source remains byte-for-byte unchanged. Parse diagnostics are exposed in the manifest; the delivered index has none.

To update to a new upstream revision, consciously update `PIN`, the app revision, source citations, chapter explanations and walkthrough references together, then regenerate and revalidate. Do not repin only the source bundles.

## Reproduce agent-loop verification

With your existing **Conda environment activated**, create an isolated environment from its Python:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-verification.txt
.venv/bin/python verify_agent_loop.py
```

The recorded run used `/home/christian/miniconda3/bin/python` 3.12.12. Installation requires Git and network access; running the probes needs no model credentials or provider calls. These optional packages are **not** needed to serve the static website.

`requirements-verification.txt` pins immutable Deep Agents source and the resolved dependency versions. The script checks the versions and full source hashes of the three inspected modules, then writes [runtime evidence](evidence/agent-loop-runtime.json). The dependency-owned router is retained as a [source snapshot](evidence/langchain-1.4.8-agent-factory.py), separately from the unchanged Deep Agents atlas.

The 52 cases distinguish successful graph termination from interrupts and failures, including the measured mixed structured-output/error pitfall. They are not the upstream test suite, a live-model benchmark, or a proof that arbitrary external tools and services behave correctly. See [the verification record](verification.md#agent-loop-verification-2026-11-06) for exact boundaries and diagram scoring.

## Layout

- `index.html`, `styles.css`, `app.js`: static application.
- `walkthrough.js`: source-grounded illustrative scenarios.
- `syntax.js`, `vendor/prism.js`, `vendor/prism-LICENSE`: local syntax rendering, pinned grammars, and MIT license.
- `chapter-diagrams.js`: contextual diagram placement and captions.
- `content/*.json`: authored chapter content and line citations.
- `source/index.json`: file metadata, SHA-256 hashes, definitions and provenance.
- `source/*.json`: complete text source, bundled by repository package.
- `build_source_index.py`: reproducible offline-source exporter.
- `verify_agent_loop.py`, `requirements-verification.txt`: optional, source-pinned executable graph verification.
- `diagrams/`: editable diagrams and render/fit/helper evidence.
- `verification.md`, `evidence/`: actual verification record and browser captures.
- `UPSTREAM-LICENSE`: upstream MIT license for redistributed source.

Chapter HTML is trusted, locally authored content—not a user-input channel. Source code is HTML-escaped before display. External source/documentation links require network access; chapter reading, searching, walkthroughs and source browsing do not require third-party requests after the local assets load.

## Verification boundary

See [verification.md](verification.md). Website behavior, source integrity and rendered diagram checks do **not** establish that upstream model/provider/network integrations pass their own test suites. No upstream test-suite pass is claimed. Code snippets are explicitly illustrative unless separately marked as executed.

## Changelog

- Initial pinned implementation guide, full source atlas, interactive walkthroughs and validated diagram bundle.
- Corrected source-schema projections and profile-dependent planning behavior; distinguished all four review decisions and fixed keyboard/router boundaries found during verification.
- Reworked dense paragraph bodies into numbered explanations and comparison tables, preserving source citations, metadata, and example code.
- Added five contextual diagrams, explicit event-contract distinctions, and locally bundled syntax highlighting with multiline Python context and exact source-text preservation.
- Revised every chapter for concept-first learning, added concrete state/file/delegation/configuration examples, and retained all existing citation targets and section IDs.
- Added seven compact diagram variants, mobile comparison cards with accessible header associations, 16 px reading text, and clearer section jumps.
- Corrected default-backend file seeding, ACP rebuild/checkpoint qualifications, headless shell-versus-file-tool permissions, and the example-local YAML mapping shape; reverified all chapters through the replacement public tunnel.
- Added the 100K-token offload walkthrough, a concrete 100K-window input-budget example, and explicit limits for full-result understanding, application memory, failed writes, and restart durability; checked both changed chapters on desktop/mobile.
- Prepared a standalone public repository with branch-based GitHub Pages publishing, `.nojekyll`, relative assets, retained upstream licensing, and a stable `github.io` reading URL.
- Added the dedicated agent-loop chapter, three desktop/mobile diagram pairs, 52 source-pinned runtime probes, and explicit distinctions between completion, schema validity, application success, pauses, failures, and external/background boundaries.
