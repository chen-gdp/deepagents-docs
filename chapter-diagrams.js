export const chapterDiagrams = {
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
