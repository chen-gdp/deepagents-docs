"""Execute credential-free Agent loop probes against real compiled graphs.

The scripted chat model controls provider responses only; graph scheduling,
checkpointing, middleware, tools, validation, and cancellation remain real.

Authors:
    Deep Agents documentation contributors
References:
    https://github.com/langchain-ai/deepagents/tree/c4e2811312718e98b1465b6e67c34997ca72c793
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import inspect
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Do not send traces even if the invoking shell normally enables LangSmith.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from deepagents import create_deep_agent
from deepagents.middleware.rubric import RubricMiddleware
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
    after_agent,
    after_model,
    wrap_tool_call,
)
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain.tools import ToolRuntime
from langchain_core.exceptions import ContextOverflowError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.errors import GraphRecursionError
from langgraph.graph import END
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import Command
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
PIN = "c4e2811312718e98b1465b6e67c34997ca72c793"
SOURCE_HASHES = {
    "langchain.agents.factory": "cc4a7d9a620224558c4eddd4e13edc988a9ac9e328b7a67deeb71ed2c5ec5174",
    "deepagents.graph": "5964f538571f415331870230b86eae1833f11e52c0d91b38e3c37e6e0c609569",
    "deepagents.middleware.rubric": "6669a81403ad10c98bc6370343aa87f7e889b3b506d4dda77f4e0e1c026c5a43",
}
CASES: list[tuple[str, Any]] = []
RESULTS: list[dict[str, Any]] = []


def plain(value: Any) -> Any:
    """Convert observed objects into JSON-safe evidence."""
    if isinstance(value, BaseModel):
        return plain(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, BaseException):
        return {"type": type(value).__name__, "message": str(value)}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


class ScriptedModel(BaseChatModel):
    """A deterministic provider boundary, not a replacement graph executor."""

    responses: list[Any] = Field(default_factory=list)
    calls: list[Any] = Field(default_factory=list)
    bindings: list[Any] = Field(default_factory=list)
    repeat: bool = False

    @property
    def _llm_type(self) -> str:
        return "offline-agent-loop-fixture"

    def bind_tools(self, tools: Any, **kwargs: Any) -> ScriptedModel:
        """Accept real agent tool binding without requiring a provider."""
        self.bindings.append({"tools": [getattr(t, "name", str(t)) for t in tools], "kwargs": plain(kwargs)})
        return self

    def get_num_tokens(self, text: str) -> int:
        """Use a deterministic token estimate; no tokenizer downloads."""
        return max(1, len(text) // 4)

    def _generate(
        self, messages: list[BaseMessage], stop: Any = None, run_manager: Any = None, **kwargs: Any
    ) -> ChatResult:
        """Return the next explicitly controlled provider response."""
        index = len(self.calls)
        self.calls.append(plain(messages))
        assert self.repeat or index < len(self.responses), f"Graph requested unscripted model turn {index + 1}"
        response = self.responses[0 if self.repeat else index]
        if isinstance(response, BaseException):
            raise response
        return ChatResult(generations=[ChatGeneration(message=response.model_copy(deep=True))])


def ai(*calls: tuple[str, str, dict[str, Any]], text: str = "") -> AIMessage:
    """Build explicit provider tool calls with stable correlation IDs."""
    return AIMessage(
        content=text, tool_calls=[{"name": n, "id": i, "args": a, "type": "tool_call"} for n, i, a in calls]
    )


def case(name: str) -> Any:
    """Register one independently checked scenario."""

    def decorate(fn: Any) -> Any:
        CASES.append((name, fn))
        return fn

    return decorate


class Probe:
    """Collect graph, checkpoint, model inputs, and tool side effects."""

    def __init__(
        self,
        responses: list[Any],
        *,
        deep: bool = True,
        tools: Any = None,
        middleware: Any = (),
        repeat: bool = False,
        **kwargs: Any,
    ) -> None:
        self.events: list[Any] = []
        self.model = ScriptedModel(responses=responses, repeat=repeat)
        serializer = JsonPlusSerializer(allowed_msgpack_modules=[(Receipt.__module__, "Receipt")])
        self.saver = InMemorySaver(serde=serializer)
        self.config = {"configurable": {"thread_id": "verification"}, "max_concurrency": 1}
        self.graph = (create_deep_agent if deep else create_agent)(
            model=self.model, tools=tools or [], middleware=middleware, checkpointer=self.saver, **kwargs
        )
        self.owner = "deepagents.create_deep_agent" if deep else "langchain.agents.create_agent"
        self.observations: dict[str, Any] = {}

    def invoke(self, data: Any = None, **config: Any) -> dict[str, Any]:
        """Run the public graph interface and capture actual checkpoint state."""
        result = self.graph.invoke(
            data if data is not None else {"messages": [HumanMessage("begin")]}, {**self.config, **config}
        )
        self.capture(result)
        return result

    def capture(self, result: Any = None) -> None:
        """Capture terminal or suspended state without asserting it is terminal."""
        state = self.graph.get_state(self.config)
        self.observations.update(
            {
                "result": plain(result),
                "next": list(state.next),
                "checkpoint_messages": plain(state.values.get("messages", [])),
                "tasks": [
                    {"name": t.name, "error": plain(t.error), "interrupts": plain(t.interrupts)} for t in state.tasks
                ],
            }
        )

    def terminal(self) -> None:
        """Assert that no graph node remains scheduled."""
        assert self.graph.get_state(self.config).next == ()

    def evidence(self) -> dict[str, Any]:
        """Return observed runtime facts, including the actual compiled topology."""
        return {
            "graph_owner": self.owner,
            "graph": self.graph.get_graph().to_json(),
            "graph_default_recursion_limit": self.graph.config.get("recursion_limit"),
            "model_calls": len(self.model.calls),
            "model_inputs": self.model.calls,
            "tool_events": plain(self.events),
            **self.observations,
        }


def tools_for(events: list[Any]) -> list[Any]:
    """Create observable real Python tools."""

    @tool
    def record(value: str) -> str:
        """Record a value and return its receipt."""
        events.append({"tool": "record", "value": value})
        return f"recorded:{value}"

    @tool(return_direct=True)
    def direct(value: str) -> str:
        """Return a receipt without requiring model interpretation."""
        events.append({"tool": "direct", "value": value})
        return f"direct:{value}"

    return [record, direct]


def standard(responses: list[Any], *, deep: bool = True, **kwargs: Any) -> Probe:
    """Build a probe with receipt tools bound to its event collection."""
    events: list[Any] = []
    p = Probe(responses, deep=deep, tools=tools_for(events), **kwargs)
    p.events = events
    return p


for name, text in [("no_calls_text", "done"), ("no_calls_empty", "")]:

    @case(name)
    def no_calls(text: str = text) -> Probe:
        p = standard([AIMessage(content=text)])
        r = p.invoke()
        assert len(p.model.calls) == 1 and p.events == []
        assert r["messages"][-1].content == text
        p.terminal()
        return p


@case("provider_length_finish_without_calls_ends")
def length_finish() -> Probe:
    """Prove provider truncation metadata is not a separate retry instruction."""
    p = standard([AIMessage(content="truncated", response_metadata={"finish_reason": "length"})])
    r = p.invoke()
    assert r["messages"][-1].response_metadata["finish_reason"] == "length"
    assert len(p.model.calls) == 1 and p.events == []
    p.terminal()
    return p


@case("done_text_with_call_is_not_stop")
def done_with_call() -> Probe:
    p = standard([ai(("record", "r1", {"value": "one"}), text="done"), AIMessage(content="final")])
    r = p.invoke()
    assert p.events == [{"tool": "record", "value": "one"}]
    assert len(p.model.calls) == 2
    assert r["messages"][-2].tool_call_id == "r1" and r["messages"][-2].content == "recorded:one"
    assert p.model.calls[1][-1]["tool_call_id"] == "r1"
    assert r["messages"][-1].content == "final"
    p.terminal()
    return p


@case("multiple_calls_single_batch")
def multiple_calls() -> Probe:
    p = standard(
        [ai(("record", "r1", {"value": "one"}), ("record", "r2", {"value": "two"})), AIMessage(content="both complete")]
    )
    r = p.invoke()
    assert p.events == [{"tool": "record", "value": "one"}, {"tool": "record", "value": "two"}]
    assert [(m.tool_call_id, m.content) for m in r["messages"] if isinstance(m, ToolMessage)] == [
        ("r1", "recorded:one"),
        ("r2", "recorded:two"),
    ]
    assert len(p.model.calls) == 2
    p.observations["order_note"] = (
        "max_concurrency=1 serializes this probe; production concurrent tool completion order is not guaranteed"
    )
    p.terminal()
    return p


for mixed in [False, True]:

    @case("mixed_return_direct_continues" if mixed else "all_return_direct_stops")
    def direct_case(mixed: bool = mixed) -> Probe:
        calls = [("direct", "d1", {"value": "one"}), ("record" if mixed else "direct", "d2", {"value": "two"})]
        p = standard([ai(*calls), AIMessage(content="mixed interpreted")] if mixed else [ai(*calls)])
        r = p.invoke()
        assert len(p.events) == 2 and len(p.model.calls) == (2 if mixed else 1)
        assert [m.tool_call_id for m in r["messages"] if isinstance(m, ToolMessage)] == ["d1", "d2"]
        assert isinstance(r["messages"][-1], AIMessage if mixed else ToolMessage)
        p.terminal()
        return p


class Receipt(BaseModel):
    """Structured-output schema validated by real LangChain strategies."""

    count: int = Field(ge=1)


@case("tool_strategy_plain_text_with_ordinary_tools_ends_without_schema")
def structured_plain_text_with_tools() -> Probe:
    """Check no-call completion can leave structured output unfulfilled."""
    p = standard([AIMessage(content="plain text, not a schema result")], response_format=ToolStrategy(Receipt))
    result = p.invoke()
    assert len(p.model.calls) == 1 and p.events == []
    assert result.get("structured_response") is None
    assert result["messages"][-1].tool_calls == []
    p.terminal()
    return p


@case("tool_strategy_plain_text_without_ordinary_tools_retries")
def structured_plain_text_without_tools() -> Probe:
    """Check the dependency-only schema loop retries a plain-text response."""
    p = Probe(
        [AIMessage(content="plain text, not a schema result"), ai(("Receipt", "schema_after_text", {"count": 4}))],
        deep=False,
        response_format=ToolStrategy(Receipt),
    )
    result = p.invoke()
    assert len(p.model.calls) == 2 and p.events == []
    assert result["structured_response"] == Receipt(count=4)
    assert result["messages"][-1].tool_call_id == "schema_after_text"
    p.terminal()
    return p


@case("tool_structured_success")
def tool_structured() -> Probe:
    p = Probe([ai(("Receipt", "s1", {"count": 2}))], deep=False, response_format=ToolStrategy(Receipt))
    r = p.invoke()
    assert r["structured_response"] == Receipt(count=2) and len(p.model.calls) == 1
    assert r["messages"][-1].tool_call_id == "s1" and r["messages"][-1].status == "success"
    p.terminal()
    return p


@case("structured_success_with_real_tool_executes_then_ends")
def structured_and_real_tool() -> Probe:
    """Check pending real work takes priority, then structured success stops."""
    p = standard(
        [ai(("Receipt", "schema1", {"count": 5}), ("record", "real1", {"value": "required work"}))],
        deep=False,
        response_format=ToolStrategy(Receipt),
    )
    r = p.invoke()
    assert r["structured_response"] == Receipt(count=5)
    assert p.events == [{"tool": "record", "value": "required work"}] and len(p.model.calls) == 1
    assert [(m.tool_call_id, m.status) for m in r["messages"] if isinstance(m, ToolMessage)] == [
        ("schema1", "success"),
        ("real1", "success"),
    ]
    p.terminal()
    return p


@case("tool_structured_validation_retry")
def tool_structured_retry() -> Probe:
    p = Probe(
        [ai(("Receipt", "bad", {"count": 0})), ai(("Receipt", "good", {"count": 3}))],
        deep=False,
        response_format=ToolStrategy(Receipt),
    )
    r = p.invoke()
    assert len(p.model.calls) == 2 and r["structured_response"] == Receipt(count=3)
    tms = [m for m in r["messages"] if isinstance(m, ToolMessage)]
    assert [m.tool_call_id for m in tms] == ["bad", "good"]
    assert "validation error" in tms[0].content.lower() and tms[1].status == "success"
    p.terminal()
    return p


@case("tool_structured_multiple_outputs_retry")
def structured_multiple() -> Probe:
    p = Probe(
        [ai(("Receipt", "a", {"count": 1}), ("Receipt", "b", {"count": 2})), ai(("Receipt", "c", {"count": 3}))],
        deep=False,
        response_format=ToolStrategy(Receipt),
    )
    r = p.invoke()
    assert len(p.model.calls) == 2 and r["structured_response"] == Receipt(count=3)
    assert [m.tool_call_id for m in r["messages"] if isinstance(m, ToolMessage)] == ["a", "b", "c"]
    p.terminal()
    return p


def mixed_schema_error(calls: list[tuple[str, str, dict[str, Any]]], expected_error: str) -> Probe:
    """Observe schema-error receipts ending a mixed ordinary-tool batch.

    Args:
        calls: Structured-output calls that cannot produce one valid result.
        expected_error: Error text expected in each schema receipt.

    Returns:
        The executed Deep Agents probe with terminal state and no validated result.
    """
    p = standard(
        [ai(*calls, ("record", "real_mixed", {"value": "required work"}))],
        response_format=ToolStrategy(Receipt),
    )
    result = p.invoke()
    assert len(p.model.calls) == 1 and p.events == [{"tool": "record", "value": "required work"}]
    assert result.get("structured_response") is None
    assert p.graph.get_state(p.config).values.get("structured_response") is None
    receipts = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert [(message.tool_call_id, message.status) for message in receipts] == [
        (call[1], "success") for call in calls
    ] + [("real_mixed", "success")]
    assert all(expected_error in str(message.content).lower() for message in receipts[:-1])
    p.observations["structured_output_pitfall"] = (
        "Corrective schema receipts default to status=success; after ordinary work, "
        + "the tools router ends without retrying or producing a validated structured_response."
    )
    p.terminal()
    return p


@case("mixed_tool_structured_validation_error_ends_without_retry")
def mixed_structured_validation() -> Probe:
    """Verify premature completion after invalid schema output plus real work."""
    return mixed_schema_error([("Receipt", "invalid_mixed", {"count": 0})], "validation error")


@case("mixed_tool_multiple_structured_outputs_end_without_retry")
def mixed_structured_multiple() -> Probe:
    """Verify premature completion after multiple schema outputs plus real work."""
    return mixed_schema_error(
        [("Receipt", "schema_a", {"count": 1}), ("Receipt", "schema_b", {"count": 2})],
        "multiple structured responses",
    )


@case("tool_structured_validation_no_retry")
def tool_structured_no_retry() -> Probe:
    """Verify that disabling ToolStrategy recovery propagates invalid output."""
    p = Probe(
        [ai(("Receipt", "invalid_schema", {"count": 0}))],
        deep=False,
        response_format=ToolStrategy(Receipt, handle_errors=False),
    )
    try:
        p.invoke()
    except Exception as exc:
        assert type(exc).__name__ == "StructuredOutputValidationError"
        assert len(p.model.calls) == 1
        p.capture()
        p.observations["exception"] = plain(exc)
        assert p.graph.get_state(p.config).next
    else:
        raise AssertionError("Expected disabled structured-output recovery to raise")
    return p


@case("native_structured_success")
def native_structured() -> Probe:
    p = Probe([AIMessage(content='{"count":4}')], deep=False, response_format=ProviderStrategy(Receipt))
    r = p.invoke()
    assert r["structured_response"] == Receipt(count=4) and len(p.model.calls) == 1
    p.observations["provider_boundary"] = (
        "Offline native-format response parsing, not provider-side constrained generation"
    )
    p.terminal()
    return p


@case("native_invalid_has_no_implicit_validation_retry")
def native_invalid() -> Probe:
    p = Probe([AIMessage(content='{"count":0}')], deep=False, response_format=ProviderStrategy(Receipt))
    try:
        p.invoke()
    except Exception as exc:
        assert type(exc).__name__ == "StructuredOutputValidationError"
        assert len(p.model.calls) == 1
        p.capture()
        p.observations["exception"] = plain(exc)
    else:
        raise AssertionError("Expected native validation failure")
    return p


for destination in ["end", "model", "tools"]:

    @case(f"middleware_explicit_{destination}")
    def middleware_jump(destination: str = destination) -> Probe:
        hits: list[str] = []

        @after_model(can_jump_to=[destination])
        def route(state: Any, runtime: Any) -> Any:
            hits.append("after_model")
            return {"jump_to": destination} if len(hits) == 1 else None

        responses = [ai(("record", "r1", {"value": "one"})), AIMessage(content="routed final")]
        p = standard(responses, deep=False, middleware=[route])
        r = p.invoke()
        assert len(p.model.calls) == (1 if destination == "end" else 2)
        assert len(p.events) == (1 if destination == "tools" else 0)
        if destination == "end":
            assert r["messages"][-1].tool_calls[0]["id"] == "r1"
        p.observations["hook_calls"] = hits
        p.terminal()
        return p


@case("after_agent_can_reenter_model")
def reenter_after_agent() -> Probe:
    hits: list[str] = []

    @after_agent(can_jump_to=["model"])
    def review(state: Any, runtime: Any) -> Any:
        hits.append("review")
        return {"jump_to": "model"} if len(hits) == 1 else None

    p = standard([AIMessage(content="apparent final"), AIMessage(content="reviewed final")], middleware=[review])
    r = p.invoke()
    assert len(p.model.calls) == 2 and hits == ["review", "review"]
    assert r["messages"][-1].content == "reviewed final"
    p.observations["hook_calls"] = hits
    p.terminal()
    return p


@case("router_missing_ai_ends")
def missing_ai() -> Probe:
    @after_model
    def clear_ai(state: Any, runtime: Any) -> Any:
        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), HumanMessage("AI removed")]}

    p = standard([AIMessage(content="removed")], deep=False, middleware=[clear_ai])
    r = p.invoke()
    assert len(p.model.calls) == 1 and all(not isinstance(m, AIMessage) for m in r["messages"])
    p.terminal()
    return p


@case("router_already_answered_calls_reenter_model")
def synthetic_answer() -> Probe:
    @after_model
    def answer(state: Any, runtime: Any) -> Any:
        if state["messages"][-1].tool_calls:
            return {"messages": [ToolMessage(content="answered by middleware", tool_call_id="r1", name="record")]}
        return None

    p = standard(
        [ai(("record", "r1", {"value": "never executed"})), AIMessage(content="synthetic read")],
        deep=False,
        middleware=[answer],
    )
    r = p.invoke()
    assert p.events == [] and len(p.model.calls) == 2
    assert r["messages"][-2].tool_call_id == "r1"
    p.terminal()
    return p


@case("tools_router_missing_ai_returns_to_model")
def tool_removes_ai() -> Probe:
    """Exercise the tools-to-model missing-AI branch through a real tool Command."""

    @tool
    def clear_history(runtime: ToolRuntime) -> Command:
        """Replace conversation history while retaining the required tool receipt."""
        return Command(
            update={
                "messages": [
                    RemoveMessage(id=REMOVE_ALL_MESSAGES),
                    ToolMessage(content="cleared", tool_call_id=runtime.tool_call_id),
                    HumanMessage("continue with clean context"),
                ]
            }
        )

    p = Probe(
        [ai(("clear_history", "clear1", {})), AIMessage(content="continued after clearing")],
        deep=False,
        tools=[clear_history],
    )
    r = p.invoke()
    assert len(p.model.calls) == 2
    assert not any(m["type"] == "ai" for m in p.model.calls[1])
    assert r["messages"][0].tool_call_id == "clear1"
    assert r["messages"][-1].content == "continued after clearing"
    p.terminal()
    return p


for behavior in ["end", "error"]:

    @case(f"model_call_limit_{behavior}")
    def model_limit(behavior: str = behavior) -> Probe:
        """Exercise an explicit opt-in resource limit, distinct from recursion."""
        p = standard(
            [ai(("record", "limit1", {"value": "once"}))],
            middleware=[ModelCallLimitMiddleware(run_limit=1, exit_behavior=behavior)],
        )
        if behavior == "error":
            try:
                p.invoke()
            except Exception as exc:
                assert type(exc).__name__ == "ModelCallLimitExceededError"
                p.capture()
                p.observations["exception"] = plain(exc)
                assert p.graph.get_state(p.config).next
            else:
                raise AssertionError("Expected ModelCallLimitExceededError")
        else:
            r = p.invoke()
            assert "limit" in r["messages"][-1].content.lower()
            p.terminal()
        assert len(p.model.calls) == 1 and p.events == [{"tool": "record", "value": "once"}]
        return p


for behavior in ["continue", "end", "error"]:

    @case(f"tool_call_limit_{behavior}")
    def tool_limit(behavior: str = behavior) -> Probe:
        """Observe blocking, explicit termination, and exception limit policies."""
        p = standard(
            [ai(("record", "limit1", {"value": "blocked"})), AIMessage(content="blocked understood")],
            middleware=[ToolCallLimitMiddleware(run_limit=0, exit_behavior=behavior)],
        )
        if behavior == "error":
            try:
                p.invoke()
            except Exception as exc:
                assert type(exc).__name__ == "ToolCallLimitExceededError"
                p.capture()
                p.observations["exception"] = plain(exc)
                assert p.graph.get_state(p.config).next
            else:
                raise AssertionError("Expected ToolCallLimitExceededError")
        else:
            r = p.invoke()
            tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
            assert tm.tool_call_id == "limit1" and tm.status == "error"
            p.terminal()
        assert p.events == [] and len(p.model.calls) == (2 if behavior == "continue" else 1)
        return p


for direct_command in [False, True]:

    @case(
        "tool_command_end_with_return_direct" if direct_command else "tool_command_end_does_not_override_factory_edge"
    )
    def command_end(direct_command: bool = direct_command) -> Probe:
        events: list[str] = []

        @tool(return_direct=direct_command)
        def finish(runtime: ToolRuntime) -> Command:
            """Request END and return a correlated tool receipt."""
            events.append("finish")
            return Command(
                update={"messages": [ToolMessage(content="command receipt", tool_call_id=runtime.tool_call_id)]},
                goto=END,
            )

        responses = [ai(("finish", "end1", {}))]
        if not direct_command:
            responses.append(AIMessage(content="factory still called model"))
        p = Probe(responses, tools=[finish])
        r = p.invoke()
        assert events == ["finish"] and len(p.model.calls) == (1 if direct_command else 2)
        tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
        assert tm.tool_call_id == "end1" and tm.content == "command receipt"
        assert isinstance(r["messages"][-1], ToolMessage if direct_command else AIMessage)
        p.observations["command_events"] = events
        p.observations["routing_note"] = "Command.goto does not cancel the factory's normal tools-to-model edge"
        p.terminal()
        return p


for decision_type in ["approve", "edit", "reject", "respond"]:

    @case(f"hitl_pause_same_thread_{decision_type}")
    def human_case(decision_type: str = decision_type) -> Probe:
        p = standard(
            [ai(("record", "h1", {"value": "original"})), AIMessage(content="resumed final")],
            interrupt_on={"record": {"allowed_decisions": ["approve", "edit", "reject", "respond"]}},
        )
        paused = p.invoke()
        assert paused["__interrupt__"] and p.events == [] and len(p.model.calls) == 1
        state = p.graph.get_state(p.config)
        assert state.next and any(t.interrupts for t in state.tasks)
        p.observations["pause"] = {"next": list(state.next), "interrupts": plain(paused["__interrupt__"])}
        decision: dict[str, Any] = {"type": decision_type}
        if decision_type == "edit":
            decision["edited_action"] = {"name": "record", "args": {"value": "edited"}}
        if decision_type in ["reject", "respond"]:
            decision["message"] = "human replacement" if decision_type == "respond" else "not authorized"
        r = p.invoke(Command(resume={"decisions": [decision]}))
        assert len(p.model.calls) == 2 and r["messages"][-1].content == "resumed final"
        expected = [{"tool": "record", "value": "edited" if decision_type == "edit" else "original"}]
        assert p.events == (expected if decision_type in ["approve", "edit"] else [])
        tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
        assert tm.tool_call_id == "h1"
        if decision_type == "reject":
            assert tm.status == "error" and "not authorized" in tm.content
        if decision_type == "respond":
            assert tm.status == "success" and tm.content == "human replacement"
        p.terminal()
        return p


@case("handled_tool_exception_continues")
def handled_error() -> Probe:
    @tool
    def broken() -> str:
        """Raise a real tool error."""
        raise ValueError("tool failed deliberately")

    @wrap_tool_call
    def handle(request: Any, handler: Any) -> Any:
        try:
            return handler(request)
        except ValueError as exc:
            return ToolMessage(content=str(exc), tool_call_id=request.tool_call["id"], status="error")

    p = Probe([ai(("broken", "e1", {})), AIMessage(content="recovered")], tools=[broken], middleware=[handle])
    r = p.invoke()
    tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
    assert tm.tool_call_id == "e1" and tm.status == "error" and tm.content == "tool failed deliberately"
    assert len(p.model.calls) == 2 and r["messages"][-1].content == "recovered"
    p.terminal()
    return p


@case("tool_input_validation_error_continues")
def invalid_tool_args() -> Probe:
    p = standard([ai(("record", "invalid", {})), AIMessage(content="validation observed")])
    r = p.invoke()
    tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
    assert p.events == [] and tm.status == "error" and tm.tool_call_id == "invalid"
    assert "value" in tm.content and len(p.model.calls) == 2
    p.terminal()
    return p


@case("unknown_tool_name_returns_error_then_continues")
def unknown_tool_name() -> Probe:
    """Verify that a missing handler returns correlated feedback to the model."""
    p = standard([ai(("not_registered", "unknown1", {})), AIMessage(content="unknown tool handled")])
    result = p.invoke()
    tool_result = next(message for message in result["messages"] if isinstance(message, ToolMessage))
    assert tool_result.status == "error" and tool_result.tool_call_id == "unknown1"
    assert "not_registered is not a valid tool" in tool_result.content
    assert p.events == [] and len(p.model.calls) == 2
    assert result["messages"][-1].content == "unknown tool handled"
    p.terminal()
    return p


@case("malformed_tool_call_ends_then_repairs_next_invocation")
def malformed_tool_call() -> Probe:
    """Separate malformed call parsing, no-call exit, and next-run repair."""
    invalid_response = AIMessage(
        content="",
        invalid_tool_calls=[
            {
                "name": "record",
                "args": "{",
                "id": "bad1",
                "error": "Invalid JSON",
                "type": "invalid_tool_call",
            }
        ],
    )
    p = standard([invalid_response, AIMessage(content="repaired on next invocation")])
    first = p.invoke()
    assert len(p.model.calls) == 1 and p.events == []
    assert first["messages"][-1].tool_calls == []
    assert first["messages"][-1].invalid_tool_calls[0]["id"] == "bad1"
    p.terminal()
    p.observations["first_invocation"] = {"model_calls": 1, "next": [], "valid_tool_calls": []}
    result = p.invoke({"messages": [HumanMessage("Try again")]})
    repairs = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert len(p.model.calls) == 2 and p.events == []
    assert len(repairs) == 1 and repairs[0].tool_call_id == "bad1" and repairs[0].status == "error"
    assert result["messages"][-1].content == "repaired on next invocation"
    p.terminal()
    return p


for error_kind in ["tool", "provider", "context_overflow", "recursion"]:

    @case(f"exception_{error_kind}")
    def exception_case(error_kind: str = error_kind) -> Probe:
        @tool
        def explode() -> str:
            """Raise an unhandled application error."""
            raise RuntimeError("unhandled tool failure")

        if error_kind == "tool":
            p = Probe([ai(("explode", "x1", {}))], tools=[explode])
            expected = RuntimeError
        elif error_kind == "provider":
            p = standard([RuntimeError("offline provider failure")])
            expected = RuntimeError
        elif error_kind == "context_overflow":
            p = standard([ContextOverflowError("irreducible offline context overflow")], repeat=True)
            expected = ContextOverflowError
        else:
            p = standard([ai(("record", "loop", {"value": "again"}))], repeat=True)
            expected = GraphRecursionError
        try:
            p.invoke(**({"recursion_limit": 8} if error_kind == "recursion" else {}))
        except expected as exc:
            p.capture()
            p.observations["exception"] = plain(exc)
            assert p.graph.get_state(p.config).next, "Failed run must not be mislabeled completed"
            if error_kind in ["tool", "provider"]:
                assert len(p.model.calls) == 1
            if error_kind == "context_overflow":
                assert len(p.model.calls) == 1 and p.events == []
                assert "after recovery" in str(exc)
            if error_kind == "recursion":
                assert len(p.model.calls) == 4 and len(p.events) == 3
                assert p.graph.get_state(p.config).next == ("tools",)
        else:
            raise AssertionError(f"Expected {expected.__name__}")
        return p


@case("child_ends_parent_continues")
def child_end() -> Probe:
    child_model = ScriptedModel(responses=[AIMessage(content="child final")])
    child = create_agent(model=child_model)
    p = standard(
        [
            ai(("task", "child1", {"subagent_type": "worker", "description": "complete one task"})),
            AIMessage(content="parent final after child"),
        ],
        subagents=[{"name": "worker", "description": "A deterministic worker", "runnable": child}],
    )
    r = p.invoke()
    tm = next(m for m in r["messages"] if isinstance(m, ToolMessage))
    assert tm.tool_call_id == "child1" and tm.content == "child final"
    assert len(p.model.calls) == 2 and r["messages"][-1].content == "parent final after child"
    assert len(child_model.calls) == 1
    p.observations["child_model_calls"] = len(child_model.calls)
    p.observations["child_graph"] = child.get_graph().to_json()
    p.terminal()
    return p


for outcome in ["satisfied", "failed", "revision_then_satisfied", "max_iterations_reached", "grader_error"]:

    @case(f"rubric_{outcome}")
    def rubric_case(outcome: str = outcome) -> Probe:
        def grade(result: str, index: int) -> AIMessage:
            args = {
                "result": result,
                "explanation": "controlled rubric verdict",
                "criteria": []
                if result == "failed"
                else [
                    {
                        "name": "Answer meets the stated criterion",
                        "passed": result == "satisfied",
                        **({} if result == "satisfied" else {"gap": "Revise the answer"}),
                    }
                ],
            }
            return ai(("GraderResponse", f"g{index}", args))

        statuses = (
            ["needs_revision", "satisfied"]
            if outcome == "revision_then_satisfied"
            else (["needs_revision"] * 3 if outcome == "max_iterations_reached" else [outcome])
        )
        grader = ScriptedModel(
            responses=[RuntimeError("grader unavailable")]
            if outcome == "grader_error"
            else [grade(s, i) for i, s in enumerate(statuses)]
        )
        middleware = RubricMiddleware(model=grader)
        count = len(statuses)
        p = standard([AIMessage(content=f"draft {i}") for i in range(count)], middleware=[middleware])
        result = p.invoke({"messages": [HumanMessage("write answer")], "rubric": "Answer meets the stated criterion"})
        r = p.graph.get_state(p.config).values
        expected = "satisfied" if outcome == "revision_then_satisfied" else outcome
        assert r["_rubric_status"] == expected
        assert r["_rubric_iterations"] == count and len(p.model.calls) == count and len(grader.calls) == count
        assert len(r["_rubric_evaluations"]) == count
        assert result["messages"][-1].content == f"draft {count - 1}"
        p.observations["rubric"] = {k: plain(v) for k, v in r.items() if k.startswith("_rubric")}
        p.observations["rubric_output_note"] = (
            "Internal rubric keys are visible in get_state(config).values, filtered from invoke output"
        )
        p.observations["grader_calls"] = len(grader.calls)
        p.terminal()
        return p


for cancel_mode in ["timeout", "cancel"]:

    @case(f"async_{cancel_mode}_cleanup")
    async def async_cleanup(cancel_mode: str = cancel_mode) -> Probe:
        started = asyncio.Event()
        cleaned = asyncio.Event()
        events: list[str] = []

        @tool
        async def wait_for_signal() -> str:
            """Block until externally cancelled, always releasing owned resources."""
            events.append("started")
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                events.append("cleaned")
                cleaned.set()
            return "unreachable"

        p = Probe([ai(("wait_for_signal", "a1", {}))], tools=[wait_for_signal])
        task = asyncio.create_task(p.graph.ainvoke({"messages": [HumanMessage("begin")]}, p.config))
        await asyncio.wait_for(started.wait(), 5)
        if cancel_mode == "timeout":
            try:
                await asyncio.wait_for(task, 0.02)
            except TimeoutError as exc:
                error = exc
            else:
                raise AssertionError("Expected caller deadline")
        else:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError as exc:
                error = exc
            else:
                raise AssertionError("Expected explicit cancellation")
        await asyncio.wait_for(cleaned.wait(), 5)
        assert task.done() and task.cancelled() and events == ["started", "cleaned"]
        p.capture()
        assert p.graph.get_state(p.config).next
        p.observations.update(
            {
                "exception": plain(error),
                "async_events": events,
                "cleanup_observed": cleaned.is_set(),
                "task_cancelled": task.cancelled(),
            }
        )
        return p


def source_record(module_name: str, ranges: list[list[int]], url: str, snapshot: bool = False) -> dict[str, Any]:
    """Record the actual installed source bytes and optional public snapshot."""
    import importlib

    module = importlib.import_module(module_name)
    path = Path(inspect.getfile(module))
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == SOURCE_HASHES[module_name], f"Pinned verification source changed: {module_name}"
    result = {
        "module": module_name,
        "installed_path": str(path),
        "sha256": digest,
        "lines": len(data.splitlines()),
        "ranges": ranges,
        "source_url": url,
    }
    if snapshot:
        destination = ROOT / "evidence" / "langchain-1.4.8-agent-factory.py"
        destination.write_bytes(data)
        result["snapshot"] = str(destination.relative_to(ROOT))
    return result


async def main() -> None:
    """Run every scenario and persist factual evidence, including failures."""
    expected = {
        "deepagents": "0.7.32",
        "langchain": "1.4.8",
        "langchain-core": "1.7.6",
        "langgraph": "1.2.20",
        "langgraph-prebuilt": "1.1.1",
    }
    for package, version in expected.items():
        assert importlib.metadata.version(package) == version, f"Install requirements-verification.txt: {package}"
    for name, fn in CASES:
        try:
            p = await fn() if inspect.iscoroutinefunction(fn) else fn()
            RESULTS.append({"name": name, "status": "passed", **p.evidence()})
            print(f"PASS {name}")
        except Exception as exc:
            RESULTS.append(
                {"name": name, "status": "failed", "exception": plain(exc), "traceback": traceback.format_exc()}
            )
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    packages = {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "interpreter": sys.executable,
        "platform": platform.platform(),
        "deepagents_commit": PIN,
        "langchain_release_commit": "5dcec1858191a6b54cd843dd8e54d856e2e007cc",
        "routing_source_release_match": {
            "sha256": "cc4a7d9a620224558c4eddd4e13edc988a9ac9e328b7a67deeb71ed2c5ec5174",
            "method": "Release-tag commit raw factory.py downloaded once and byte-compared with installed wheel source",
            "network_required_for_script": False,
        },
        "install_commands": [
            "/home/christian/miniconda3/bin/python -m venv .venv",
            ".venv/bin/python -m pip install -r requirements-verification.txt",
            ".venv/bin/python verify_agent_loop.py",
        ],
        "initial_install": (
            ".venv/bin/python -m pip install /tmp/deepagents-study-source/libs/deepagents " + "langchain==1.4.8"
        ),
        "packages": dict(sorted(packages.items())),
        "sources": [
            source_record(
                "langchain.agents.factory",
                [[237, 260], [1297, 1345], [1955, 2109]],
                "https://github.com/langchain-ai/langchain/blob/5dcec1858191a6b54cd843dd8e54d856e2e007cc/libs/langchain_v1/langchain/agents/factory.py",
                True,
            ),
            source_record(
                "deepagents.graph",
                [[1008, 1030]],
                f"https://github.com/langchain-ai/deepagents/blob/{PIN}/libs/deepagents/deepagents/graph.py",
            ),
            source_record(
                "deepagents.middleware.rubric",
                [[659, 720], [739, 831], [1229, 1273]],
                f"https://github.com/langchain-ai/deepagents/blob/{PIN}/libs/deepagents/deepagents/middleware/rubric.py",
            ),
        ],
        "scope": (
            "Standalone documentation verification harness; "
            + "not the upstream test suite or a live-provider evaluation"
        ),
        "boundaries": [
            (
                "Provider responses are deliberately scripted; "
                + "no provider network/model call or provider-side enforcement was exercised."
            ),
            "Provider-hosted server tools and real remote background-job reconciliation are source-only boundaries.",
            (
                "max_concurrency=1 makes ordered receipt assertions reproducible; "
                + "it is not a universal concurrency ordering promise."
            ),
            (
                "Timeout is the caller's asyncio.wait_for deadline, not an agent completion condition; "
                + "owned async tool cleanup was observed."
            ),
            "Terminal means checkpoint.next is empty, not that model prose or task quality is correct.",
            (
                "Failed/cancelled checkpoints can retain pending nodes; "
                + "no rollback or automatic external-side-effect cancellation is promised."
            ),
        ],
        "summary": {
            "total": len(RESULTS),
            "passed": sum(r["status"] == "passed" for r in RESULTS),
            "failed": sum(r["status"] == "failed" for r in RESULTS),
        },
        "cases": RESULTS,
    }
    destination = ROOT / "evidence" / "agent-loop-runtime.json"
    destination.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(evidence["summary"]))
    if evidence["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
