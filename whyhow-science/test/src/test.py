import time
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase
from whyhow import WhyHow
import os

# Load environment variables from .env file
load_dotenv()

# Environment variables list
required_env_vars = {
    'WHYHOW_API_KEY': os.getenv('WHYHOW_API_KEY'),
    'NEO4J_URL': os.getenv('NEO4J_URL'),
    'NEO4J_USER': os.getenv('NEO4J_USER'),
    'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY')
}

# Check if all necessary environment variables are set
missing_vars = [var for var, value in required_env_vars.items() if not value]
if missing_vars:
    raise Exception(f"Missing environment variables: {', '.join(missing_vars)}")

print("All required environment variables are set. Continuing with application initialization...")

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def main():
    try:
        print(f"{current_time()} - Starting the WhyHow client initialization...")
        client = WhyHow(
            api_key = os.environ.get("WHYHOW_API_KEY"),
            openai_api_key="sk-proj-dOdUoVNk3UKCjJSZ5j3PT3BlbkFJRf2VjqW187CaZWq8EHTi",
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            neo4j_url=os.getenv("NEO4J_URI"),
            neo4j_user=os.getenv("NEO4J_USERNAME"),
            neo4j_password=os.getenv("NEO4J_PASSWORD"),
        )

        # namespace = "scientific-research-bruh" # define Namespace
        namespace = "Test01"

        """
        Adding documents.
        """
        documents = ["../data/paper1.pdf", "../data/paper2.pdf", "../data/test.pdf"]
        documents_response = client.graph.add_documents(namespace, documents)
        print(f"{current_time()} - Documents uploaded. Response: {documents_response}")

        # Waiting before creating graph
        print(f"{current_time()} - Waiting for the graph to stabilize for 25 seconds...")
        time.sleep(15)

        """
        Creating graph using natural language.
        """
        # Creating graph from natural language questions
        questions = ["What is philosophy of language?", "What does philosophy of language contain?"]

        extracted_graph = client.graph.create_graph(namespace, questions)

        print(f"{current_time()} - Graph created from questions. Extracted Graph: {extracted_graph} {type(extracted_graph)}")

        # Waiting before querying
        sleeb_tim = 120
        print(f"{current_time()} - Waiting before querying graph for {sleeb_tim} seconds...")
        time.sleep(sleeb_tim)

        # Query the graph
        query_response = client.graph.query_graph(namespace, "What important concepts are in philosophy of language?")
        print(f"{current_time()} - Query Response: {query_response}")

    except Exception as e:
        print(f"{current_time()} - Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
