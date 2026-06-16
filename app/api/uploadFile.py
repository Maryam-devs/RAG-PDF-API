from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.LoadPDF import LoadPDF

router = APIRouter()

@router.post("/upload_file")
def upload_file(file: UploadFile = File(...)):

    # Check if user uploaded a different format file
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Generate id and save file
    load_pdf = LoadPDF()
    upload_info = load_pdf.store_pdf(file)

    return {
        "message": upload_info,
    }
