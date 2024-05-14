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
import utils  # Import the utility module

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
        pdf_path = f"./data/{file.filename}"

        with open(pdf_path, 'wb') as f:
            f.write(content)

        logger.info(f"Uploaded file: {file.filename}")

        return {"filename": file.filename, "namespace": namespace}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_graph")
async def create_graph(request: CreateGraphRequest):
    start_time = time.time()
    try:
        if not request.namespace or not request.files:
            raise HTTPException(status_code=400, detail="Namespace and files are required.")

        combined_text = ""
        missing_files = []

        for file_name in request.files:
            pdf_path = f"./data/{file_name}"
            if not os.path.exists(pdf_path):
                missing_files.append(file_name)
            else:
                pdf_document = fitz.open(pdf_path)
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    combined_text += page.get_text()

        if missing_files:
            raise HTTPException(status_code=404, detail=f"Not all documents exist: {missing_files}")

        if request.use_raw_text:
            phrases = [combined_text]  # Using raw text as a single document
        else:
            phrases = utils.extract_phrases(combined_text)
        
        lda, vectorizer = utils.extract_topics(phrases)
        topic_phrases = utils.get_topic_phrases(lda, vectorizer)

        questions = []
        for topic in topic_phrases:
            questions.extend(utils.generate_questions_gpt3(topic, openai_client))

        documents_response = client.graph.add_documents(request.namespace, request.files)
        extracted_graph = client.graph.create_graph(request.namespace, questions)

        return {
            "important_phrases": topic_phrases,
            "questions": questions,
            "documents_response": documents_response,
            "extracted_graph": extracted_graph
        }
    except HTTPException as http_exc:
        logger.error(f"HTTP error occurred: {str(http_exc)}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_graph(query: Query):
    try:
        response = client.graph.query_graph(
            namespace=query.namespace,
            query=query.question,
            include_triples=True,
            include_chunks=True
        )

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
