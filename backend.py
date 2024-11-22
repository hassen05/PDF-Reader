import logging
import os
from fastapi import FastAPI, HTTPException, UploadFile, File

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        logger.info(f"Uploaded PDF: {file.filename}")
        return {"filename": file.filename}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.1", port=8001)