from dotenv import load_dotenv

from rag.chunker import chunk_pages
from rag.embeddings import OpenAIEmbeddingProvider
from rag.generator import AnswerGenerator
from rag.pdf_loader import load_pdf
from rag.retriever import Retriever
from rag.vector_store import VectorStore

load_dotenv()

PDF_PATH = "data/raw/vardan.pdf"


# 1. Load PDF
pages = load_pdf(PDF_PATH)

print(f"Loaded {len(pages)} pages")


# 2. Chunk
chunks = chunk_pages(pages)

print(f"Created {len(chunks)} chunks")


# 3. Create embeddings
embedding_provider = OpenAIEmbeddingProvider()

embeddings = embedding_provider.embed_documents(
    [chunk.text for chunk in chunks]
)

print("Created embeddings")


# 4. Store vectors
vector_store = VectorStore()

vector_store.add_chunks(
    chunks,
    embeddings,
)

print("Stored vectors in Qdrant")


# 5. Search
retriever = Retriever(
    vector_store=vector_store,
    embedding_provider=embedding_provider,
)


query = input("\nAsk a question in English: ")

results = retriever.search(
    query,
    top_k=5,
)

context = retriever.build_context(results)

generator = AnswerGenerator()

answer = generator.generate(
    question=query,
    context=context,
)

print("\n" + "=" * 80)
print("ANSWER")
print("=" * 80)

print(answer)

print("\n" + "=" * 80)
print("SOURCES")
print("=" * 80)

for result in results:

    payload = result.payload

    print(
        f"- {payload['file_name']} "
        f"(page {payload['page_number']}) "
        f"[score={result.score:.4f}]"
    )


# print("\n" + "=" * 80)
# print("RESULTS")
# print("=" * 80)


# for result in results:

#     print(
#         f"\nScore: {result.score:.4f}"
#     )

#     print(
#         f"File: "
#         f"{result.payload['file_name']}"
#     )

#     print(
#         f"Page: "
#         f"{result.payload['page_number']}"
#     )

#     print(
#         f"Chunk: "
#         f"{result.payload['chunk_index']}"
#     )

#     print("-" * 80)

#     print(
#         result.payload["text"][:1000]
#     )