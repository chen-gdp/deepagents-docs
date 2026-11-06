import { scenarios } from './walkthrough.js';
import { highlightCode, highlightSourceLines, languageForFile } from './syntax.js';
import { chapterDiagrams } from './chapter-diagrams.js';

const REVISION = 'c4e2811312718e98b1465b6e67c34997ca72c793';
const REPO = `https://github.com/langchain-ai/deepagents/blob/${REVISION}/`;
const $ = selector => document.querySelector(selector);
const main = $('#main');
let chapters = [];
let atlasPromise;
const bundles = new Map();
let routeEpoch = 0;
let toastTimer;
let searchIndex = [];
let runtimeFocus = null;

function clampInteger(value, minimum, maximum) {
  const number = Number(value);
  const integer = Number.isFinite(number) ? Math.trunc(number) : minimum;
  return Math.max(minimum, Math.min(maximum, integer));
}

function setMenuOpen(open) {
  const focusInside = $('#sidebar').contains(document.activeElement);
  $('#sidebar').classList.toggle('open', open);
  $('#mobile-menu').setAttribute('aria-expanded', String(open));
  if (!open && focusInside && matchMedia('(max-width: 720px)').matches) {
    $('#mobile-menu').focus({preventScroll:true});
  }
}
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const strip = html => { const node = document.createElement('div'); node.innerHTML = html; return node.textContent || ''; };
const fetchJson = async path => { const response = await fetch(path); if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`); return response.json(); };
const chapterUrl = id => `#/chapter/${encodeURIComponent(id)}`;
const sourceUrl = (path, start = 1, end = start) => `#/source?file=${encodeURIComponent(path)}&line=${start}&end=${end}`;
const remoteUrl = (path, start, end) => `${REPO}${path.split('/').map(encodeURIComponent).join('/')}#L${start}${end && end !== start ? `-L${end}` : ''}`;
const loadAtlas = () => atlasPromise ||= fetchJson('source/index.json');

function showToast(message) {
  $('#toast').textContent = message;
  $('#toast').classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 2500);
}

function sourcesHtml(sources = []) {
  if (!sources.length) return '';
  return `<div class="sources"><span class="sources-label">Read the implementation</span>${sources.map(source => `<a class="source-link" href="${sourceUrl(source.path, source.start, source.end)}" title="Open local source: ${escape(source.path)}">${escape(source.label || source.path.split('/').at(-1))}:${source.start}–${source.end}</a><a class="source-external" href="${remoteUrl(source.path, source.start, source.end)}" target="_blank" rel="noopener" aria-label="Open ${escape(source.path)} lines ${source.start} to ${source.end} on GitHub">↗</a>`).join('')}</div>`;
}

function buildNavigation() {
  const specials = `<div class="nav-group"><span class="nav-label">The field guide</span><a class="nav-link" href="#/" data-route="home"><span class="nav-num">⌂</span>Start here</a><a class="nav-link" href="#/runtime" data-route="runtime"><span class="nav-num">↻</span>Execution lab</a><a class="nav-link" href="#/source" data-route="source"><span class="nav-num">{ }</span>Source atlas</a><a class="nav-link" href="#/glossary" data-route="glossary"><span class="nav-num">Aa</span>Concept glossary</a></div>`;
  const groups = [...new Set(chapters.map(chapter => chapter.group))];
  $('#navigation').innerHTML = specials + groups.map(group => `<div class="nav-group"><span class="nav-label">${escape(group)}</span>${chapters.filter(chapter => chapter.group === group).map(chapter => `<a class="nav-link" href="${chapterUrl(chapter.id)}" data-chapter="${escape(chapter.id)}"><span class="nav-num">${String(chapters.indexOf(chapter) + 1).padStart(2, '0')}</span>${escape(chapter.title)}</a>`).join('')}</div>`).join('') + '<div class="nav-group"><a class="nav-link" href="#/about" data-route="about">Scope & evidence ↗</a></div>';
}

function setActive(route, id) {
  document.querySelectorAll('.nav-link').forEach(link => {
    const active = id ? link.dataset.chapter === id : link.dataset.route === route;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
  });
  setMenuOpen(false);
}

function header(kicker, title, summary, extra = '') {
  return `<header class="article-header"><div class="eyebrow">${escape(kicker)}</div><h1>${escape(title)}</h1><p class="article-summary">${escape(summary)}</p>${extra}</header>`;
}

function renderHome() {
  const foundations = chapters.find(c => c.group === 'Foundations') || chapters[0];
  main.innerHTML = `<div class="home"><div class="eyebrow">A source-first technical companion</div><div class="hero"><div><h1>Beyond the agent.<br>Inside the <em>harness.</em></h1><p class="intro">Understand Deep Agents from the public API down to the execution loop. Follow the middleware, trace the state, and see exactly where the code does the work.</p><div class="hero-actions"><a class="button-primary" href="${chapterUrl(foundations.id)}">Start the guided deep dive <span>↗</span></a><a class="button-secondary" href="#/runtime">Trace a run <span>→</span></a></div><p class="hero-note">Python repository · pinned to <a href="${REPO.replace('/blob/', '/tree/')}" target="_blank" rel="noopener"><code>c4e2811</code></a> · independent learning resource</p></div><figure class="hero-art"><div class="figure-label">The mental model / three layers</div><img src="diagrams/layers.svg" width="660" height="470" alt="Deep Agents configures LangChain create_agent, which builds a graph executed by LangGraph."><figcaption class="hero-note">Layers of one stack—not three independent services.</figcaption></figure></div><div class="facts-strip"><div class="fact"><span class="fact-icon">01</span><div><strong>Concept → implementation</strong><span>Build the mental model, then inspect it.</span></div></div><div class="fact"><span class="fact-icon">↳</span><div><strong>Evidence at every turn</strong><span>Local source and pinned GitHub line links.</span></div></div><div class="fact"><span class="fact-icon">{ }</span><div><strong>The whole repository in reach</strong><span>SDK, applications, adapters, examples & tests.</span></div></div></div><div class="section-heading"><h2>Choose your way in.</h2><p>Three complementary ways to understand the same implementation.</p></div><div class="learning-grid"><a class="learning-card" href="${chapterUrl(foundations.id)}"><span class="card-index">01 / UNDERSTAND</span><h3>Read the implementation guide</h3><p>Layer-by-layer chapters on construction, tools, context, persistence, delegation, safety, and the applications built on top.</p><div class="card-bottom"><span>${chapters.length} technical chapters</span><span>↗</span></div></a><a class="learning-card" href="#/runtime"><span class="card-index">02 / FOLLOW</span><h3>Step through an agent run</h3><p>Watch a request cross the model, middleware, tool, and backend boundaries. Compare execution with approval and delegation.</p><div class="card-bottom"><span>3 annotated walkthroughs</span><span>↗</span></div></a><a class="learning-card" href="#/source"><span class="card-index">03 / INVESTIGATE</span><h3>Open the source atlas</h3><p>Search file paths, classes, functions, and methods. Read full local source with line numbers, docstrings, and links to the original.</p><div class="card-bottom"><span>Implementation + test source</span><span>↗</span></div></a></div><aside class="callout"><strong>The distinction that unlocks the repository.</strong> Deep Agents is not a new model or a replacement runtime. It assembles an opinionated harness on LangChain’s <code>create_agent</code>; LangGraph drives the resulting graph. The model proposes actions. Tools, backends, approvals, and the execution environment determine what can actually happen.</aside><div class="section-heading"><h2>The complete reading path</h2><p>Read in order, or jump to the question you’re trying to answer.</p></div><div class="chapter-directory">${chapters.map((chapter, i) => `<a class="directory-row" href="${chapterUrl(chapter.id)}"><span>${String(i + 1).padStart(2, '0')}</span><div><h3>${escape(chapter.title)}</h3><p>${escape(chapter.summary)}</p></div><small>${chapter.readingMinutes} min · ${chapter.sections.length} sections ↗</small></a>`).join('')}</div></div>`;
}

function renderSection(section) {
  const diagram = chapterDiagrams[section.id];
  const figure = diagram
    ? `<figure class="diagram-panel chapter-diagram"><img src="diagrams/${diagram.name}.svg" width="${diagram.width}" height="${diagram.height}" alt="${escape(diagram.alt)}"><figcaption>${escape(diagram.caption)}</figcaption></figure>`
    : '';
  return `<section id="${escape(section.id)}"><h2>${escape(section.title)}</h2>${figure}${section.body}${sourcesHtml(section.sources)}</section>`;
}

function renderChapter(id, sectionId) {
  const chapter = chapters.find(chapter => chapter.id === id);
  if (!chapter) return renderNotFound();
  const index = chapters.indexOf(chapter);
  main.innerHTML = `<div class="reading-layout"><article class="prose">${header(chapter.kicker, chapter.title, chapter.summary, `<div class="article-meta"><span>CHAPTER ${String(index + 1).padStart(2, '0')}</span><span>${chapter.readingMinutes} min read</span><span>${chapter.sections.length} implementation sections</span><span>Revision c4e2811</span></div>`)}${chapter.sections.map(renderSection).join('')}<div class="chapter-pager">${index > 0 ? `<a href="${chapterUrl(chapters[index - 1].id)}"><small>← Previous chapter</small>${escape(chapters[index - 1].title)}</a>` : '<span></span>'}${index < chapters.length - 1 ? `<a href="${chapterUrl(chapters[index + 1].id)}"><small>Next chapter →</small>${escape(chapters[index + 1].title)}</a>` : '<a href="#/source"><small>Keep investigating →</small>Open the source atlas</a>'}</div></article><aside class="toc" aria-label="On this page"><div class="toc-label">IN THIS CHAPTER</div>${chapter.sections.map(section => `<a href="${chapterUrl(id)}?section=${encodeURIComponent(section.id)}">${escape(section.title)}</a>`).join('')}<hr><a href="#/runtime">↻ Follow an execution</a><a href="#/source">{ } Inspect the source</a></aside></div>`;
  prepareReadingTables();
  addCodeControls();
  if (sectionId) requestAnimationFrame(() => document.getElementById(sectionId)?.scrollIntoView());
}

function prepareReadingTables() {
  main.querySelectorAll('.table-wrap table').forEach((table, tableIndex) => {
    table.classList.add('reading-table');
    table.setAttribute('role', 'table');
    const headers = [...table.querySelectorAll('thead th')];
    table.querySelectorAll('thead, tbody').forEach(group => group.setAttribute('role', 'rowgroup'));
    table.querySelectorAll('tr').forEach(row => row.setAttribute('role', 'row'));
    headers.forEach((header, column) => {
      header.id = `reading-table-${tableIndex}-column-${column}`;
      header.scope = 'col';
      header.setAttribute('role', 'columnheader');
    });
    table.querySelectorAll('tbody tr').forEach(row => {
      [...row.cells].forEach((cell, column) => {
        const header = headers[column];
        if (!header) return;
        cell.setAttribute('role', 'cell');
        cell.setAttribute('headers', header.id);
        const label = document.createElement('span');
        label.className = 'table-cell-label';
        label.setAttribute('aria-hidden', 'true');
        label.textContent = header.textContent;
        cell.prepend(label);
      });
    });
  });
}

function prepareDiagrams() {
  const mobileHeights = {layers: 414, execution: 546, construction: 414, 'state-flow': 450, delegation: 414, routing: 342, 'code-processes': 400, 'agent-loop-routing': 588, 'agent-loop-outcomes': 528, 'agent-loop-compiled': 726};
  main.querySelectorAll('.hero-art img, .diagram-panel img').forEach(image => {
    const name = image.getAttribute('src').split('/').at(-1).replace('.svg', '');
    const source = document.createElement('source');
    source.media = '(max-width: 980px)';
    source.srcset = `diagrams/${name}-mobile.svg`;
    source.setAttribute('width', '320');
    source.setAttribute('height', mobileHeights[name]);
    const picture = document.createElement('picture');
    image.before(picture);
    picture.append(source, image);
  });
}

function addCodeControls() {
  main.querySelectorAll('pre').forEach(pre => {
    if (pre.classList.contains('source-code')) return;
    const code = pre.querySelector('code');
    if (code) {
      const declared = code.className.match(/\blanguage-([\w-]+)\b/);
      const language = declared?.[1] || (pre.classList.contains('state-view') ? 'json' : 'python');
      code.classList.add(`language-${language}`);
      pre.dataset.language = language;
      code.innerHTML = highlightCode(code.textContent, language);
    }
    const button = document.createElement('button');
    button.className = 'copy-button'; button.textContent = 'Copy'; button.setAttribute('aria-label', 'Copy code example');
    button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(pre.querySelector('code')?.textContent || pre.textContent.replace(/Copy$/, '')); showToast('Code copied'); }
      catch { showToast('Clipboard unavailable. Select the code to copy it.'); }
    });
    if (!pre.classList.contains('state-view')) {
      pre.tabIndex = 0;
      pre.setAttribute('aria-label', `${pre.dataset.language || 'Source'} code example. Scroll horizontally for long lines.`);
      const hint = document.createElement('p');
      hint.className = 'code-scroll-hint';
      hint.textContent = 'Long lines: swipe the code sideways, or use Copy.';
      pre.after(hint);
    }
    pre.append(button);
  });
}

function renderRuntime(scenarioId = 'filesystem', requestedStep = 0) {
  const scenario = scenarios.find(s => s.id === scenarioId) || scenarios[0];
  const stepIndex = clampInteger(requestedStep, 0, scenario.steps.length - 1);
  const step = scenario.steps[stepIndex];
  main.innerHTML = `<div class="wide-page">${header('The execution lab', 'Follow one decision at a time.', 'An annotated, deterministic teaching walkthrough—not a live model, SDK execution, or captured production trace. Inspect what each layer owns and what changes in state.')}<figure class="diagram-panel"><img src="diagrams/execution.svg" width="760" height="550" alt="A model proposes a tool call, harness middleware prepares or gates it, an allowed tool accesses a backend or service, and the result returns to the next model decision."><figcaption>Primary arrows describe the call path; the lower return route carries the tool result. The backend/service connector represents request and response. Middleware is not a universal security boundary: built-in file permissions do not sandbox arbitrary tools or shell commands.</figcaption></figure><div class="scenario-select"><label for="scenario">Explore a scenario</label><select id="scenario">${scenarios.map(s => `<option value="${s.id}" ${s.id === scenario.id ? 'selected' : ''}>${escape(s.title)}</option>`).join('')}</select><span class="tag">Illustrative values · source-grounded control flow</span></div><p>${escape(scenario.description)}</p><div class="runtime-grid"><nav class="runtime-steps" aria-label="Execution steps">${scenario.steps.map((s, index) => `<button class="runtime-step ${index === stepIndex ? 'active' : ''}" data-step="${index}" ${index === stepIndex ? 'aria-current="step"' : ''}><span class="step-number">${index + 1}</span>${escape(s.title)}</button>`).join('')}</nav><section class="runtime-detail" aria-live="polite"><p class="runtime-owner">${escape(step.owner)} · STEP ${stepIndex + 1} OF ${scenario.steps.length}</p><h2>${escape(step.title)}</h2><div class="prose">${step.body}</div><p class="state-label">Illustrative state / observation</p><pre class="state-view"><code>${escape(JSON.stringify(step.state, null, 2))}</code></pre>${sourcesHtml(step.sources)}<div class="runtime-controls"><button id="step-back" ${stepIndex === 0 ? 'disabled' : ''}>← Previous</button><button id="step-next" ${stepIndex === scenario.steps.length - 1 ? 'disabled' : ''}>Next step →</button></div></section></div></div>`;
  const navigate = (index, focus) => {
    runtimeFocus = focus;
    location.hash = `/runtime?scenario=${scenario.id}&step=${index}`;
  };
  $('#scenario').addEventListener('change', event => {
    runtimeFocus = '#scenario';
    location.hash = `/runtime?scenario=${event.target.value}&step=0`;
  });
  main.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => navigate(Number(button.dataset.step), `[data-step="${button.dataset.step}"]`)));
  $('#step-back').addEventListener('click', () => navigate(stepIndex - 1, '#step-back'));
  $('#step-next').addEventListener('click', () => navigate(stepIndex + 1, '#step-next'));
  if (runtimeFocus) {
    const control = $(runtimeFocus);
    const focusTarget = control && !control.disabled ? control : $(`[data-step="${stepIndex}"]`);
    focusTarget.focus({preventScroll:true});
    showToast(`Step ${stepIndex + 1}: ${step.title}`);
    runtimeFocus = null;
  }
  addCodeControls();
}

async function renderAtlas(params, epoch) {
  main.innerHTML = '<p class="loading">Loading the repository index. Source bundles are fetched only when you open a file…</p>';
  const data = await loadAtlas();
  if (epoch !== routeEpoch) return;
  const packages = [...new Set(data.files.map(f => f.bundle))].sort();
  main.innerHTML = `<div class="wide-page">${header('Read the real implementation', 'The source atlas.', 'Search paths and Python definitions, then inspect the complete file. All source is local, read-only, and pinned to the reviewed commit; nothing here executes repository code.')}<p class="source-stats">${data.statistics.files.toLocaleString()} text files · ${data.statistics.pythonFiles.toLocaleString()} Python files · ${data.statistics.symbols.toLocaleString()} indexed definitions · ${data.statistics.lines.toLocaleString()} source lines</p><div class="atlas-controls"><input id="file-search" type="search" aria-label="Search file paths and Python symbols" placeholder="Search paths, classes, functions, methods…"><select id="package-filter" aria-label="Filter source package"><option value="">All packages</option>${packages.map(p => `<option value="${escape(p)}">${escape(p)}</option>`).join('')}</select><select id="kind-filter" aria-label="Filter implementation or tests"><option value="all">Implementation + tests</option><option value="implementation">Implementation only</option><option value="tests">Tests only</option></select></div><p id="file-count" class="source-stats" aria-live="polite"></p><div class="atlas-layout"><nav class="file-list" id="file-list" aria-label="Source files"></nav><div class="source-pane" id="source-pane"><p class="empty-state">Select a file to inspect its source and definitions.</p></div></div><aside class="callout"><strong>Scope, not a completeness illusion.</strong> ${escape(data.exclusions)} Markdown documentation is context, not proof that a feature is implemented. This atlas includes private helpers and tests so you can follow behavior beyond public API names.${data.parseDiagnostics.length ? ` ${data.parseDiagnostics.length} files could not be parsed by the indexing interpreter; their full source is still available.` : ''}</aside></div>`;
  let selected = params.get('file');
  let sourceEpoch = 0;
  const renderList = () => {
    const query = $('#file-search').value.toLowerCase().trim();
    const pack = $('#package-filter').value;
    const kind = $('#kind-filter').value;
    const filtered = data.files.filter(file => (!pack || file.bundle === pack) && (kind === 'all' || (kind === 'tests') === file.test) && (!query || file.path.toLowerCase().includes(query) || file.symbols.some(symbol => symbol.name.toLowerCase().includes(query))));
    $('#file-count').textContent = `${filtered.length.toLocaleString()} matching files${filtered.length > 200 ? ' · showing the first 200; narrow your search' : ''}`;
    $('#file-list').innerHTML = filtered.slice(0, 200).map(file => `<button class="file-item ${file.path === selected ? 'active' : ''}" data-file="${escape(file.path)}">${escape(file.path)}<small>${file.lines.toLocaleString()} lines · ${file.symbols.length} definitions${file.test ? ' · test' : ''}</small></button>`).join('') || '<p class="empty-state">No matching paths or definitions. Try a shorter term or reset the package filter.</p>';
  };
  const openFile = async (path, line = 1, end = line) => {
    const current = ++sourceEpoch;
    const file = data.files.find(file => file.path === path);
    if (!file) { $('#source-pane').innerHTML = '<p class="empty-state">This path is not embedded in the atlas. Use the pinned repository link to inspect other assets.</p>'; return; }
    selected = path; renderList();
    $('#source-pane').innerHTML = '<p class="loading">Loading source…</p>';
    try {
      if (!bundles.has(file.bundle)) bundles.set(file.bundle, fetchJson(`source/${encodeURIComponent(file.bundle)}.json`));
      const bundle = await bundles.get(file.bundle);
      if (epoch !== routeEpoch || current !== sourceEpoch) return;
      const text = bundle[path];
      const start = clampInteger(line, 1, file.lines || 1);
      const last = clampInteger(end, start, file.lines || 1);
      // Render a bounded source window to keep huge implementation/test files responsive.
      let windowStart = Math.max(1, start - 25);
      let windowEnd = Math.min(file.lines, windowStart + 349);
      const language = languageForFile(path);
      const lines = highlightSourceLines(text, language);
      const renderCode = () => {
        $('#source-window').textContent = file.lines
          ? `Lines ${windowStart}–${windowEnd} of ${file.lines.toLocaleString()} · ${file.bytes.toLocaleString()} bytes`
          : 'Empty file · 0 bytes';
        $('#source-code').innerHTML = lines.slice(windowStart - 1, windowEnd).map((value, index) => { const number = windowStart + index; return `<span class="source-line ${number >= start && number <= last ? 'highlighted' : ''}" id="source-line-${number}"><a class="line-number" href="${sourceUrl(path, number)}" aria-label="Permalink to line ${number}">${number}</a><code class="language-${language}">${value}</code></span>`; }).join('');
        $('#source-earlier').disabled = windowStart === 1; $('#source-later').disabled = windowEnd === file.lines;
      };
      $('#source-pane').innerHTML = `<header class="source-header"><strong>${escape(path)}</strong>${file.summary ? `<p>${escape(file.summary)}</p>` : ''}<p id="source-window"></p><a href="${remoteUrl(path, start, last)}" target="_blank" rel="noopener">Open pinned source on GitHub ↗</a><select class="symbol-select" id="symbol-select" aria-label="Jump to a definition"><option value="">Jump to a definition (${file.symbols.length})</option>${file.symbols.map(symbol => `<option value="${symbol.line}:${symbol.end}">${escape(symbol.name)} · L${symbol.line}</option>`).join('')}</select><div class="runtime-controls"><button id="source-earlier">↑ Earlier lines</button><button id="source-later">Later lines ↓</button></div></header><pre id="source-code" class="source-code" tabindex="0" aria-label="Source code with line numbers"></pre>`;
      renderCode();
      $('#symbol-select').addEventListener('change', event => { if (!event.target.value) return; const [a,b] = event.target.value.split(':'); history.replaceState(null, '', sourceUrl(path, a, b)); openFile(path, a, b); });
      $('#source-earlier').addEventListener('click', () => { windowEnd = windowStart - 1; windowStart = Math.max(1, windowEnd - 349); renderCode(); });
      $('#source-later').addEventListener('click', () => { windowStart = windowEnd + 1; windowEnd = Math.min(file.lines, windowStart + 349); renderCode(); });
      const target = document.getElementById(`source-line-${start}`);
      if (target) {
        const viewport = $('#source-code');
        viewport.scrollTop += target.getBoundingClientRect().top - viewport.getBoundingClientRect().top - 80;
      }
    } catch (error) { if (current === sourceEpoch && epoch === routeEpoch) $('#source-pane').innerHTML = `<p class="empty-state">Unable to load source: ${escape(error.message)}. <a href="${remoteUrl(path, 1)}" target="_blank" rel="noopener">Read the pinned original ↗</a></p>`; }
  };
  $('#file-search').addEventListener('input', renderList);
  $('#package-filter').addEventListener('change', renderList);
  $('#kind-filter').addEventListener('change', renderList);
  $('#file-list').addEventListener('click', event => { const button = event.target.closest('[data-file]'); if (button) { history.replaceState(null, '', sourceUrl(button.dataset.file)); openFile(button.dataset.file); } });
  if (selected) { const file = data.files.find(file => file.path === selected); if (file) $('#package-filter').value = file.bundle; }
  renderList();
  if (selected) await openFile(selected, params.get('line'), params.get('end'));
}

const glossary = [
 ['Agent', 'A repeated model/tool interaction, rather than a single model request. The model can decide which tool calls to propose next.'],
 ['Harness', 'The surrounding machinery that constructs prompts, exposes tools, manages context and state, and governs execution. Deep Agents supplies opinionated defaults on top of LangChain.'],
 ['Graph', 'The runnable stateful program returned by create_agent. LangGraph schedules its nodes and carries updates between them; Deep Agents does not implement a separate scheduler.'],
 ['Middleware', 'Hooks around agent/model/tool lifecycle events. Unlike a tool, middleware can affect a request before the model chooses an action. Hook ordering and sync/async implementations matter.'],
 ['Backend', 'A filesystem capability interface used by built-in tools and middleware. A backend can store virtual files in graph state, use a shared store, map host files, route paths, or delegate to a sandbox.'],
 ['Tool', 'A callable capability with a model-visible name and argument schema. Visibility is not authorization. Custom tools can bypass built-in filesystem permission checks.'],
 ['Checkpoint', 'A runtime snapshot for a graph thread, enabling persistence and resume when configured with an appropriate checkpointer. It is not the same thing as a cross-thread store or a host file.'],
 ['Store', 'A namespaced persistence interface. StoreBackend uses it for files that need a different lifetime from per-thread graph state. Durability depends on the store implementation.'],
 ['Thread', 'The conversation/execution identity used with checkpoints. Reusing a thread identifier is not a substitute for tenant authorization.'],
 ['State', 'Typed values flowing through the graph: messages plus middleware/application fields. Reducers determine how concurrent updates combine, rather than blindly replacing every field.'],
 ['Reducer', 'A merge rule for a state field. Custom state modified concurrently by subagents needs an appropriate reducer or graph updates can conflict.'],
 ['DeltaChannel', 'The message channel used by DeepAgentState to store incremental updates and periodic snapshots, reducing repeated checkpoint message-history storage.'],
 ['Subagent', 'A delegated runnable with a selected prompt, tools, model and state transfer rules. Fresh task context, forked context, precompiled graphs, and remote async runs have different semantics.'],
 ['Context isolation', 'Controlling which messages/state enter a delegated run and what comes back. This is not OS isolation, and does not imply separate filesystem permissions.'],
 ['Skill', 'A reusable instruction/resource package discovered through backend paths. Skill metadata and selected content are disclosed progressively; a skill is not a separately trained model.'],
 ['Memory', 'Here, instructions or content loaded from configured sources and injected by middleware. Memory injection, storing files, and semantic retrieval are different operations.'],
 ['Compaction', 'Reducing active conversation context by summarization or eviction while preserving a usable continuation. It is lossy and differs from merely storing a large tool response outside the prompt.'],
 ['Offloading', 'Moving large or binary tool content into backend files and exposing a smaller reference in messages. Consumers must be able to access the backing path later.'],
 ['HITL / interrupt', 'A runtime pause for human review. Approval, edit, rejection and resume need an application interface and persistence configuration; a prompt requesting approval is not equivalent.'],
 ['Provider profile', 'Provider/model resolution settings such as default constructor behavior. Distinct from a harness profile that customizes prompts, middleware and tool descriptions.'],
 ['Harness profile', 'Model-specific harness configuration: prompt changes, additional middleware, exclusions, descriptions and general-purpose subagent settings. It can change what “default” means.'],
 ['Sandbox', 'An execution environment with a capability contract. Real isolation is supplied by the environment/provider, not by the word sandbox or by the Python protocol alone.'],
 ['MCP', 'Model Context Protocol: an external tool integration path used by applications. MCP tools still need authentication, authorization, lifecycle management and a trusted execution boundary.'],
 ['ACP', 'Agent Client Protocol: the editor/client integration surface in libs/acp, distinct from MCP tool-server integration.'],
 ['Talon', 'A separate application package around the SDK, with channels, scheduling, history, authorization and runtime services. It is not automatically started by create_deep_agent.'],
 ['Illustrative trace', 'A deliberately constructed teaching sequence. The execution lab shows control flow but makes no claim that a model emitted those exact calls or that the listed states are checkpoint dumps.'],
];

function renderGlossary() {
  main.innerHTML = `<div class="reading-layout"><article class="prose">${header('Vocabulary without the fog', 'The concept glossary.', 'Similar words often hide different lifetimes, trust boundaries, or responsibilities. Use these distinctions when reading the code.')}<dl>${glossary.map(([term, definition]) => `<div class="glossary-term"><dt>${escape(term)}</dt><dd>${escape(definition)}</dd></div>`).join('')}</dl><aside class="callout">These are explanatory definitions for this pinned repository. Follow the chapter citations or use the source atlas for the concrete types and algorithms.</aside></article></div>`;
}

async function renderAbout(epoch) {
  const data = await loadAtlas();
  if (epoch !== routeEpoch) return;
  main.innerHTML = `<div class="reading-layout"><article class="prose">${header('Scope & provenance', 'An inspectable guide, not an oracle.', 'Implementation claims are tied to a fixed source revision. The repository can change; this site does not silently track main.')}<section><h2>What was inspected</h2><p>Repository: <a href="https://github.com/langchain-ai/deepagents">langchain-ai/deepagents</a>. Revision: <a href="https://github.com/langchain-ai/deepagents/tree/${REVISION}"><code>${REVISION}</code></a>. A local shallow clone was used to read the implementation, public exports, package metadata, examples, and tests.</p><p>This guide contains ${chapters.length} chapters and ${chapters.reduce((n,c)=>n+c.sections.length,0)} sections. The atlas embeds ${data.statistics.files.toLocaleString()} tracked text files including ${data.statistics.pythonFiles.toLocaleString()} Python files. ${escape(data.exclusions)}</p><p>The source snapshot is redistributed under its upstream MIT license. See <a href="UPSTREAM-LICENSE">UPSTREAM-LICENSE</a>. This is an independent educational artifact, not an official LangChain product.</p></section><section><h2>How to read the evidence</h2><ul><li><strong>Implementation citations:</strong> section-level links open exact local source ranges. The adjacent ↗ opens the same revision on GitHub.</li><li><strong>Tests:</strong> cited test source shows intended behavior and boundary cases. Reading tests is not the same as executing the upstream suite.</li><li><strong>Examples:</strong> snippets and execution-lab data are illustrative unless explicitly described as executed. Provider/network/model behavior depends on your installed versions and credentials.</li><li><strong>Dependency boundary:</strong> LangChain/LangGraph/provider internals are not vendored here. Their runtime responsibilities are distinguished from Deep Agents’ own implementation.</li><li><strong>Documentation:</strong> architecture notes and READMEs orient the reader; planned behavior is not treated as implemented solely because prose describes it.</li></ul></section><section><h2>Coverage by learning question</h2><div class="table-wrap"><table><thead><tr><th>Question</th><th>Where to investigate</th></tr></thead><tbody>${[...new Set(chapters.map(c=>c.group))].map(group=>`<tr><td>${escape(group)}</td><td>${chapters.filter(c=>c.group===group).map(c=>`<a href="${chapterUrl(c.id)}">${escape(c.title)}</a>`).join('<br>')}</td></tr>`).join('')}</tbody></table></div><p>This is not a claim that every line is individually explained. Guided chapters provide depth on the central mechanisms; the atlas exposes complete tracked implementation and test files for the remaining detail. Generated lockfiles, binary assets, agent instructions and openwiki pages are not embedded.</p></section><section><h2>Verification and limits</h2><p>The website is a static client application. It does not send prompts, execute Python, call an LLM, start Talon/Code, or contact MCP servers. Searches operate locally. GitHub and official-reference links leave the site.</p><p>See <a href="verification.md">the verification record</a> for exercised browser behavior, source-citation checks, rendered diagram evidence, and G1–G9 scoring. Website verification does not establish that the upstream applications or provider integrations pass their own tests.</p><p>For local serving and reproducible source indexing, see <a href="README.md">README.md</a>. Python commands use the existing Conda interpreter. Re-indexing a different commit deliberately fails until the content and revision are consciously updated.</p></section></article></div>`;
}

function renderNotFound() {
  main.innerHTML = '<div class="wide-page"><h1>That page isn’t in this guide.</h1><p>The source revision is fixed, but this URL may be incomplete.</p><a class="button-primary" href="#/">Return to the reading path →</a></div>';
}

async function route() {
  const epoch = ++routeEpoch;
  const raw = (location.hash.slice(1) || '/');
  const [path, query = ''] = raw.split('?');
  const params = new URLSearchParams(query);
  const parts = path.split('/').filter(Boolean);
  const type = parts[0] || 'home';
  let id = null;
  try {
    id = parts[1] ? decodeURIComponent(parts[1]) : null;
  } catch {
    $('#breadcrumb').textContent = 'Page not found';
    document.title = 'Page not found — Deep Agents Field Guide';
    setActive('not-found');
    return renderNotFound();
  }
  const chapter = chapters.find(c => c.id === id);
  const names = {home:'Start here',runtime:'Execution lab',source:'Source atlas',glossary:'Concept glossary',about:'Scope & evidence'};
  $('#breadcrumb').textContent = type === 'chapter' ? chapter?.title || 'Chapter not found' : names[type] || 'Page not found';
  document.title = `${$('#breadcrumb').textContent} — Deep Agents Field Guide`;
  setActive(type, type === 'chapter' ? id : null);
  if (type !== 'runtime' || !params.has('step')) window.scrollTo(0, 0);
  try {
    if (type === 'home') renderHome();
    else if (type === 'chapter') renderChapter(id, params.get('section'));
    else if (type === 'runtime') renderRuntime(params.get('scenario') || 'filesystem', params.get('step'));
    else if (type === 'source') await renderAtlas(params, epoch);
    else if (type === 'glossary') renderGlossary();
    else if (type === 'about') await renderAbout(epoch);
    else renderNotFound();
    if (epoch === routeEpoch) {
      prepareDiagrams();
    }
  } catch (error) {
    if (epoch === routeEpoch) main.innerHTML = `<div class="wide-page"><h1>Couldn’t load this page.</h1><p>${escape(error.message)}</p><p>Serve the site over HTTP rather than opening index.html directly. See the README.</p><a href="#/">Back to the guide</a></div>`;
  }
}

function setupSearch() {
  const dialog = $('#search-dialog');
  const open = () => { dialog.showModal(); $('#global-search').focus(); renderSearch(); };
  $('#search-open').addEventListener('click', open);
  $('#search-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
  document.addEventListener('keydown', event => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); if (!dialog.open) open(); else dialog.close(); } });
  $('#global-search').addEventListener('input', renderSearch);
  $('#search-results').addEventListener('click', event => { if (event.target.closest('a')) dialog.close(); });
  function renderSearch() {
    const query = $('#global-search').value.toLowerCase().trim();
    const terms = query.split(/\s+/).filter(Boolean);
    const matches = searchIndex.filter(item => !terms.length || terms.every(term => item.search.includes(term))).slice(0, 30);
    $('#search-results').innerHTML = matches.map(item => { const matchIndex = query ? item.text.toLowerCase().indexOf(terms[0]) : 0; const start = Math.max(0, matchIndex - 65); return `<a class="search-result" href="${chapterUrl(item.chapter.id)}?section=${encodeURIComponent(item.section.id)}"><strong>${escape(item.section.title)}</strong><small>${escape(item.chapter.title)} · ${escape(item.text.slice(start, start + 170))}…</small></a>`; }).join('') || '<p class="empty-state">No matching sections. Try fewer words, or search function names in the source atlas.</p>';
  }
}

async function boot() {
  try {
    const content = await Promise.all(['sdk','backends','applications','agent-loop'].map(name => fetchJson(`content/${name}.json`)));
    const groupOrder = ['Foundations', 'Harness internals', 'Storage & safety', 'Applications', 'Engineering'];
    chapters = content.flat().sort((a, b) => groupOrder.indexOf(a.group) - groupOrder.indexOf(b.group));
    searchIndex = chapters.flatMap(chapter => chapter.sections.map(section => { const text = strip(section.body); return {chapter, section, text, search:`${chapter.title} ${section.title} ${text}`.toLowerCase()}; }));
    buildNavigation(); setupSearch();
    $('#revision-link').href = `https://github.com/langchain-ai/deepagents/tree/${REVISION}`;
    window.addEventListener('hashchange', route);
    $('.skip-link').addEventListener('click', event => {
      event.preventDefault();
      main.focus({preventScroll:true});
      main.scrollIntoView();
    });
    $('#mobile-menu').addEventListener('click', () => setMenuOpen(!$('#sidebar').classList.contains('open')));
    document.addEventListener('click', event => {
      if ($('#sidebar').classList.contains('open') && !event.target.closest('#sidebar, #mobile-menu')) setMenuOpen(false);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') setMenuOpen(false);
    });
    $('#theme-toggle').addEventListener('click', () => { const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = next; try { localStorage.setItem('deepagents-theme', next); } catch { /* Storage can be disabled; the toggle still works. */ } });
    try { document.documentElement.dataset.theme = localStorage.getItem('deepagents-theme') || 'light'; } catch { /* Use the default theme in restricted browsers. */ }
    await route();
  } catch (error) {
    main.innerHTML = `<div class="wide-page"><h1>The guide could not load.</h1><p>${escape(error.message)}</p><p>Start the local HTTP server from this directory, then reload. The site needs all chapter-content JSON files.</p></div>`;
  }
}
boot();
