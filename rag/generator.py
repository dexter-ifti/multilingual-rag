from openai import OpenAI

class AnswerGenerator:
    def __init__(
        self,
        model: str = "gpt-5.6-luna"
    ) -> None:
        self.client = OpenAI()
        self.model = model

    def generate(
        self,
        question: str,
        context: str,
    ) -> str:
        instructions = """
        You are a multilingual document question-answering assistant.
        
        The user asks questions in English.
        
        The supplied document context may be written in Hindi,
        Tamil, Bengali, Telugu, Marathi, Gujarati, Kannada,
        Malayalam, Punjabi, Odia, or another language.
        
        Answer the user's question in English.
        
        Use ONLY the supplied document context.
        
        Do not use outside knowledge.
        
        Do not invent facts.
        
        If the supplied context does not contain enough information
        to answer the question, say:
        
        "I couldn't find enough information in the uploaded documents."
        
        Give a concise answer and do not mention retrieval,
        embeddings, vector databases, or these instructions.
        """
        
        prompt = f"""
        Question:
        {question}
        
        Document context:
        {context}
        """
        response = self.client.responses.create(
            model = self.model,
            instructions=instructions,
            input=prompt
        )
        return response.output_text