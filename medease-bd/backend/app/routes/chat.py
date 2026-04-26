from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import rag_service
from app.services.guardrail_service import guardrail_service

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    company: Optional[str] = None
    language: Optional[str] = "en"


class ChatResponse(BaseModel):
    query: str
    response: str
    disclaimer: str
    medicines: list
    status: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat query through RAG pipeline."""
    try:
        sanitized_query = guardrail_service.sanitize_input(request.query)

        is_safe, message = guardrail_service.check_query(sanitized_query)
        if not is_safe:
            raise HTTPException(status_code=400, detail=message)

        result = rag_service.process_query(
            query=sanitized_query,
            company=request.company,
            language=request.language,
        )

        return ChatResponse(
            query=request.query,
            response=result["response"],
            disclaimer=result["disclaimer"],
            medicines=result["medicines"],
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
