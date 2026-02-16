import ast
import json
import os

import pandas as pd
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.metrics import (
    ContextEntityRecall,
    Faithfulness,
    FactualCorrectness,
    LLMContextRecall,
    NoiseSensitivity,
    ResponseRelevancy,
)

from rag_pipeline import rag_answer, vector_store


OUT_CSV = "ragas_testset_with_mmr_outputs.csv"
RESULT_JSON = "mmr_result.json"

FORCE_REGEN = True

MMR_K = 5
MMR_FETCH_K = 30
MMR_LAMBDA = 0.3

EVAL_TIMEOUT = 360


def to_list(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                return ast.literal_eval(s)
            except Exception:
                try:
                    return json.loads(s)
                except Exception:
                    return []
        try:
            return json.loads(s)
        except Exception:
            return []
    return []


def evaluation_result_to_dict(result):
    if hasattr(result, "to_pandas"):
        try:
            df_scores = result.to_pandas()
            numeric_cols = df_scores.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                return {c: float(df_scores[c].mean()) for c in numeric_cols}
        except Exception:
            pass

    if isinstance(result, dict):
        out = {}
        for k, v in result.items():
            try:
                out[k] = float(v)
            except Exception:
                out[k] = str(v)
        return out

    try:
        d = dict(result)
        out = {}
        for k, v in d.items():
            try:
                out[k] = float(v)
            except Exception:
                out[k] = str(v)
        return out
    except Exception:
        return {"result_str": str(result)}


def main():
    df = pd.read_csv("ragas_testset.csv")

    if "reference_contexts" in df.columns:
        df["reference_contexts"] = df["reference_contexts"].apply(to_list)

    if "response" not in df.columns:
        df["response"] = ""
    if "retrieved_contexts" not in df.columns:
        df["retrieved_contexts"] = [[] for _ in range(len(df))]

    if FORCE_REGEN:
        df["response"] = ""
        df["retrieved_contexts"] = [[] for _ in range(len(df))]
        print("FORCE_REGEN=True, regenerating outputs and contexts")
    else:
        try:
            df_existing = pd.read_csv(OUT_CSV)
            for col in ["response", "retrieved_contexts"]:
                if col in df_existing.columns:
                    df[col] = df_existing[col]
            print("resuming from:", OUT_CSV)
        except Exception:
            print("starting fresh:", OUT_CSV)

    mmr_retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": MMR_K,
            "fetch_k": MMR_FETCH_K,
            "lambda_mult": MMR_LAMBDA,
        },
    )

    debug_q = str(df.loc[0, "user_input"])
    debug_docs = mmr_retriever.invoke(debug_q)

    print("MMR debug query:", debug_q)
    print("MMR debug docs:", len(debug_docs))
    for i, d in enumerate(debug_docs[:MMR_K], start=1):
        txt = (d.page_content or "").strip().replace("\n", " ")
        print(f"doc {i} chars:", len(txt))
        print("source:", d.metadata.get("source"))
        print("preview:", txt[:220])
        print()

    need = df["response"].isna() | (df["response"].astype(str).str.strip() == "")
    need_idxs = df[need].index.tolist()

    print("rows needing generation:", len(need_idxs), "out of", len(df))

    for j, i in enumerate(need_idxs, start=1):
        q = str(df.at[i, "user_input"])
        print(f"generating {j}/{len(need_idxs)}")
        out = rag_answer(q, retriever_override=mmr_retriever)
        df.at[i, "response"] = out["response"]
        df.at[i, "retrieved_contexts"] = [d.page_content for d in out["context"]]
        df.to_csv(OUT_CSV, index=False)

    df.to_csv(OUT_CSV, index=False)
    print("wrote", OUT_CSV, "with columns:", list(df.columns))

    for col in ["retrieved_contexts", "reference_contexts"]:
        if col in df.columns:
            df[col] = df[col].apply(to_list)

    for col in ["user_input", "response", "reference"]:
        if col in df.columns:
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
    print("evaluation_dataset size:", len(evaluation_dataset))

    evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    run_config = RunConfig(timeout=EVAL_TIMEOUT)

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
        show_progress=True,
        raise_exceptions=True,
        batch_size=1,
    )

    print(result)

    result_dict = evaluation_result_to_dict(result)
    with open(RESULT_JSON, "w") as f:
        json.dump(result_dict, f, indent=2)

    print("wrote", RESULT_JSON)


if __name__ == "__main__":
    main()
