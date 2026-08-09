from fastapi import APIRouter, HTTPException

from rag.page_service import PageService
from rag.translator import Translator


router = APIRouter(
    prefix="/documents",
    tags=["pages"],
)


page_service = PageService()
translator = Translator()


@router.get(
    "/{document_id}/pages/{page_number}"
)
def get_page(
    document_id: str,
    page_number: int,
):

    try:

        text = page_service.get_page_text(
            document_id=document_id,
            page_number=page_number,
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "document_id": document_id,
        "page_number": page_number,
        "text": text,
    }


@router.post(
    "/{document_id}/pages/{page_number}/translate"
)
def translate_page(
    document_id: str,
    page_number: int,
):

    try:

        text = page_service.get_page_text(
            document_id=document_id,
            page_number=page_number,
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    translation = translator.translate_to_english(
        text
    )

    return {
        "document_id": document_id,
        "page_number": page_number,
        "original_text": text,
        "translation": translation,
    }