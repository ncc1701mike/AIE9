from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
import openai
from typing import List
import os
import numpy as np
import asyncio


class EmbeddingModel:
    def __init__(self, embeddings_model_name: str = "text-embedding-3-large", batch_size: int = 1024):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.async_client = AsyncOpenAI()
        self.client = OpenAI()

        if self.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. Please set it to your OpenAI API key."
            )
        self.embeddings_model_name = embeddings_model_name
        self.batch_size = batch_size

    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        """Synchronous embedding call, with simple batching."""
        batch_size = 128
        all_embeddings: List[List[float]] = []

        for i in range(0, len(list_of_text), batch_size):
            batch = list_of_text[i : i + batch_size]

            resp = self.client.embeddings.create(
                input=batch,
                model=self.embeddings_model_name,
            )

            # resp.data is a list of objects with `.embedding`
            all_embeddings.extend([item.embedding for item in resp.data])

        return all_embeddings

    async def async_get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        """Async wrapper that runs the sync client in a background thread."""
        return await asyncio.to_thread(self.get_embeddings, list_of_text)

    async def async_get_embedding(self, text: str) -> List[float]:
        """Helper for a single text, reusing async_get_embeddings."""
        embeddings = await self.async_get_embeddings([text])
        return embeddings[0]

    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        embedding_response = self.client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )

        return [embeddings.embedding for embeddings in embedding_response.data]

    def get_embedding(self, text: str) -> List[float]:
        embedding = self.client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding


if __name__ == "__main__":
    embedding_model = EmbeddingModel()
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
