import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from whyhow import WhyHow
import os
import fitz  # PyMuPDF
import logging
from openai import OpenAI
from utils import extract_phrases, extract_topics, get_topic_phrases, generate_questions_gpt3

load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables and clients
WHYHOW_API_KEY = os.getenv('WHYHOW_API_KEY')
OPENAI_API_KEY = 'sk-proj-dOdUoVNk3UKCjJSZ5j3PT3BlbkFJRf2VjqW187CaZWq8EHTi'
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
NEO4J_URL = os.getenv('NEO4J_URL')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

if not all([WHYHOW_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY, NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise Exception("Missing one or more environment variables")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
client = WhyHow(
    api_key=WHYHOW_API_KEY,
    openai_api_key=OPENAI_API_KEY,
    pinecone_api_key=PINECONE_API_KEY,
    neo4j_url=NEO4J_URL,
    neo4j_user=NEO4J_USERNAME,
    neo4j_password=NEO4J_PASSWORD
)

class Query(BaseModel):
    namespace: str
    question: str

class CreateGraphRequest(BaseModel):
    namespace: str
    files: List[str]
    use_raw_text: bool = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), namespace: str = Form(...)):
    try:
        content = await file.read()
        pdf_path = f"./data/{file.filename}"  # Construct the full path
        logger.info(f"Received file {file.filename} with size {len(content)} bytes.")

        with open(pdf_path, 'wb') as f:
            f.write(content)
            logger.info(f"File {file.filename} written to {pdf_path}")

        # Ensure that full file paths are used
        client.graph.add_documents(namespace, [pdf_path])

        return {"filename": file.filename, "namespace": namespace}

    except Exception as e:
        logger.error(f"Failed to upload {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create_graph")
async def create_graph(request: CreateGraphRequest):
    start_time = time.time()
    logger.info("Starting the graph creation process")
    
    try:
        if not request.namespace or not request.files:
            logger.error("Namespace and files are required but not provided.")
            raise HTTPException(status_code=400, detail="Namespace and files are required.")

        combined_text = ""
        full_pdf_paths = []  # List to store full paths of the PDF files
        logger.info(f"Processing files for namespace {request.namespace}: {request.files}")

        for file_name in request.files:
            pdf_path = f"./data/{file_name}"
            logger.info(f"Opening file: {pdf_path}")
            if not os.path.exists(pdf_path):
                logger.error(f"File not found: {pdf_path}")
                raise HTTPException(status_code=404, detail=f"File {file} not found.")
            
            full_pdf_paths.append(pdf_path)  # Add the full path to the list
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                page_text = pdf_document.load_page(page_num).get_text()
                combined_text += page_text
                logger.debug(f"Extracted text from page {page_num} of {file_name}")

        phrases = extract_phrases(combined_text) if not request.use_raw_text else [combined_text]
        lda, vectorizer = extract_topics(phrases)
        topic_phrases = get_topic_phrases(lda, vectorizer)

        logger.info(f"Extracted phrases and topics successfully: {topic_phrases}")

        questions = []
        for topic in topic_phrases:
            questions += generate_questions_gpt3(topic, openai_client)
            logger.info(f"Generated questions for topic: {topic}")

        logger.info("Adding documents to the graph...")
        documents_response = client.graph.add_documents(request.namespace, full_pdf_paths)
        logger.info(f"Documents added successfully: {documents_response}")

        logger.info("Creating graph...")
        extracted_graph = client.graph.create_graph(request.namespace, questions)
        logger.info("Graph created successfully")

        return {
            "important_phrases": topic_phrases,
            "questions": questions,
            "documents_response": documents_response,
            "extracted_graph": extracted_graph
        }

    except HTTPException as http_exc:
        logger.error(f"HTTP error occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_graph(query: Query):
    try:
        response = client.graph.query_graph(
            namespace=query.namespace,
            query=query.question,
            # include_triples=True,
            include_chunks=True
        )

        print(response)

        return {"response": response}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_files")
async def list_files():
    try:
        files = [f for f in os.listdir('./data') if os.path.isfile(os.path.join('./data', f))]
        return {"files": files}
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete_file")
async def delete_file(file_name: str = Form(...)):
    try:
        file_path = os.path.join('./data', file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"File {file_name} deleted successfully"}
        else:
            return {"message": f"File {file_name} does not exist"}
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
