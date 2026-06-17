import chromadb
from app.core.models import get_embedding_model



class Retrieval:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="app/storage/chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

        self.embedding_model = get_embedding_model()


    # Retrieval Function
    def retrieve_relevant_chunks(self, query, top_k=5):

        # Check if DB is empty
        if self.collection.count() == 0:
            return {
                "query": 'Vector Db is empty, Upload a document first',
                "chunks": None,
                "metadatas": None,
                "ids": None
            }

        # Embed query
        embedded_query = self.embed_query(query)

        # Search in vector DB
        results = self.collection.query(
            query_embeddings=[embedded_query],
            n_results=top_k
        )

        # Return clean output
        return {
            "query": query,
            "chunks": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "ids": results["ids"][0]
        }

   
    def embed_query(self, query):
        return self.embedding_model.encode(query).tolist()