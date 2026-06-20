import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class CompanionBot:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are a warm, caring companion named Aria. 
Someone is talking to you because they feel lonely or are going through something difficult.
Rules:
- Be genuinely empathetic, never robotic or generic
- Remember what they've told you earlier in the conversation
- Keep responses to 2-3 sentences
- If someone seems to be in crisis or mentions self-harm, gently encourage them to reach out to a real person or helpline
- Occasionally suggest a small mood-lifting activity (a walk, music, journaling) when appropriate"""

    def is_crisis(self, message):
        crisis_keywords = [
            "suicide", "kill myself", "end my life", "self harm",
            "hurt myself", "don't want to live", "want to die"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)

    def chat(self, user_message):
        # Safety check first — before anything else
        if self.is_crisis(user_message):
            return (
                "I hear you, and I'm really concerned about what you just shared. "
                "Please reach out to a real person right now — you can contact the "
                "Umang helpline (Pakistan) at 0317-4288665, available 24/7. "
                "You don't have to go through this alone. 💙"
            )

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call LLM with full history
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
        )

        # Get reply
        reply = response.choices[0].message.content

        # Add bot reply to history too
        self.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def run(self):
        print("Aria: Hey, I'm here. What's on your mind? 💙\n")
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["bye", "exit", "quit"]:
                print("Aria: Take care of yourself. I'm always here when you need to talk. 💙")
                break
            response = self.chat(user_input)
            print(f"\nAria: {response}\n")

if __name__ == "__main__":
    bot = CompanionBot()
    bot.run()