from dataclasses import dataclass

from rag.embeddings import OpenAIEmbeddingProvider
from rag.generator import AnswerGenerator
from rag.retriever import Retriever
from rag.vector_store import VectorStore


@dataclass
class Source:
    document_id: str
    file_name: str
    page_number: int
    chunk_index: int
    score: float


@dataclass
class QAResponse:
    answer: str
    sources: list[Source]


class RAGPipeline:

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: OpenAIEmbeddingProvider,
        answer_generator: AnswerGenerator,
    ):
        self.retriever = Retriever(
            vector_store=vector_store,
            embedding_provider=embedding_provider,
        )

        self.answer_generator = answer_generator

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> QAResponse:

        results = self.retriever.search(
            question,
            top_k=top_k,
        )

        if not results:
            return QAResponse(
                answer=(
                    "I couldn't find relevant "
                    "information in the uploaded documents."
                ),
                sources=[],
            )

        context_parts = []

        sources = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            payload = result.payload

            context_parts.append(
                f"""
SOURCE {index}
File: {payload["file_name"]}
Page: {payload["page_number"]}
Chunk: {payload["chunk_index"]}

{payload["text"]}
""".strip()
            )

            sources.append(
                Source(
                    document_id=payload["document_id"],
                    file_name=payload["file_name"],
                    page_number=payload["page_number"],
                    chunk_index=payload["chunk_index"],
                    score=result.score,
                )
            )

        context = "\n\n".join(context_parts)

        answer = self.answer_generator.generate(
            question=question,
            context=context,
        )

        return QAResponse(
            answer=answer,
            sources=sources,
        )
    def deduplicate_sources(
        self,
        sources: list[Source],
    ) -> list[Source]:
    
        seen = set()
        unique = []
    
        for source in sources:
    
            key = (
                source.file_name,
                source.page_number,
            )
    
            if key in seen:
                continue
    
            seen.add(key)
            unique.append(source)
    
        return unique