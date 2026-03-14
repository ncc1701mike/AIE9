# ============================================================
# ACTIVITY 1 — Cache Performance Testing
# Paste into Cell 16
# ============================================================

import time
from app.caching import setup_llm_cache
from app.rag import retrieve_information

setup_llm_cache(cache_type="memory")

# --- Embedding Cache Test ---
# First call: cold — PDFs are chunked, embedded, and stored in Qdrant
# Subsequent calls with the same text hit the local embedding cache

embedding_test_queries = [
    "What vaccinations do cats need?",
    "How do I know if my cat is sick?",
    "What should I feed a senior cat?",
]

print("=" * 55)
print("EMBEDDING CACHE TEST")
print("=" * 55)

embedding_times = {}

for query in embedding_test_queries:
    times = []
    for i in range(2):
        start = time.time()
        retrieve_information.invoke(query)
        elapsed = time.time() - start
        times.append(elapsed)
        label = "MISS (cold)" if i == 0 else "HIT  (cached)"
        print(f"  [{label}]  {elapsed:.3f}s  —  {query[:45]}")
    speedup = times[0] / times[1] if times[1] > 0 else float("inf")
    print(f"  Speedup: {speedup:.1f}x\n")
    embedding_times[query] = times

# --- LLM Cache Test ---
# The LLM cache (InMemoryCache) stores full completion results keyed
# on prompt + model. An identical prompt on the second call returns
# instantly from memory without an API round-trip.

print("=" * 55)
print("LLM CACHE TEST")
print("=" * 55)

llm_test_queries = [
    "What are common signs of illness in cats?",
    "How often should cats visit the vet?",
]

llm_times = {}

for query in llm_test_queries:
    times = []
    for i in range(3):  # 3 calls: 1 miss + 2 hits
        start = time.time()
        retrieve_information.invoke(query)
        elapsed = time.time() - start
        times.append(elapsed)
        label = "MISS (cold)" if i == 0 else f"HIT  (call {i+1})"
        print(f"  [{label}]  {elapsed:.3f}s  —  {query[:45]}")
    speedup = times[0] / times[1] if times[1] > 0 else float("inf")
    print(f"  Speedup (call 1 → 2): {speedup:.1f}x\n")
    llm_times[query] = times

# --- Summary ---
print("=" * 55)
print("CACHE HIT RATE SUMMARY")
print("=" * 55)
total_calls = (len(embedding_test_queries) * 2) + (len(llm_test_queries) * 3)
total_hits = len(embedding_test_queries) + (len(llm_test_queries) * 2)
hit_rate = (total_hits / total_calls) * 100
print(f"  Total calls :  {total_calls}")
print(f"  Cache hits  :  {total_hits}")
print(f"  Cache misses:  {total_calls - total_hits}")
print(f"  Hit rate    :  {hit_rate:.1f}%")


# ============================================================
# ACTIVITY 2 — Tool Selection Testing
# Paste into Cell 24
# ============================================================

import time
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.graphs.simple_agent import graph as simple_agent

def run_agent_test(query: str, expected_tool: str) -> None:
    """Run a query through the simple agent and report which tools were used."""
    print(f"\n{'=' * 55}")
    print(f"QUERY       : {query}")
    print(f"EXPECTED    : {expected_tool}")
    print("-" * 55)

    start = time.time()
    response = simple_agent.invoke({"messages": [HumanMessage(content=query)]})
    elapsed = time.time() - start

    # Extract tool calls from message history
    tools_used = []
    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])
        elif isinstance(msg, ToolMessage):
            pass  # tool result, not the call itself

    tools_str = ", ".join(tools_used) if tools_used else "none (direct LLM response)"
    match = "✅" if any(expected_tool.lower() in t.lower() for t in tools_used) else "⚠️ "

    print(f"TOOLS USED  : {tools_str}  {match}")
    print(f"LATENCY     : {elapsed:.2f}s")
    print(f"RESPONSE    :\n{response['messages'][-1].content[:300]}")

# --- Cat health → should use retrieve_information (RAG) ---
run_agent_test(
    query="What vaccinations does an indoor cat need and at what age?",
    expected_tool="retrieve_information"
)

# --- Current events → should use TavilySearch ---
run_agent_test(
    query="What are the latest developments in AI regulation in 2025?",
    expected_tool="TavilySearch"
)

# --- Research question → should use ArxivQueryRun ---
run_agent_test(
    query="Find recent research papers about transformer attention mechanisms",
    expected_tool="arxiv"
)

# --- Multi-step → should use multiple tools ---
run_agent_test(
    query="How does recent AI research in computer vision relate to advances in veterinary diagnostics for cats?",
    expected_tool="retrieve_information + arxiv"
)

print(f"\n{'=' * 55}")
print("TOOL SELECTION SUMMARY")
print("=" * 55)
print("  RAG (retrieve_information) : feline/veterinary domain questions")
print("  TavilySearch               : current events, news, recent facts")
print("  ArxivQueryRun              : academic research and papers")
print("  Multiple tools             : cross-domain or multi-step reasoning")
