from pypdf import PdfReader
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
        chunks_size = self.create_chunks(text)

        return {
            "text" : text,
            "chunks_size" : chunks_size
        }


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

    
    def create_chunks(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_text(text)
        return len(chunks)