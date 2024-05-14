# utils.py
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from openai import OpenAI

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def generate_questions_gpt3(phrases, openai_client):
    print(phrases)
    messages = [
        {"role": "system", "content": "You are an expert in ontology creation for knowledge graphs. You take a bunch of phrases, and you generate good questions that can act as a seed for generating and populating information in a knowledge graph based on phrases provided."},
        {"role": "user", "content": f"Generate a list of specific, high-quality questions to create seed questions for an ontology for a knowledge graph from the following key phrases: {', '.join(phrases)}"}
    ]
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=250,
        n=1,
        stop=None
    )
    return response.choices[0].message.content.strip().split('\n')

def extract_phrases(text, top_n=3000):

    doc = nlp(text)
    phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    if not phrases:
        return []
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(phrases)
    feature_names = vectorizer.get_feature_names_out()
    scores = np.sum(tfidf_matrix.toarray(), axis=0)
    top_indices = np.argsort(scores)[-top_n:]
    return [feature_names[i] for i in top_indices]

def extract_topics(phrases, n_topics=1):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(phrases)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    return lda, vectorizer

def get_topic_phrases(lda, vectorizer, num_phrases=20):
    topic_phrases = []
    for topic_idx, topic in enumerate(lda.components_):
        topic_phrases.append([vectorizer.get_feature_names_out()[i] for i in topic.argsort()[:-num_phrases - 1:-1]])
    return topic_phrases
