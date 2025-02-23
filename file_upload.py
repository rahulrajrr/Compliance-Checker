# importing required libraries
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import aiofiles
import uvicorn

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

CHUNK_SIZE = 10 * 1024 * 1024


def validate_file_type(file: UploadFile):
    """Validates if the uploaded file is a PDF or Word document."""
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and Word files are allowed.",
        )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles file upload, validates the file type, and saves it in chunks."""
    validate_file_type(file)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                await buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return JSONResponse(
        content={"filename": file.filename, "message": "File uploaded successfully."}
    )


if __name__ == "__main__":
    uvicorn.run("file_upload:app", host="127.0.0.1", port=8000, reload=True)
