"""Toolbelt assembly for agents.

Collects third-party tools, local tools (RAG), and MCP-server tools into a
single list that graphs can bind to their language models.

MCP server must be running before graphs are initialised:
    python mcp_server.py          # starts http://localhost:8000/mcp
"""
from __future__ import annotations

import asyncio
import logging
from typing import List

from langchain_tavily import TavilySearch
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.rag import retrieve_information

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP server connection config
# ---------------------------------------------------------------------------
MCP_SERVER_URL = "http://localhost:8000/mcp"

_MCP_CONFIG: dict = {
    "local_toolbelt": {
        "transport": "http",          # Streamable HTTP (MCP spec 2025-03-26)
        "url": MCP_SERVER_URL,
    }
}


# ---------------------------------------------------------------------------
# Async helper: fetch tools from MCP server
# ---------------------------------------------------------------------------
async def get_mcp_tools() -> List:
    """Connect to the local MCP server and return its tools as LangChain tools.

    Each call creates a fresh stateless session (MultiServerMCPClient default).
    Returns an empty list and logs a warning if the server is unreachable so
    the rest of the toolbelt still works during development.
    """
    try:
        client = MultiServerMCPClient(_MCP_CONFIG)
        return await client.get_tools()
    except Exception as exc:
        logger.warning(
            "Could not reach MCP server at %s — MCP tools will be unavailable. "
            "Start the server with: python mcp_server.py\n  Error: %s",
            MCP_SERVER_URL,
            exc,
        )
        return []


# ---------------------------------------------------------------------------
# Sync convenience wrapper (for use in synchronous graph factories)
# ---------------------------------------------------------------------------
def get_mcp_tools_sync() -> List:
    """Synchronous wrapper around get_mcp_tools() for non-async call sites."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already inside an event loop (e.g. Jupyter / LangGraph async context)
            # — callers should prefer await get_mcp_tools() directly.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, get_mcp_tools())
                return future.result()
        return loop.run_until_complete(get_mcp_tools())
    except Exception as exc:
        logger.warning("MCP tools sync fetch failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_tool_belt() -> List:
    """Return all tools available to agents.

    Combines:
      - TavilySearch      (web search)
      - ArxivQueryRun     (academic paper lookup)
      - retrieve_information  (project RAG)
      - MCP tools: summarize_text, calculate, fetch_weather
        (requires mcp_server.py to be running)
    """
    base_tools = [
        TavilySearch(max_results=5),
        ArxivQueryRun(),
        retrieve_information,
    ]
    mcp_tools = get_mcp_tools_sync()
    return base_tools + mcp_tools


async def get_tool_belt_async() -> List:
    """Async version of get_tool_belt() — preferred inside LangGraph nodes."""
    base_tools = [
        TavilySearch(max_results=5),
        ArxivQueryRun(),
        retrieve_information,
    ]
    mcp_tools = await get_mcp_tools()
    return base_tools + mcp_tools



