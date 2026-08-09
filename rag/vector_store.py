import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag.models import DocumentChunk


class VectorStore:

    def __init__(
        self,
        collection_name: str = 'Documents',
        vector_size: int = 1536
    ) :
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=os.environ["QDRANT_URL"],
            api_key=os.environ["QDRANT_API_KEY"],
            cloud_inference=True,
            timeout=120
        )

        collections = self.client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name = collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )

    def add_chunks(
        self,
        chunks:list[DocumentChunk],
        embeddings:  list[list[float]],
        batch_size: int = 20,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match "
                "number of embeddings"
            )

        points = []

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):
            points.append(
                PointStruct(
                    id=chunk.chunk_id,
                    vector=embedding,
                    payload={
                        "document_id": chunk.document_id,
                        "text": chunk.text,
                        "file_name": chunk.file_name,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "language": chunk.language,
                    },
                )
            )
        for start in range(0, len(points), batch_size):
            batch = points[start:start+batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points = batch,
            )
            print(
                f"Uploaded "
                f"{min(start + batch_size, len(points))}"
                f"/{len(points)}"
            )