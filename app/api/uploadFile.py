from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.LoadPDF import LoadPDF
from app.services.DataIngestion import DataIngestion

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
    
    if upload_info.get("duplicate"):
        return {
            "message": "File already exists",
            "document_id": upload_info["document_id"],
            "cached": True
        }

    ingestion = DataIngestion()
    ext_text = ingestion.extract_text(upload_info["doc_path"], upload_info['document_id'])

    return {
        "Extracted Text": ext_text
    }
