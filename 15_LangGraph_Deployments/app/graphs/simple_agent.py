"""A minimal tool-using agent graph.

The graph:
- Calls a chat model bound to the tool belt.
- If the last message requested tool calls, routes to a ToolNode.
- Otherwise, terminates.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.models import get_chat_model
from app.state import MessagesState
from app.tools import get_tool_belt_async


def _build_model_with_tools():
    """Return a chat model instance bound to the current tool belt."""
    model = get_chat_model()
    return model.bind_tools(get_tool_belt())


async def call_model(state: MessagesState) -> dict:
    """Invoke the model with the accumulated messages and append its response."""
    tools = await get_tool_belt_async()
    model = get_chat_model()
    model_with_tools = model.bind_tools(tools)
    response = await model_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    async def action_node(state: MessagesState) -> dict:
        tools = await get_tool_belt_async()
        tool_node = ToolNode(tools)
        return await tool_node.ainvoke(state)

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("action", action_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "action", END: END})
    graph.add_edge("action", "agent")
    return graph



# Export compiled graph for LangGraph
graph = build_graph().compile()
