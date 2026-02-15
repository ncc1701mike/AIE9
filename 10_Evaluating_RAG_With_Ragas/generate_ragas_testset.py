import os
import asyncio

# Force standard asyncio policy on macOS
if hasattr(asyncio, "set_event_loop_policy"):
    try:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI

from ragas.testset import TestsetGenerator
from ragas.run_config import RunConfig
from ragas.embeddings import OpenAIEmbeddings as RagasOpenAIEmbeddings

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader


def main():
    run_config = RunConfig(timeout=120, max_retries=2, max_wait=10, max_workers=1)

    # Load docs
    docs = []
    for p in ["data/MentalHealthGuide.txt", "data/HealthWellnessGuide.txt"]:
        docs.extend(TextLoader(p).load())

    # LLM (force clean JSON output for Pydantic parsing)
    generator_llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        timeout=60,
        max_retries=2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    # Ragas-native embeddings (async, has embed_text / embed_texts)
    # Ragas v0.4 expects native clients instead of LangChain embeddings wrappers.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in your environment.")

    openai_client = AsyncOpenAI(api_key=api_key)

    generator_embeddings = RagasOpenAIEmbeddings(
        client=openai_client,
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)

    dataset = generator.generate_with_langchain_docs(
        docs,
        testset_size=30,
        run_config=run_config,
        raise_exceptions=True,
        with_debugging_logs=True,
    )

    df = dataset.to_pandas()
    df.to_csv("ragas_testset.csv", index=False)
    print("wrote ragas_testset.csv rows:", len(df))


if __name__ == "__main__":
    main()


# import os
# import asyncio

# # Force standard asyncio policy on macOS
# if hasattr(asyncio, "set_event_loop_policy"):
#     try:
#         asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
#     except Exception:
#         pass

# from dotenv import load_dotenv
# load_dotenv()

# import openai

# from ragas.testset import TestsetGenerator
# from ragas.run_config import RunConfig
# from ragas.embeddings import OpenAIEmbeddings as RagasOpenAIEmbeddings

# from langchain_openai import ChatOpenAI
# from langchain_community.document_loaders import TextLoader


# def main():
#     run_config = RunConfig(timeout=120, max_retries=2, max_wait=10, max_workers=1)

#     # Load docs
#     docs = []
#     for p in ["data/MentalHealthGuide.txt", "data/HealthWellnessGuide.txt"]:
#         docs.extend(TextLoader(p).load())

#     # LLM (JSON-only output to satisfy Ragas Pydantic parsing)
#     generator_llm = ChatOpenAI(
#         model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
#         temperature=0,
#         timeout=60,
#         max_retries=2,
#         model_kwargs={"response_format": {"type": "json_object"}},
#     )

#     # Embeddings (Ragas wrapper, provides embed_text / embed_texts)
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         raise RuntimeError("OPENAI_API_KEY is not set in environment or .env")

#     openai_client = openai.OpenAI(api_key=api_key)

#     generator_embeddings = RagasOpenAIEmbeddings(
#         client=openai_client,
#         model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
#     )

#     generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)

#     dataset = generator.generate_with_langchain_docs(
#         docs,
#         testset_size=10,
#         run_config=run_config,
#         raise_exceptions=True,
#         with_debugging_logs=True,
#     )

#     df = dataset.to_pandas()
#     df.to_csv("ragas_testset.csv", index=False)
#     print("wrote ragas_testset.csv rows:", len(df))


# if __name__ == "__main__":
#     main()
