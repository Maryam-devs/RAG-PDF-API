from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/upload_file")
def upload_file(file: UploadFile = File(...)):

    contents = file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
