"""
Text Preprocessing Utility
Provides helper functions to clean and normalize text extracted from resumes and job descriptions.
"""

import re
import string

# Basic English stopwords list to eliminate common words without external NLTK dependencies
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
])


def clean_text(text: str) -> str:
    """
    Cleans raw text by converting to lowercase, removing special characters/urls,
    and removing excessive whitespace.
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lower case
    text = text.lower()

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove email addresses from raw text matching to avoid noise in vectorization
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

    # Replace punctuation with spaces (preserving alphanumeric characters)
    text = re.sub(r'[^a-zA-Z0-9+#\s]', ' ', text)

    # Normalize multiple whitespace characters
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def remove_stopwords(text: str) -> str:
    """
    Removes common stop words from a pre-cleaned string.
    """
    cleaned = clean_text(text)
    words = cleaned.split()
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return ' '.join(filtered_words)
