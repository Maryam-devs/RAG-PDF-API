from fastapi import APIRouter
from pydantic import BaseModel
from app.services.Retrieval import Retrieval
from app.services.ChatLLM import ChatLLM

router = APIRouter()

retrieval = Retrieval()
llm = ChatLLM()


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/chat")
def chat(req: ChatRequest):

    # Retrieve relevant chunks from docs
    results = retrieval.retrieve_relevant_chunks(
        query=req.query,
        top_k=req.top_k
    )

    if "chunks" not in results:
        return results

    # Make context
    context = "\n\n".join(results["chunks"])

    # Send context and prompt to LLM
    answer = llm.generate_answer(req.query, context)

    # Retrieve sources
    sources = []

    for chunk, metadata in zip(
        results["chunks"],
        results["metadatas"]
    ):
        sources.append({
            "doc_id": metadata["doc_id"],
            "chunk_index": metadata["chunk_index"],
            "preview": chunk[:150] + "..."
        })

    return {
        "query": req.query,
        "answer": answer,
        "sources": sources
    }