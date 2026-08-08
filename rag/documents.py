import uuid


def create_document_id() -> str:
    return str(uuid.uuid4())