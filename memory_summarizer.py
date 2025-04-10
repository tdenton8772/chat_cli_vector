import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import json

# Ensure required resources are downloaded
nltk.data.path.append("/root/nltk_data")
nltk.download('stopwords', download_dir="/root/nltk_data")
nltk.download('wordnet', download_dir="/root/nltk_data")

# Initialize stemmer, lemmatizer, and stopword set
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    """Cleans and compresses a block of text for simplified storage."""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'#\w+', '', text)  # Remove hashtags

    # Replace emoticons
    emoticons = {':)': 'smile', ':-)': 'smile', ':(': 'sad', ':-(': 'sad'}
    words = text.split()
    words = [emoticons.get(word, word) for word in words]
    text = " ".join(words)

    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)  # Remove single characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

    # Remove stopwords
    words = [word for word in text.split() if word not in STOPWORDS]

    # Stem and lemmatize
    words = [stemmer.stem(word) for word in words]
    words = [lemmatizer.lemmatize(word) for word in words]

    return ' '.join(words)

def summarize_exchange(user_input, assistant_response):
    cleaned_user = clean_text(user_input)
    cleaned_assistant = clean_text(assistant_response)
    return f"User: {cleaned_user}\nAssistant: {cleaned_assistant}"

# Example usage
if __name__ == "__main__":
    user = "Hey, what's the weather like in NYC today?"
    assistant = "Sure! The weather in New York City today is partly cloudy with highs in the 70s."
    summary = summarize_exchange(user, assistant)
    print("Simplified memory entry:", summary)
