class SimpleChatbot:
    def __init__(self):
        self.responses = {
            "hello": "Hey! How can I help you?",
            "hi": "Hey! How can I help you?",
            "how are you": "I'm just a bot, but I'm doing great!",
            "bye": "Goodbye! See you later.",
        }

    def get_response(self, user_input):
        user_input = user_input.lower().strip()

        for keyword, response in self.responses.items():
            if keyword in user_input:
                return response

        return "Sorry, I didn't understand that."

    def run(self):
        print("Chatbot is running. Type 'bye' to exit.\n")
        while True:
            user_input = input("You: ")
            if "bye" in user_input.lower():
                print("Bot: Goodbye!")
                break
            response = self.get_response(user_input)
            print(f"Bot: {response}\n")


if __name__ == "__main__":
    bot = SimpleChatbot()
    bot.run()