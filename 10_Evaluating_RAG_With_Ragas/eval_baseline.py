import ast
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.metrics import (
    LLMContextRecall,
    Faithfulness,
    FactualCorrectness,
    ResponseRelevancy,
    ContextEntityRecall,
    NoiseSensitivity,
)

from langchain_openai import ChatOpenAI

from rag_pipeline import rag_answer


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=False)

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Ensure .env exists in this folder and contains OPENAI_API_KEY=..."
    )


def to_list(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return []
        try:
            return json.loads(s)
        except Exception:
            pass
        try:
            return ast.literal_eval(s)
        except Exception:
            return []
    return []


df = pd.read_csv("ragas_testset.csv")

if "reference_contexts" in df.columns:
    df["reference_contexts"] = df["reference_contexts"].apply(to_list)

if "reference" not in df.columns:
    df["reference"] = ""

if "response" not in df.columns:
    df["response"] = ""

if "retrieved_contexts" not in df.columns:
    df["retrieved_contexts"] = [[] for _ in range(len(df))]

import os
import json
import pandas as pd
from pathlib import Path

# If you have python-dotenv installed, also load .env here to be safe
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

PROJECT_DIR = Path(__file__).resolve().parent
ENV_PATH = PROJECT_DIR / ".env"
if load_dotenv is not None and ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=False)

# Import rag_answer from rag_pipeline
from rag_pipeline import rag_answer

INPUT_CSV = "ragas_testset.csv"
OUTPUT_CSV = "ragas_testset_with_baseline_outputs.csv"

def json_to_list(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        try:
            return json.loads(v)
        except Exception:
            return []
    return []

# Load either the existing outputs file (resume) or the original testset
if Path(OUTPUT_CSV).exists():
    df = pd.read_csv(OUTPUT_CSV)
    print("resuming from:", OUTPUT_CSV)
else:
    df = pd.read_csv(INPUT_CSV)
    print("starting from:", INPUT_CSV)

# Normalize columns
if "reference_contexts" in df.columns:
    df["reference_contexts"] = df["reference_contexts"].apply(json_to_list)

if "response" not in df.columns:
    df["response"] = ""

if "retrieved_contexts" not in df.columns:
    df["retrieved_contexts"] = [[] for _ in range(len(df))]

# Ensure retrieved_contexts is a list
df["retrieved_contexts"] = df["retrieved_contexts"].apply(json_to_list)

# Only run the LLM for rows that are missing outputs
def needs_generation(row):
    resp = str(row.get("response", "")).strip()
    ctxs = row.get("retrieved_contexts", [])
    return (resp == "") or (not isinstance(ctxs, list)) or (len(ctxs) == 0)

todo_idx = [i for i, r in df.iterrows() if needs_generation(r)]
print("rows needing generation:", len(todo_idx), "out of", len(df))

for n, i in enumerate(todo_idx, start=1):
    q = str(df.at[i, "user_input"])
    print(f"generating {n}/{len(todo_idx)}")
    out = rag_answer(q)
    df.at[i, "response"] = out["response"]
    df.at[i, "retrieved_contexts"] = [d.page_content for d in out["context"]]

df.to_csv(OUTPUT_CSV, index=False)
print("wrote", OUTPUT_CSV, "with columns:", list(df.columns))

df.to_csv("ragas_testset_with_baseline_outputs.csv", index=False)
print("wrote ragas_testset_with_baseline_outputs.csv with columns:", list(df.columns))


df["retrieved_contexts"] = df["retrieved_contexts"].apply(to_list)
df["reference_contexts"] = df["reference_contexts"].apply(to_list)

for col in ["user_input", "response", "reference"]:
    df[col] = df[col].fillna("").astype(str)


df_valid = df[
    (df["user_input"].str.strip() != "")
    & (df["response"].str.strip() != "")
    & (df["reference"].str.strip() != "")
    & (df["retrieved_contexts"].apply(lambda x: isinstance(x, list) and len(x) > 0))
    & (df["reference_contexts"].apply(lambda x: isinstance(x, list) and len(x) > 0))
].copy()

print("rows total:", len(df))
print("rows valid for full metrics:", len(df_valid))

df_valid = df_valid.head(5)

evaluation_dataset = EvaluationDataset.from_pandas(df_valid)
print("evaluation_dataset features:", evaluation_dataset.features())
print("evaluation_dataset size:", len(evaluation_dataset))


evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

custom_run_config = RunConfig(timeout=360)

result = evaluate(
    dataset=evaluation_dataset,
    metrics=[
        LLMContextRecall(),
        Faithfulness(),
        FactualCorrectness(),
        ResponseRelevancy(),
        ContextEntityRecall(),
        NoiseSensitivity(),
    ],
    llm=evaluator_llm,
    run_config=custom_run_config,
    show_progress=True,
    raise_exceptions=True,
    batch_size=1,
)

print(result)
