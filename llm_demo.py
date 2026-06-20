import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat(user_message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a warm, empathetic companion. Someone is talking to you because they feel lonely or are going through something difficult. Be genuinely caring, never robotic. Keep responses concise — 2-3 sentences max."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    return response.choices[0].message.content

# Test it
user_input = "I feel so lonely n i've no one to talk to"
print("User:", user_input)
print("Bot:", chat(user_input))