from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import chromadb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://super-space-system-r44ggx4ppp77cp954-5500.app.github.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="database")
collection = client.get_or_create_collection(name="pdf_chunks")



class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "status":"ok"
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global collection

    try:
        client.delete_collection("pdf_chunks")
    except:
        pass

    collection = client.get_or_create_collection("pdf_chunks")

    content = await file.read()
    pdf_file = io.BytesIO(content)
    reader = PdfReader(pdf_file)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text: 
            text += page_text
    
    def chunk(text, chunk_size):
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i : i + chunk_size ])
        return chunks
    
    chunk_size = 300
    chunks = chunk(text,chunk_size)

    embeddings = model.encode(chunks)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[f"{file.filename}chunks_{i}"],
            metadatas=[{"pdf": file.filename, "chunk_id": i}]
        )
    print("*****************")
    print("*****************")
    print(collection.count())
    print("*****************")
    print("*****************")

    return {
        "filename":file.filename,
        "size":len(content),
        "preview_file": chunks[:1],
        "total_chunks": len(chunks),
        "first_chunk": chunks[0]
    }

@app.post("/ask")
def question_accept(question: QuestionRequest):

    if collection.count() == 0:
        return {"error": "Upload a pdf first"}
    
    question_embedding = model.encode([question.question])

    results = collection.query(
        query_embeddings=[question_embedding[0]],
        n_results=1
    )

    best_chunk = results["documents"][0][0]

    prompt = f"""
    Answer the user's question using the context below.

    Context:
    {best_chunk}

    Question:
    {question.question}
    """

    response = requests.post(
        "https://super-space-system-r44ggx4ppp77cp954-11434.app.github.dev/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        }
    )


    data = response.json()
    answer = data["response"]


    return {
        "answer": answer,
        "context": best_chunk,
        "question": question.question
    }