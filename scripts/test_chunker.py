from rag.chunker import chunk_pages
from rag.pdf_loader import load_pdf


PDF_PATH = "data/raw/vardan.pdf"


pages = load_pdf(PDF_PATH)

chunks = chunk_pages(pages)

print(f"Pages:  {len(pages)}")
print(f"Chunks: {len(chunks)}")


for chunk in chunks[:10]:

    print("\n" + "=" * 80)

    print(
        f"File: {chunk.file_name}"
    )

    print(
        f"Page: {chunk.page_number}"
    )

    print(
        f"Chunk: {chunk.chunk_index}"
    )

    print(
        f"Characters: {len(chunk.text)}"
    )

    print("-" * 80)

    print(chunk.text)