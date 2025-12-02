import random
import nltk
import string
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet



# Ensure neccessary NLTK data is downloaded 
nltk.download ('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def preprocess_text(text):
    """
    Tokenizes, lowercases, removes punctuation, and lemmatizes input text.add
    Returns a list of clean tokens. 
    """
    # initializes lemmatizer 
    lemmatizer = WordNetLemmatizer()

    # Step 1: Tokenize 
    tokens = nltk.word_tokenize(text)

    # Step 2: Lowercase
    tokens = [token.lower() for token in tokens]

    # Step 3: Remove Punctuation
    tokens = [token for token in tokens if token not in string.punctuation]

    # Step 4: POS (Part of speech) tagging 
    pos_tags = nltk.pos_tag(tokens)

    # Steps 5: Lemmatize based on POS
    def get_wordnet_pos(tag):
        """
        Convert POS tag to format recognized by WordNetLemmatizer
        """
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN    # default

    lemmatized_tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

    return lemmatized_tokens


def playful_responses():
    """
    Generates Random playful resposes to unknown user questions.
    """
    replies = [
        "Hmmn, I would get back to you. I'm phoning NASA for that....",
        "Hmm, that question's in a different galaxy. Try asking me about blackholes",
        "Even my cosmic database doesn't have an answer to that one. Ask me about blackholes instead!",
        "That's beyond my event horizon. How about something closer to home, like Mars?",
        "My circuits are drawing a blank on that one. Maybe try rephrasing?", 
        "I'm still learning! Could you ask me about something space-related instead?", 
        "Error  404: Space knowledge not found. Try asking about rockets or Astronauts?", 
        "The cosmos hasn't revealed that secret to me yet. What else wonders you?", 
        "Some mysteries remain within the stars. Perhaps ask about known celestial bodies instead?",
        "That knowledge is still orbiting in uncharted space. Try a different question!",
        "That's outside my current knowledge base. Want to try a space-related question instead?"
    ]

    return random.choice(replies)
