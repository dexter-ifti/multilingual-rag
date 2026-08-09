from dotenv import load_dotenv

from rag.embeddings import OpenAIEmbeddingProvider
from rag.generator import AnswerGenerator
from rag.qa import RAGPipeline
from rag.vector_store import VectorStore

load_dotenv()

embedding_provider = OpenAIEmbeddingProvider()

vector_store = VectorStore()

answer_generator = AnswerGenerator()

rag = RAGPipeline(
    vector_store=vector_store,
    embedding_provider=embedding_provider,
    answer_generator=answer_generator,
)


while True:

    question = input("\nQuestion: ").strip()

    if not question:
        continue

    if question.lower() in {"exit", "quit"}:
        break

    result = rag.ask(
        question=question,
        top_k=5,
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(result.answer)

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)
    sources=result.sources
    sources = rag.deduplicate_sources(sources=sources)
    for source in sources:

        print(
            f"- {source.file_name} "
            f"| Page {source.page_number} "
            f"| Chunk {source.chunk_index} "
            f"| Score {source.score:.4f}"
        )