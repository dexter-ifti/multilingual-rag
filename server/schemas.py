from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    document_id: str
    file_name: str
    page_number: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]