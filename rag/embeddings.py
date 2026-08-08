from abc import ABC, abstractmethod

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class EmbeddingProvider(ABC):

    @abstractmethod
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        pass

    @abstractmethod
    def embed_query(
        self, 
        query: str,
    ) -> list[float]:
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):

    def __init__(self, model: str = "text-embedding-3-small",):
        self.client = OpenAI()
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model = self.model,
            input = texts
        )

        return [
            item.embedding
            for item in response.data
        ]

    def embed_query(self, query: str) -> list[float]:
        response = self.client.embeddings.create(
            model= self.model,
            input = query
        )

        return response.data[0].embedding