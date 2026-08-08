from dotenv import load_dotenv
from openai import OpenAI, responses

load_dotenv()

class Translator:
    def __init__(self, model: str = "gpt-5.6-luna"):
        self.client = OpenAI()
        self.model = model

    def translate_to_english(self, text: str) -> str:
        if not text.strip():
            return ""

        response = self.client.responses.create(
            model = self.model,
            instructions="""
            You are a document translation assistant.
            
            Translate the supplied document text into natural English.
            
            Rules:
            - Preserve the original meaning.
            - Do not summarize.
            - Do not add information.
            - Preserve names of people and places.
            - Preserve paragraph structure where possible.
            - Return only the English translation.
            """,
            input= text,
        )

        return response.output_text