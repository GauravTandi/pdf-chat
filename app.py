from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io
app = FastAPI()

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
    
    return {
        "filename":file.filename,
        "size":len(content),
        "preview_file": chunks[:1],
        "total_chunks": len(chunks),
        "first_chunk": chunks[0]
    }