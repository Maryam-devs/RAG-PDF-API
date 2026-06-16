import uuid
import os
import shutil
import json
from datetime import datetime


class LoadPDF:

    def __init__(self):
        self.PDF_DIR = "app/storage/pdfs"
        self.META_DIR = "app/storage/metadata"

    def store_pdf(self, file):
        # Create storage
        self.ensure_dirs()
        # Generate unique id
        doc_id = str(uuid.uuid4())

        # Save PDF
        self.save_pdf(file, doc_id)

        # Save metadata
        metadata = self.save_metadata(doc_id, file.filename)

        return {
            "document_id": doc_id,
            "filename": file.filename
        }

    def ensure_dirs(self):
        os.makedirs(self.PDF_DIR, exist_ok=True)
        os.makedirs(self.META_DIR, exist_ok=True)

    def save_pdf(self, file, doc_id):
        file_path = os.path.join(self.PDF_DIR, f"{doc_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path

    def save_metadata(self, doc_id, filename):
        metadata = {
            "document_id": doc_id,
            "filename": filename,
            "stored_as": f"{doc_id}.pdf",
            "upload_time": datetime.utcnow().isoformat(),
            "status": "uploaded"
        }

        meta_path = os.path.join(self.META_DIR, f"{doc_id}.json")

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return metadata