from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

stored_chunks = []
stored_embeddings = None


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "status":"ok"
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    pdf_file = io.BytesIO(content)
    reader = PdfReader(pdf_file)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text: #text += page_text or ""
            text += page_text
    
    def chunk(text, chunk_size):
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i : i + chunk_size ])
        return chunks
    
    chunk_size = 300
    chunks = chunk(text,chunk_size)

    global stored_chunks 
    global stored_embeddings

    stored_chunks = chunks
    stored_embeddings = model.encode(chunks)
    
    print(len(stored_chunks))
    print(len(stored_embeddings))
    

    return {
        "filename":file.filename,
        "size":len(content),
        "preview_file": chunks[:1],
        "total_chunks": len(chunks),
        "first_chunk": chunks[0]
    }

@app.post("/ask")
def question_accept(question: QuestionRequest):

    if not stored_chunks:
        return {"error": "Upload a PDF first"}

    question_embedding = model.encode([question.question])

    scores = cosine_similarity(
        question_embedding,
        stored_embeddings
    )

    best_index = scores.argmax()

    best_chunk = stored_chunks[best_index]

    prompt = f"""
Answer the user's question using the context below.

Context:
{best_chunk}

Question:
{question.question}
"""

    response = gemini.generate_content(prompt)

    return {
        "answer": response.text,
        "context": best_chunk
    }