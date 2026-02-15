import os
import ast
import json
import asyncio
import pandas as pd
from dotenv import load_dotenv

# Keep macOS + Python 3.12 event loop behavior predictable
if hasattr(asyncio, "set_event_loop_policy"):
    try:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    except Exception:
        pass

load_dotenv()

from ragas import EvaluationDataset, evaluate, RunConfig
from ragas.metrics import (
    LLMContextRecall,
    Faithfulness,
    FactualCorrectness,
    ResponseRelevancy,
    ContextEntityRecall,
    NoiseSensitivity,
)

from langchain_openai import ChatOpenAI

def parse_list(v):
    if isinstance(v, list):
        return v
    if pd.isna(v):
        return []
    try:
        out = ast.literal_eval(v)
        return out if isinstance(out, list) else []
    except Exception:
        return []

def main():
    input_csv = os.getenv("EVAL_READY_CSV", "eval_ready.csv")
    df = pd.read_csv(input_csv)

    # Ensure expected columns exist
    required = ["user_input", "response", "retrieved_contexts", "reference", "reference_contexts"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing columns in {input_csv}: {missing}")

    # Fix types
    df["user_input"] = df["user_input"].fillna("").astype(str)
    df["response"] = df["response"].fillna("").astype(str)
    df["reference"] = df["reference"].fillna("").astype(str)
    df["retrieved_contexts"] = df["retrieved_contexts"].apply(parse_list)
    df["reference_contexts"] = df["reference_contexts"].apply(parse_list)

    evaluation_dataset = EvaluationDataset.from_pandas(df)

    evaluator_llm = ChatOpenAI(
        model=os.getenv("OPENAI_EVAL_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
        temperature=0,
        timeout=120,
        max_retries=2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    run_config = RunConfig(timeout=360, max_retries=1, max_wait=10, max_workers=1)

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
        run_config=run_config,
    )

    scores = result.to_pandas().mean(numeric_only=True).to_dict()
    print(scores)

    with open("baseline_result.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

    print("wrote baseline_result.json")

if __name__ == "__main__":
    main()
