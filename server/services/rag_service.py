from rag.embeddings import OpenAIEmbeddingProvider
from rag.generator import AnswerGenerator
from rag.qa import RAGPipeline
from rag.vector_store import VectorStore


class RAGService:

    def __init__(self):

        self.embedding_provider = (
            OpenAIEmbeddingProvider()
        )

        self.vector_store = VectorStore()

        self.answer_generator = (
            AnswerGenerator()
        )

        self.pipeline = RAGPipeline(
            vector_store=self.vector_store,
            embedding_provider=(
                self.embedding_provider
            ),
            answer_generator=(
                self.answer_generator
            ),
        )

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ):

        return self.pipeline.ask(
            question=question,
            top_k=top_k,
        )