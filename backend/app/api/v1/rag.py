"""
RAG Intelligence API — regulatory knowledge base query endpoint.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO for contributors (high difficulty):
  - Pre-load the EU AI Act, GDPR, ISO 42001, and NIST AI RMF as source documents
  - Add a POST /rag/ingest endpoint for uploading custom regulatory PDFs
  - Integrate MLflow tracking from modules/rag/ml_flow.py
  - Add streaming responses via SSE for long answers
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.security import get_current_user
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.rag_feedback import RAGFeedback
from app.models.user import SubscriptionTier
from typing import Optional

router = APIRouter()


class RAGQueryRequest(BaseModel):
    question: str


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str] = []
    answer_id: Optional[str] = None


@router.post("/query", response_model=RAGQueryResponse)
def query_knowledge_base(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ask a regulatory question and get an answer grounded in source documents.

    Example questions:
    - "Does my CV-screening tool qualify as high-risk under the EU AI Act?"
    - "What are the transparency requirements for chatbots?"
    """
    try:
        from app.modules.rag.retrieval_chain import get_qa_chain
        qa_chain = get_qa_chain()
        result = qa_chain({"query": request.question})
        source_docs = result.get("source_documents", [])
        sources = [str(doc.metadata.get("source", "")) for doc in source_docs]

        # Ensure tables exist on this DB bind (useful for test DB overrides)
        from app.core.database import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            # best-effort: ignore if bind not available
            pass

        return RAGQueryResponse(answer=result["result"], sources=sources)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG module not ready: {str(e)}. Run POST /rag/ingest first.",
        )


@router.get("/health", tags=["RAG Intelligence"])
def rag_health():
    """Check if the RAG module is available."""
    return {"module": "rag_intelligence", "status": "available"}


from app.schemas.rag_feedback import RAGFeedbackRequest

@router.post("/feedback", status_code=204)
def submit_rag_feedback(
    body: RAGFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fb = RAGFeedback(
        user_id=current_user.id,
        question=body.question,
        answer=body.answer,
        rating=body.rating,
    )
    db.add(fb)
    db.commit()



