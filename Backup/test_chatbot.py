import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Enables python to look up the parent folder
from Backup.chatbot import Chatbot

def main():
    # initializes chatbot
    bot = Chatbot(knowledge_base_file="knowledge_base.json", confidence_threshold = 0.2)
    bot_name = input("What's my name at this phase? :")

    print(f"{bot_name} Test (Type 'exit' to quit)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["Exit", "Quit"]:
            print("-" * 40, "\n", " Exiting Test...........", "-" * 40)
            break

        response = bot.get_response(user_input)
        print(f"{bot_name}: ", response)


if __name__ == "__main__":
    main()
