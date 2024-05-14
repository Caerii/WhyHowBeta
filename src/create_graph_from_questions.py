import time
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase
from whyhow import WhyHow
import os

# Load environment variables from .env file
load_dotenv()


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

client = WhyHow(
    api_key = os.environ.get("WHYHOW_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    neo4j_url=os.getenv("NEO4J_URL"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
)

def main():
    try:
        print(f"{current_time()} - Starting the WhyHow client initialization...")

        # namespace = "scientific-research-bruh" # define Namespace
        namespace = "Instance01"

        """
        Adding documents.
        """
        documents = ["../data/paper1.pdf", "../data/paper2.pdf", "../data/test.pdf"]
        documents_response = client.graph.add_documents(namespace, documents)
        print(f"{current_time()} - Documents uploaded. Response: {documents_response}")

        # Waiting before creating graph
        print(f"{current_time()} - Waiting for the graph to stabilize for 35 seconds...")
        time.sleep(35)

        """
        Creating graph using natural language.
        """
        # Creating graph from natural language questions
        questions = ["What is philosophy language?", "What is philosophy of language composed of?"]

        # Try creating graph multiple times
        for attempt in range(3):
            print(f"{current_time()} - Attempt {attempt + 1} to create graph...")
            extracted_graph = client.graph.create_graph(
                namespace = namespace,
                  questions = questions)
            
            if extracted_graph and 'error' not in extracted_graph:
                print(f"{current_time()} - Graph successfully created.")
                break
            print(f"{current_time()} - Waiting before retrying...")
            time.sleep(15)

        print(f"{current_time()} - Graph created from questions. Extracted Graph: {extracted_graph} {type(extracted_graph)}")

        # Waiting before querying
        sleeb_tim = 120
        print(f"{current_time()} - Waiting before querying graph for {sleeb_tim} seconds...")
        time.sleep(sleeb_tim)

        """ Query the graph in natural language. """
        query_questions = ["What does philosophy of language contain?"]
        query_response = client.graph.query_graph(namespace, query_questions[0])
        print(f"{current_time()} - Query Response: {query_response}")

    except Exception as e:
        print(f"{current_time()} - Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
