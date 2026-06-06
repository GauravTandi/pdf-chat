from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def home():
    return {
        "status":"ok"
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    return {
        "filename":file.filename,
        "size":len(content)
    }