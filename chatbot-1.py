def get_response(user_input):
    user_input = user_input.lower().strip()

    responses = {
        "hello": "Hey! How can I help you?",
        "hi": "Hey! How can I help you?",
        "how are you": "I'm just a bot, but I'm doing great!",
        "bye": "Goodbye! See you later.",
    }

    for keyword, response in responses.items():
        if keyword in user_input:
            return response

    return "Sorry, I didn't understand that."


def main():
    print("Chatbot is running. Type 'bye' to exit.\n")
    while True:
        user_input = input("You: ")
        if "bye" in user_input.lower():
            print("Bot: Goodbye!")
            break
        response = get_response(user_input)
        print(f"Bot: {response}\n")


main()