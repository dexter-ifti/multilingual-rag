from rag.pdf_loader import load_pdf

PDF_PATH = "data/raw/vardan.pdf"


pages = load_pdf(PDF_PATH)

print(f"Loaded {len(pages)} pages\n")

empty_pages = 0

for page in pages:
    char_count = len(page.text)

    print(
        f"Page {page.page_number:>3}: "
        f"{char_count:>6} characters"
    )

    if char_count == 0:
        empty_pages += 1


print("\n" + "=" * 50)
print(f"Total pages : {len(pages)}")
print(f"Empty pages : {empty_pages}")
print("=" * 50)