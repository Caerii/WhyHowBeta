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
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),  # Include this if it's needed for your project
    'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY')  # Include this if it's needed for your project
}

# Check if all necessary environment variables are set
missing_vars = [var for var, value in required_env_vars.items() if not value]
if missing_vars:
    raise Exception(f"Missing environment variables: {', '.join(missing_vars)}")

# If all environment variables are present, continue with initialization
print("All required environment variables are set. Continuing with application initialization...")

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

"""
Convert Text files into PDFs START
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def text_to_pdf(text_filename, pdf_filename):
    # Create a canvas to write to PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter  # Get dimensions of the letter size

    # Open text file and read lines
    with open(text_filename, 'r') as file:
        lines = file.readlines()

    # Start writing from the top (1 inch margin)
    y = height - 72
    for line in lines:
        # Draw the line and move to next line position
        c.drawString(72, y, line.strip())
        y -= 15  # Decrease Y coordinate to move to the next line

    c.save()

# Specify directory paths and filenames
base_dir = '../data'
text_files = ['paper1.txt', 'paper2.txt']

# Loop through each text file and convert it to PDF
for text_file in text_files:
    text_path = os.path.join(base_dir, text_file)
    pdf_path = os.path.join(base_dir, text_file.replace('.txt', '.pdf'))
    text_to_pdf(text_path, pdf_path)
    print(f"Converted {text_path} to {pdf_path}")
"""
Convert Text files into PDFs END
"""

def connect_to_neo4j(uri, user, password):
    # Establish a connection to the Neo4j database
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

def main():
    try:
        print(f"{current_time()} - Starting the WhyHow client initialization...")
        start_time = time.time()
        client = WhyHow(
            api_key = os.environ.get("WHYHOW_API_KEY"),
            openai_api_key="sk-proj-dOdUoVNk3UKCjJSZ5j3PT3BlbkFJRf2VjqW187CaZWq8EHTi",
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            neo4j_url=os.getenv("NEO4J_URI"),
            neo4j_user=os.getenv("NEO4J_USERNAME"),
            neo4j_password=os.getenv("NEO4J_PASSWORD"),
        )

        initialization_time = time.time() - start_time
        print(f"{current_time()} - WhyHow client initialized in {initialization_time:.2f} seconds.")

        # Define namespace and specify documents
        namespace = "scientific-research-test"
        documents = [
            "../data/paper1.pdf",
            "../data/paper2.pdf"
        ]

        print(f"{current_time()} - Uploading documents to namespace '{namespace}'...")
        start_time = time.time()
        documents_response = client.graph.add_documents(namespace, documents)
        upload_time = time.time() - start_time
        print(f"{current_time()} - Documents uploaded in {upload_time:.2f} seconds. Response: {documents_response}")

        # Define schema for creating the graph
        schema_file = "schema.json"
        print(f"{current_time()} - Creating graph from schema...")
        start_time = time.time()
        
        extracted_graph = client.graph.create_graph_from_schema(namespace, schema_file)
        graph_creation_time = time.time() - start_time
        print(f"{current_time()} - Graph created in {graph_creation_time:.2f} seconds. Extracted Graph: {extracted_graph}")

        # Wait 15 seconds for the graph to be created
        print(f"{current_time()} - Waiting for 15 seconds for the graph to be created...")
        time.sleep(120)

        # Query the graph
        query = """
        What are the hypotheses in the papers?
        """
        print(f"{current_time()} - Querying the graph...")
        start_time = time.time()
        query_response = client.graph.query_graph(namespace, query)
        query_time = time.time() - start_time
        print(f"{current_time()} - Graph queried in {query_time:.2f} seconds. Query Response: {query_response}")

    except Exception as e:
        print(f"{current_time()} - Error occurred: {str(e)}")


if __name__ == "__main__":
    main()
