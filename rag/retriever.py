from qdrant_client.models import FieldCondition, Filter, MatchValue

from rag.embeddings import OpenAIEmbeddingProvider
from rag.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        vector_store:VectorStore,
        embedding_provider:OpenAIEmbeddingProvider,
    ) :
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None=None,
    ):
        query_embedding = (
            self.embedding_provider
            .embed_query(query)
        )

        query_filter = None

        if document_id:

            query_filter = Filter(
                must = [
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(
                            value=document_id
                        ),
                    )
                ]
            )
        
        results = self.vector_store.client.query_points(
            collection_name = self.vector_store.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload = True,
        )

        return results.points

    def build_context(self, results) -> str:
    
        context_parts = []
    
        for index, result in enumerate(results, start=1):
    
            payload = result.payload
    
            context_parts.append(
                f"""
                SOURCE {index}
                File: {payload["file_name"]}
                Page: {payload["page_number"]}
                
                {payload["text"]}
                """.strip()
            )
    
        return "\n\n".join(context_parts)