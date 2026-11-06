export const chapterDiagrams = {
  'sdk-agent-loop-overview': {
    name: 'agent-loop-routing', width: 660, height: 540,
    alt: 'Simplified ordinary agent loop: a model returns an AIMessage; pending calls execute through the tool dispatcher and correlated results return to the model; no calls proceeds through completion hooks to END.',
    caption: 'Simplified normal flow, not literal compiled topology. The branches are alternatives. Direct returns, structured output, already-answered calls, and hook-driven re-entry are explained separately below; an ordinary tool result is not itself the final answer.',
  },
  'sdk-agent-loop-graph': {
    name: 'agent-loop-compiled', width: 660, height: 704,
    alt: 'Measured six-node compiled graph: start, startup call repair, model, tools, parent notifier, and end. Conditional paths include model re-entry and tool-to-completion routing.',
    caption: 'Extracted from the tested default custom-tools configuration: six nodes and eight possible edges, not a mandatory sequence. Short labels map to PatchToolCallsMiddleware.before_agent and _ParentNotifierMiddleware.after_agent. The actual graph JSON is in the runtime evidence; wrappers and other configurations can change behavior.',
  },
  'sdk-agent-loop-interrupt': {
    name: 'agent-loop-outcomes', width: 660, height: 408,
    alt: 'Non-directional comparison: completed means the invocation reached END, paused means a resumable interrupt, and failed or cancelled means abnormal termination. None guarantees task correctness or side-effect rollback.',
    caption: 'Outcome categories, not successive stages. An interrupt is not END; an exception or cancellation is not ordinary completion. Any outcome may leave external side effects in place.',
  },
  'sdk-construction-parameters': {
    name: 'construction', width: 660, height: 630,
    alt: 'Construction resolves model, profile and backend; prepares middleware stacks; builds a LangChain graph; returns a runnable for later execution.',
    caption: 'Construction is not execution. The factory prepares configuration, prompts, tools and middleware before returning a graph that the application can invoke or stream.',
  },
  'sdk-state-projections': {
    name: 'state-flow', width: 760, height: 395,
    alt: 'Graph state is projected into a model request. Model and tool work produce state writes, which reducers merge for the next iteration.',
    caption: 'Follow the arrows. This is a conceptual data-flow cycle, not the literal compiled node topology. Raw state, effective requests, and streamed observations are different views. Token chunks are not canonical message writes; restoring a checkpoint does not roll back external effects.',
  },
  'sdk-delegation-isolation': {
    name: 'delegation', width: 660, height: 630,
    alt: 'An inline task prepares child input, invokes the child graph, filters its output, then updates the parent through a Command and correlated ToolMessage.',
    caption: 'This is the inline task boundary, not the remote background-task lifecycle. A normal isolated task starts a fresh task conversation; a fork inherits effective history. Eligible state and backend access can still be shared.',
  },
  'composite-routing-dispatch': {
    name: 'routing', width: 760, height: 615,
    alt: 'A file path chooses exactly one backend: the longest matching route strips its mount prefix; otherwise the default backend receives the original path.',
    caption: 'The branches are alternatives, not parallel work. This shows one path-based file operation. Bulk search has additional aggregation behavior, and execute belongs to the default backend rather than following file mounts.',
  },
  'code-runtime-launch': {
    name: 'code-processes', width: 760, height: 385,
    alt: 'The interactive terminal client exchanges requests and streamed output with a graph server, which invokes a local or remote tool backend.',
    caption: 'Interactive Code separates client presentation from server-owned execution. The HTTP connection also carries streamed SSE output. Tool backend names a capability boundary, not necessarily a third process; other launch modes have different assembly paths.',
  },
};
