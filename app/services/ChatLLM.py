from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class ChatLLM:

    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_answer(self, query, context):

        prompt = f"""
You are a helpful assistant.

Use ONLY the context below to answer the question.
If the answer is not in the context, say that its not present in the provided context.

Context:
{context}

Question:
{query}

Answer:
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content