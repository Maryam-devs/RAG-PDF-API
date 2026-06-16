from pypdf import PdfReader
import json
import os


class DataIngestion:

    def extract_text(self, pdf_path, document_id):
        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n\n"

        # Save extracted text in metadata
        self.update_metadata(document_id, text)

        return text


    def update_metadata(self, document_id, extracted_text):
        meta_path = "app/storage/metadata/documents.json"

        # Load existing metadata
        with open(meta_path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        # Find and update correct document
        for doc in documents:
            if doc["document_id"] == document_id:
                doc["content"] = extracted_text
                doc["status"] = "processed"
                break

        # Save back to file
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=4)