from rag.page_service import PageService
from rag.translator import Translator

page_service = PageService()

translator = Translator()


file_name = "vardan.pdf"
page_number = 35


text = page_service.get_page_text(
    file_name=file_name,
    page_number=page_number,
)


print("=" * 80)
print("ORIGINAL")
print("=" * 80)

print(text)


translation = translator.translate_to_english(
    text
)


print("\n" + "=" * 80)
print("ENGLISH TRANSLATION")
print("=" * 80)

print(translation)