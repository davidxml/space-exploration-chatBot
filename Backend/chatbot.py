import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from knowledge_base  import load_knowledge_base
from utils import preprocess_text, playful_responses

class Chatbot:
    def __init__(self, knowledge_base_path: str, confidence_threshold: float = 0.2):
        """
        Initialise the chatbot:
        - Load the knowledge base 
        - Preprocess all questions
        - Build TF-IDF matrix for  similarity search
        - Set a configurable confidence threshold
        """

        self.knowledge_base = load_knowledge_base(knowledge_base_path)
        self.confidence_threshold = confidence_threshold

        # Separate questions and answers 
        self.questions = [item["question"] for item in self.knowledge_base]
        self.answers =  [item["answer"] for item in self.knowledge_base]


        # Build TF_IDF vectorizer
        self.vectorizer = TfidfVectorizer(tokenizer= preprocess_text)
        self.question_vectors = self.vectorizer.fit_transform(self.processed_questions)

    def get_response(self, user_input: str) -> str:
        """
        Process user input, compare it with knowledge base
        and returns the most relevant answer.
        """

        if not user_input.strip():
            return playful_responses()
       
        processed_input = preprocess_text(user_input)
        input_vector = self.vectorizer.transform([processed_input])

        # Compute Similarity
        similarities = cosine_similarity(input_vector, self.question_vectors)
        best_match_index = similarities.argmax()
        best_score = similarities[0][best_match_index]

        # Apply configurable confidence threshold
        if best_score < self.confidence_threshold:
            return playful_responses()
        return self.answers[best_match_index]

if __name__ == "__main__":  
    #Simple REPL for testing
    bot = Chatbot("Data", confidence_threshold = 0.25)
    bot_name = input("What's my name at this development stage? :")
    print(f"{bot_name}: Space Exploration ChatBot  --> type 'quit' to exit" )
    while True:
        user_input = input("You:  ")
        if user_input.lower() in ["quit", "exit", "bye", "alright, thank you"]:
            print(f"{bot_name}: Yeah, i'd be in space waiting....")
            break
        response = bot.get_response(user_input)
        print(f"{bot_name}:", response)