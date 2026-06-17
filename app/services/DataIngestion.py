from pypdf import PdfReader
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import uuid
from app.core.models import get_embedding_model



class DataIngestion:

    def __init__(self):
        self.embedding_model = get_embedding_model()

        self.client = chromadb.PersistentClient(
            path="app/storage/chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    # Run whole ingestion pipeline:
    def ingest_doc(self, pdf_path, document_id):

        # STEP 0: early stop if already embedded
        if self.is_already_processed(document_id):
            meta = self.get_document_metadata(document_id)

            return {
                "text": meta["content"][:500] if meta and meta.get("content") else "",
                "chunks_length": "already_processed",
                "embeddings_length": "already_processed",
                "collection_count": self.collection.count()
            }

        # Extract text
        text = self.extract_texts(pdf_path)

        # Chunk text
        chunks = self.create_chunks(text)

        # Generate Embeddings
        embeddings = self.generate_embeddings(chunks)

        # Store in vector DB 
        self.store_chunks(document_id, chunks, embeddings)

        # Update metadata after successful storage
        self.update_metadata(document_id, text, status="embedded")

        return {
            "text": text[:500],
            "chunks_length": len(chunks),
            "embeddings_length": len(embeddings),
            "collection_count": self.collection.count()
        }

    # Status Check
    def is_already_processed(self, document_id):
        meta_path = "app/storage/metadata/documents.json"

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                documents = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        for doc in documents:
            if doc["document_id"] == document_id:
                return doc.get("status") == "embedded"

        return False

    # Metadata to return with already processed docs
    def get_document_metadata(self, document_id):
        meta_path = "app/storage/metadata/documents.json"

        with open(meta_path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        for doc in documents:
            if doc["document_id"] == document_id:
                return doc

        return None
    
    # Extract Text from PDF
    def extract_texts(self, pdf_path):
        reader = PdfReader(pdf_path)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        return text

    # Chunking
    def create_chunks(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        return splitter.split_text(text)

    # Embeddings
    def generate_embeddings(self, chunks):
        return self.embedding_model.encode(chunks)

    # Vector Storage
    def store_chunks(self, doc_id, chunks, embeddings):

        ids = [str(uuid.uuid4()) for _ in chunks]

        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )



    # Metadata Update
    def update_metadata(self, document_id, extracted_text, status):

        meta_path = "app/storage/metadata/documents.json"

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                documents = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            documents = []

        for doc in documents:
            if doc["document_id"] == document_id:
                doc["content"] = extracted_text
                doc["status"] = status
                break

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=4)