"""
generate_golden_dataset.py
--------------------------

    python generate_golden_dataset.py

This script generates a golden evaluation dataset from the Health & Wellness Guide
using Ragas TestsetGenerator, then saves the result to golden_dataset.json
in the same directory. The notebook cells read from that JSON file so
Ragas never needs to run inside the notebook.

Requirements:
    pip install ragas langchain-openai langchain-community python-dotenv
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import json
import asyncio

# ── Load .env ─────────────────────────────────────────────────────────────────
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv(usecwd=True)

if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"  Loaded .env from: {dotenv_path}")
else:
    print("  WARNING: No .env file found. Falling back to exported environment variables.")

# ── Verify API key ────────────────────────────────────────────────────────────
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY not found.\n"
        f"Script was run from: {os.getcwd()}\n"
        "Either add it to a .env file in this directory or run:\n"
        "  export OPENAI_API_KEY='sk-...'"
    )
print(f"  API key found: ...{api_key[-4:]}")


# ── LangChain document loader ─────────────────────────────────────────────────
from langchain_community.document_loaders import TextLoader

# ── Ragas native OpenAI integration (replaces deprecated LangchainLLMWrapper) ─
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory
from openai import OpenAI
from ragas.testset import TestsetGenerator


# ── 1. Load the source document ───────────────────────────────────────────────
print("\nLoading source document...")

loader   = TextLoader("data/HealthWellnessGuide.txt")
raw_docs = loader.load()

if not raw_docs:
    raise ValueError("TextLoader returned no documents. Check the file path.")

print(f"  Loaded {len(raw_docs)} document(s).")
print(f"  Document length: {len(raw_docs[0].page_content)} characters.")

# ── 2. Initialise Ragas-native LLM and embeddings ────────────────────────────
print("\nInitialising models...")

openai_client = OpenAI(api_key=api_key)
ragas_llm = llm_factory(
    model="gpt-4o-mini",
    client=openai_client,
)
# llm_factory returns a Ragas-internal LLM object — no LangChain wrapper needed
ragas_embeddings = embedding_factory(
    model="text-embedding-3-small",
    client=openai_client,
)
# embedding_factory returns a Ragas-internal embeddings object

print("  Testing OpenAI connectivity...")
try:
    test = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Reply with the single word: ok"}],
        max_tokens=5,
    )
    print(f"  LLM test response: '{test.choices[0].message.content.strip()}'")
except Exception as e:
    raise ConnectionError(
        f"OpenAI API call failed: {e}\n"
        "Check your API key, credit balance, and network connection."
    )


# ── 3. Build the TestsetGenerator ─────────────────────────────────────────────
print("\nBuilding TestsetGenerator...")

generator = TestsetGenerator(
    llm=ragas_llm,
    embedding_model=ragas_embeddings,
)


# ── 4. Generate the golden dataset inside a managed event loop ────────────────
print("\nGenerating golden dataset (this may take several minutes)...")

async def run_generation():
     return generator.generate_with_langchain_docs(
        raw_docs,
        testset_size=20,
    )

testset = asyncio.run(run_generation())
# ── 5. Validate the result ────────────────────────────────────────────────────
golden_df = testset.to_pandas()

print(f"  Testset shape: {golden_df.shape}")
print(f"  Columns returned: {list(golden_df.columns)}")

if golden_df.empty:
    raise RuntimeError(
        "Ragas returned an empty testset.\n"
        "Check the output above for any warnings or skipped synthesizers."
    )

# ── 6. Resolve column names across Ragas versions ────────────────────────────
col_map = {}
for candidate in ["user_input", "question"]:
    if candidate in golden_df.columns:
        col_map["user_input"] = candidate
        break

for candidate in ["reference", "answer", "ground_truth"]:
    if candidate in golden_df.columns:
        col_map["reference"] = candidate
        break

if len(col_map) < 2:
    raise KeyError(
        f"Could not find expected columns. "
        f"Available columns: {list(golden_df.columns)}"
    )

print(f"  Using columns: '{col_map['user_input']}' and '{col_map['reference']}'")

# ── 7. Save to JSON ───────────────────────────────────────────────────────────
print("\nSaving to golden_dataset.json...")

golden_records = (
    golden_df[[col_map["user_input"], col_map["reference"]]]
    .rename(columns={
        col_map["user_input"]: "user_input",
        col_map["reference"]:  "reference",
    })
    .to_dict(orient="records")
)

output_path = "golden_dataset.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(golden_records, f, indent=2, ensure_ascii=False)

print(f"  Saved {len(golden_records)} records to '{output_path}'")
print(f"\n  First record preview:")
print(f"    Q: {golden_records[0]['user_input']}")
print(f"    A: {golden_records[0]['reference'][:120]}...")

print("\nDone. You can now run the notebook cells.")
