# DeepAgents memory, conversation state, context and RAM

Research date: 2026-11-10.

## Scope and conclusion

This report investigates the version used by [the published execution lab](https://chen-gdp.github.io/deepagents-docs/#/runtime): DeepAgents **0.7.32**, commit [`c4e2811312718e98b1465b6e67c34997ca72c793`](https://github.com/langchain-ai/deepagents/tree/c4e2811312718e98b1465b6e67c34997ca72c793). It does not assert that every DeepAgents release behaves identically.

The published `content/sdk.json`, `walkthrough.js` and execution diagram matched the local files during this investigation. The runtime walkthrough is an illustrative teaching projection, not a live model execution or a captured production trace.

**Memory and context are related, but not interchangeable capabilities.** Native `memory=[...]` loads selected files and injects their contents into the system prompt. Conversation persistence, cross-thread storage, context compaction and process RAM are separate concerns.

The research used primary source code embedded in the site's immutable source atlas, the matching installed package, official documentation, and six credential-free scenarios against real compiled graphs. Two independent read-only investigations covered native memory/storage and context/retention separately.

## 1. What each term means

| Mechanism | Purpose | Actual implementation and lifetime |
| --- | --- | --- |
| Standing file-based memory | Supply conventions, preferences and instructions that should remain available | Optional `MemoryMiddleware`; downloads configured paths into private `memory_contents` state and appends the formatted text to each model request. |
| Conversation state | Maintain the current thread's messages and other agent fields | LangGraph state; continuity across invocations depends on state restoration, normally a configured checkpointer and stable thread ID. |
| Persistent cross-thread files | Share saved knowledge across conversations | An appropriate backend, such as `StoreBackend` with a shared store and an explicitly chosen namespace. Actual restart durability depends on the store implementation. |
| Context management | Control what fits in the model's next request | Summarization, selected history, file/result offloading and subagent isolation. It is a request projection, not necessarily deletion of saved data. |
| Semantic memory retrieval | Find relevant past facts/history by meaning | Not automatically implemented by native `memory=[...]`. An ingestion and retrieval integration must be supplied separately. |
| Process RAM | Hold Python objects during execution | Includes messages, files, cached memory, serialization and provider requests. No fixed-RAM guarantee follows from context compaction. |

Primary implementation: [graph construction][graph-stack], [memory middleware][memory-loading], [state backend][state], [store backend][store], [summarization projection][summary-projection].

## 2. Native `memory=[...]`: exact flow

1. **Configure source paths.** `create_deep_agent(memory=None)` does not install native memory middleware. A non-`None` list, including an empty list, installs it. The default backend is `StateBackend()`, not the host filesystem. A host file exists only for the agent if the configured backend exposes it. [Construction][graph-stack]
2. **Load at invocation startup when the cache key is absent.** `before_agent` or `abefore_agent` downloads the configured files in one backend call and decodes their complete contents as UTF-8. It returns a path-to-text `memory_contents` dictionary. Construction alone does not read these files. [Loading][memory-loading]
3. **Reuse existing state.** If the current state already contains the `memory_contents` key, all reads are skipped, even when its value is `{}`. There is no modification-time, freshness or completeness check. [Loading][memory-loading]
4. **Inject on each model call.** `modify_request` reads cached contents, preserves configured source order, removes HTML comments/trailing whitespace, and appends the memory template to the system message. All included text is used; this path does not rank memories, select top-k results, generate embeddings or enforce a memory-specific token limit. [Formatting][memory-formatting]
5. **Keep storage and learning separate.** The default template asks the model to record durable knowledge using `edit_file`. It does not guarantee the model will do so, and there is no automatic fact-extraction/writeback pipeline. Saving a file is an ordinary tool operation. [Learning instructions][memory-guidelines]

### Loading edge cases

- Missing files are skipped. An empty cache is still recorded, so creating the file later does not automatically reload it in that same restored state.
- Other backend response errors raise `ValueError`; invalid UTF-8 and uncaught backend exceptions propagate.
- `memory_contents` is private agent state: absent from ordinary final output, but inspectable through checkpoint state. **Private is not equivalent to encrypted or secret.** Its contents also reach the model when injection is enabled.
- `MemoryMiddleware(system_prompt=None)` suppresses this middleware's prompt fragment but still loads the cache. `create_deep_agent(system_prompt=None)` does not disable installed memory injection.

Source: [memory loading and state declarations][memory-loading]; [request modification][memory-formatting].

### Stale-cache behavior: confirmed, not merely inferred

The offline scenarios used a real `FilesystemBackend`, native memory middleware and `InMemorySaver`:

1. First invocation loaded a red preference marker.
2. An external write changed the file to a blue marker.
3. A second invocation on the same checkpointed thread still injected red.
4. A new thread loaded blue.
5. Separately, the agent's real native `edit_file` changed red to green on disk, but its next model call and its next same-thread invocation still injected the old red cache.

A successful file edit therefore proves **storage changed**, not **the cached system prompt refreshed**. The tool result and conversation can still expose the updated information to the model; this finding is specifically about the cached memory fragment.

An integration requiring immediate refresh must explicitly manage cache freshness/invalidation. A fresh thread demonstrates reload but is not a general refresh solution because it also starts a different conversation. This report does not prescribe an unverified cache-reset API.

Evidence: [`memory-runtime.json`](memory-runtime.json); [cache check and request read][memory-loading].

## 3. Conversation persistence is not cross-thread memory

`create_deep_agent` accepts `checkpointer` and `store` separately; both default to `None`. Supplying a store does not automatically replace `StateBackend` or register memory files. [Graph arguments and forwarding][graph-persistence]

- **Checkpointer:** restores a graph thread's execution state, supporting subsequent turns and resumable workflows when configured correctly.
- **StateBackend:** stores virtual files in that graph's `files` channel. It does not write them to host disk or make them available to unrelated threads.
- **StoreBackend:** stores file values under a caller-provided namespace in a `BaseStore`. Two different threads can read the same file when their store and namespace agree.
- **CompositeBackend:** routes paths to different backends, commonly temporary/thread files by default and shared memory paths to a store. Routing a directory does not by itself inject every file in it into the prompt.

Sources: [StateBackend][state], [StoreBackend][store], [CompositeBackend routing][composite].

The offline cross-thread experiment used `InMemoryStore`: two separate threads read the same saved preference in the same namespace; another namespace did not read it. **This proves cross-thread sharing, not survival of a process restart.**

Namespace syntax validation is not authentication. Production isolation requires trusted identity-based namespace selection and access controls; a constant namespace intentionally shares data. Hierarchical store prefixes must not be mistaken for an authorization boundary. [Namespace implementation][store]

## 4. Native memory is not automatic semantic recall

`MemoryMiddleware` downloads exact configured file paths. `StoreBackend.download_files` fetches exact keys. Filesystem `grep` and `glob` are literal-text/path mechanisms, not a semantic user-history index. [Store retrieval implementation][store-retrieval]

Even if the underlying store supports embeddings, native `memory=[...]` does not automatically:

1. Extract durable facts from every conversation.
2. Embed and index those facts.
3. Search for relevant past interactions before each run.
4. Resolve conflicting or outdated memories.
5. Apply tenant-specific retention and deletion policies.

DeepAgents can be extended with retrieval tools or middleware. Those integration responsibilities should be named explicitly rather than silently attributed to `memory=[...]`.

For the GL Agent comparison, standing instruction memory and a GL semantic-memory integration should therefore not be presented as the same feature. This investigation does not revalidate the GL memory product/API itself.

## 5. Context compaction changes the request, not normally the raw history

The default graph installs the DeepAgents summarization factory. At this pinned revision:

| Resolved model metadata | Automatic trigger | Recent history retention |
| --- | --- | --- |
| Dictionary profile with integer `max_input_tokens` | 85% of advertised input capacity | 10% of that capacity |
| No qualifying capacity metadata | 170,000 tokens | Last 6 messages |

These are factory defaults, not universal provider capacities. The fallback is especially not evidence that a smaller model accepts 170,000 tokens. Approximate token counting and a separate known-budget check also affect when compaction occurs. [Defaults][summary-defaults]

The normal compaction flow is:

1. Prepare the history used for summarization; old tool arguments may already have been shortened.
2. Attempt to archive older history through the configured backend.
3. Produce a summary and save a private `_summarization_event` describing the summary and cutoff.
4. Send the summary plus a recent suffix of history to the next model call.
5. Normally retain original `state['messages']`; special overflow-result replacements are a separate path.

Source: [effective history projection][summary-projection]; [event-only update][summary-update].

The controlled runtime experiment used an explicit 4-message trigger and 2-message keep setting, **not the default production thresholds**. After compaction, the provider-bound fixture saw **4 messages including its system message**, while returned graph state contained **10 conversation messages**. The earliest original exchange remained in graph state and in the generated archive, but not in the next model request.

### Archive limits

The default history path is `/conversation_history/session_<id>.md`, adjusted by a composite backend's artifacts root. Archive fidelity is not identical to raw state: prior tool-argument truncation and media conversion can change the archived representation. Archive failures do not necessarily abort summarization; the summary can proceed without claiming a successful recovery path. [Archive implementation][summary-archive]; [summary archive failure handling][summary-update]

Do not promise a lossless original transcript in the archive or guaranteed archive durability without checking the backend and failure behavior.

## 6. Memory itself consumes context, and budgeting has an ordering caveat

Native memory is fully included on each model call rather than progressively disclosed. Conversation summarization does not automatically shorten the memory file's system-prompt fragment. Provider prompt caching, when applicable, is an optimization; it does not remove the text from the model's context window. [Formatting and cache-control logic][memory-formatting]

**Confirmed middleware-order limitation:** the native stack places summarization outside later memory injection. In an actual compiled graph with a recording summarization counter:

- The counter saw caller-authored system text.
- The counter did not see a uniquely marked memory fragment.
- The actual provider-bound request did contain that memory fragment.

This experiment supplied a custom recording counter and high explicit threshold. It did not simulate provider rejection or establish an end-to-end overflow failure. It demonstrates that the counter at that layer is not necessarily measuring the final request after later middleware additions. [Stack ordering][graph-stack]; [counting implementation][summary-counting]

Consequently, the website's phrases **“count the complete request”** and **“messages, system content, and tools all contribute”** need this qualification: fields present at the summarization layer are counted, but later prompt injections are not necessarily included. A memory-heavy setup must account for that additional input rather than assume compaction's estimate is the final provider payload size.

## 7. Large tool outputs and RAM

Tool offloading moves large text out of inline model context into backend files, replacing it with a path and preview when archival succeeds. The generic default threshold is nominally 20,000 tokens, implemented using a text-character heuristic; it is not a promise that an arbitrary 20,000-token payload has been measured with the provider tokenizer. Several native filesystem tools use separate handling. [Offloading implementation][tool-offload]

**Offloading to `StateBackend` does not move data out of Python graph state:** it can move data from a message to the `files` channel. Combined with retained raw conversation, memory caches and in-memory checkpoint/store implementations, substantial data can remain resident.

Source-grounded growth/peak-allocation considerations:

- Raw message history can grow despite summary projection.
- State-backed files can accumulate reports, offloaded results and history archives.
- `memory_contents` holds full decoded memory sources.
- Archive updates read the existing archive and construct a combined string; they are not a streaming append.
- An in-memory saver/store is not a disk-backed retention policy.

No RSS, peak-RAM, leak or quantitative memory-reduction measurement was made. The probes establish logical retention and request projection only. Production RAM conclusions need workload-specific profiling and explicit state/checkpoint/file retention policies. [Archive construction][summary-archive]; [state storage][state]

## 8. Subagent caveat

Sharing files does not imply sharing the same automatically injected memory or complete conversation:

- The default general-purpose and ordinary isolated declarative subagents do not automatically receive the parent's native memory middleware/cache.
- Declarative fork-mode children receive parent memory middleware and inherited private state, so the cache normally remains the inherited snapshot.
- Opaque compiled children are not automatically rebuilt with parent memory middleware.

These are source-audited findings, not additional runtime experiments in this investigation. Configure required child behavior explicitly and distinguish instruction inheritance from backend access. [Child stack assembly][child-memory]; [private-state filtering and fork input][child-filtering]

## 9. Website assessment and recommended capability names

The existing [memory chapter](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-knowledge?section=sdk-knowledge-memory) already correctly describes explicit loading, state caching, stale source edits and the lack of semantic retrieval. The [context chapter](https://chen-gdp.github.io/deepagents-docs/#/chapter/sdk-context) distinguishes request compaction from raw state.

The execution lab has three illustrative scenarios—filesystem, approval and delegation—not a dedicated memory lifecycle scenario. The inspected published runtime assets do not contain the exact label “Memory and context.” That phrase is assessed here as a proposed capability grouping, not an attributed quote from the runtime page.

**Recommendation:** use “Memory and context” only as a broad section heading. List separately:

1. **Standing instructions and preferences:** load explicitly configured memory files.
2. **Conversation continuity:** save/resume authorized threads.
3. **Shared long-term storage:** save knowledge across threads with appropriate namespaces and durable storage.
4. **Semantic memory integration, if required:** extract/retrieve relevant past knowledge through a separately specified integration.
5. **Context-window management:** summarize, offload and isolate work to fit model requests.

Confirmed wording qualifications worth applying in a later website-edit request:

- Complete-request budgeting must acknowledge later memory injection.
- A history archive is not guaranteed to preserve every original argument/media byte or succeed.
- Saving a memory file does not imply immediate cached prompt refresh.
- Context compaction is not a fixed-RAM guarantee.

**No website content or publication was changed by this research.** Only this report and its local runtime evidence were added.

## 10. Verification evidence and limits

[`memory-runtime.json`](memory-runtime.json) records six passing targeted scenarios:

1. File-backed prompt injection, checkpointed stale cache and fresh-thread reload.
2. A real native `edit_file` write without automatic memory-cache refresh.
3. Missing-file/empty-cache behavior before and after file creation.
4. Cross-thread store sharing and a different namespace's missing file.
5. Native summary projection while raw state and a history archive retain the earlier text.
6. Visibility of caller system text versus later injected memory at the summarization counter.

Environment: existing Conda-derived `~/Projects/deepagents-docs/.venv/bin/python`; base `/home/christian/miniconda3`; DeepAgents 0.7.32, LangChain 1.4.8, LangGraph 1.2.20. Installed `graph.py`, `middleware/memory.py`, `middleware/summarization.py` and `backends/store.py` matched the pinned atlas source exactly.

Actual graph scheduling, native filesystem tools, backend operations, memory hooks, checkpoint restoration and summarization event handling ran. Model responses and summary text were controlled offline fixtures. `InMemorySaver` and `InMemoryStore` were real dependency implementations. There were no provider calls, external storage services, live-model judgments, process-restart tests or RAM profiling. Temporary fixture files were automatically removed. The full upstream test suite was not run.

## Primary sources

- [Official context engineering guide](https://docs.langchain.com/oss/python/deepagents/context-engineering): useful conceptual overview; live documentation can describe a newer version than this site's pinned source. Its in-memory examples should not be mistaken for process-restart durability.
- Pinned implementation links below define the exact behavior researched here.

[graph-stack]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/graph.py#L906-L964
[graph-persistence]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/graph.py#L1008-L1030
[memory-loading]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/memory.py#L87-L344
[memory-formatting]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/memory.py#L244-L382
[memory-guidelines]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/memory.py#L104-L168
[state]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/backends/state.py#L38-L119
[store]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/backends/store.py#L90-L168
[store-retrieval]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/backends/store.py#L601-L727
[composite]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/backends/composite.py#L195-L291
[summary-defaults]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/summarization.py#L288-L325
[summary-projection]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/summarization.py#L902-L961
[summary-update]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/summarization.py#L1661-L1727
[summary-archive]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/summarization.py#L1330-L1405
[summary-counting]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/summarization.py#L1098-L1136
[tool-offload]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/_message_eviction.py#L176-L279
[child-memory]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/graph.py#L732-L885
[child-filtering]: https://github.com/langchain-ai/deepagents/blob/c4e2811312718e98b1465b6e67c34997ca72c793/libs/deepagents/deepagents/middleware/subagents.py#L748-L836
