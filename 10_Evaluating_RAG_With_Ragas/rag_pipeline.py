# -----------------------------------------
# rag_pipeline.py
# -----------------------------------------
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


# Load .env from this project folder (works whether script is run or imported)
PROJECT_DIR = Path(__file__).resolve().parent
ENV_PATH = PROJECT_DIR / ".env"

if load_dotenv is not None and ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=False)

# Fail fast with a clear message instead of hanging later
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Make sure 10_Evaluating_RAG_With_Ragas/.env exists "
        "and contains OPENAI_API_KEY=..., or export it in your shell."
    )


def load_source_documents() -> list:
    data_dir = PROJECT_DIR / "data"

    files = [
        data_dir / "HealthWellnessGuide.txt",
        data_dir / "MentalHealthGuide.txt",
    ]

    optional_files = [
        data_dir / "PsychologyHandbook.txt",
        data_dir / "Psychology Handbook.txt",
        data_dir / "Psychology_Handbook.txt",
    ]

    for fp in optional_files:
        if fp.exists():
            files.append(fp)
            break

    docs = []
    for fp in files:
        if not fp.exists():
            raise FileNotFoundError(f"Missing file: {fp}")
        docs.extend(TextLoader(str(fp), encoding="utf-8").load())

    sources = sorted({d.metadata.get("source") for d in docs if d.metadata.get("source")})
    print("Loaded sources:")
    for s in sources:
        print(" -", s)

    return docs


# Load docs (now includes MentalHealthGuide.txt too)
docs = load_source_documents()

# Split docs
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=30)
split_documents = text_splitter.split_documents(docs)

# Embeddings + vector store
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    request_timeout=60,
    max_retries=2,
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    request_timeout=60,
    max_retries=2,
)

client = QdrantClient(":memory:")
client.create_collection(
    collection_name="use_case_data",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="use_case_data",
    embedding=embeddings,
)

_ = vector_store.add_documents(documents=split_documents)

# Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

RAG_PROMPT = """\
You are a helpful assistant who answers questions based on provided context.
Use only the context. If the answer is not in the context, say you don't know.

Question:
{question}

Context:
{context}
"""

rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)


def format_docs(docs_list):
    return "\n\n".join(d.page_content for d in docs_list)


def rag_answer(question: str, retriever_override=None):
    active_retriever = retriever_override or retriever
    retrieved_docs = active_retriever.invoke(question)
    context_text = format_docs(retrieved_docs)
    messages = rag_prompt.format_messages(question=question, context=context_text)
    response = llm.invoke(messages)
    return {"response": response.content, "context": retrieved_docs}
