import uuid
import os
import shutil
import json
from datetime import datetime
import hashlib


class LoadPDF:

    def __init__(self):
        self.PDF_DIR = "app/storage/pdfs"
        self.META_DIR = "app/storage/metadata"

    def store_pdf(self, file):
        self.ensure_dirs()

        meta_path = os.path.join(self.META_DIR, "documents.json")

        # 1. hash file
        file_hash = self.get_file_hash(file)

        # 2. check duplicate
        existing = self.find_by_hash(file_hash, meta_path)

        if existing:
            return {
                "document_id": existing["document_id"],
                "doc_path": os.path.join(self.PDF_DIR, existing["stored_as"]),
                "filename": existing["filename"],
                "duplicate": True
            }

        # 3. new document
        doc_id = str(uuid.uuid4())

        pdf_path = self.save_pdf(file, doc_id)

        self.save_metadata(doc_id, file.filename, file_hash)

        return {
            "document_id": doc_id,
            "doc_path": pdf_path,
            "filename": file.filename,
            "duplicate": False
        }

    def ensure_dirs(self):
        os.makedirs(self.PDF_DIR, exist_ok=True)
        os.makedirs(self.META_DIR, exist_ok=True)

    
    def get_file_hash(self, file):
        content = file.file.read()
        file.file.seek(0)  
        return hashlib.md5(content).hexdigest()
    
    def find_by_hash(self, file_hash, meta_path):
        if not os.path.exists(meta_path):
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                documents = json.load(f)

            for doc in documents:
                if doc.get("file_hash") == file_hash:
                    return doc

        except json.JSONDecodeError:
            return None

        return None


    def save_pdf(self, file, doc_id):
        file_path = os.path.join(self.PDF_DIR, f"{doc_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path

    def save_metadata(self, doc_id, filename, file_hash):
        metadata = {
            "document_id": doc_id,
            "filename": filename,
            "stored_as": f"{doc_id}.pdf",
            "file_hash": file_hash,
            "upload_time": datetime.utcnow().isoformat(),
            "status": "uploaded",
            "content": None
        }

        meta_path = os.path.join(self.META_DIR, "documents.json")

        documents = []

        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                    if content:
                        documents = json.loads(content)

            except json.JSONDecodeError:
                documents = []

        # Add new record
        documents.append(metadata)

        # Save updated list
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=4)

