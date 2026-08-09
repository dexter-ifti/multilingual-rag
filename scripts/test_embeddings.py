import math

from rag.embeddings import OpenAIEmbeddingProvider

from dotenv import load_dotenv

load_dotenv()


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    magnitude_a = math.sqrt(
        sum(x * x for x in a)
    )

    magnitude_b = math.sqrt(
        sum(x * x for x in b)
    )

    return dot_product / (
        magnitude_a * magnitude_b
    )


provider = OpenAIEmbeddingProvider()


documents = [
    "किसानों को इस योजना के तहत आर्थिक सहायता प्रदान की जाती है।",
    "भारत में कई प्रकार की फसलें उगाई जाती हैं।",
    "दिल्ली भारत की राजधानी है।",
]

query = "What financial assistance is provided to farmers?"


document_embeddings = provider.embed_documents(documents)

query_embedding = provider.embed_query(query)


results = []

for document, embedding in zip(
    documents,
    document_embeddings,
):
    score = cosine_similarity(
        query_embedding,
        embedding,
    )

    results.append(
        (score, document)
    )


results.sort(reverse=True)


for score, document in results:
    print(f"{score:.4f}  {document}")