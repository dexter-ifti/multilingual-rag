from fastapi import APIRouter

from server.schemas import (
    ChatRequest,
    ChatResponse,
    SourceResponse,
)
from server.services.rag_service import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


rag_service = RAGService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    result = rag_service.ask(
        question=request.question,
    )

    return ChatResponse(
        answer=result.answer,
        sources=[
            SourceResponse(
                document_id=source.document_id,
                file_name=source.file_name,
                page_number=source.page_number,
                score=source.score,
            )
            for source in result.sources
        ],
    )