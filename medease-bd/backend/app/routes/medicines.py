from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.retrieval_service import RetrievalService

router = APIRouter()
retrieval_service = RetrievalService()


@router.get("/medicines/search")
async def search_medicines(
    query: str = Query(..., min_length=2, description="Search query"),
    company: Optional[str] = Query(None, description="Filter by company"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
):
    """Search medicines by brand name, generic name, or company."""
    try:
        medicines = retrieval_service.search_medicines(query, company, limit)
        return {
            "query": query,
            "count": len(medicines),
            "medicines": medicines,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/medicines/company/{company}")
async def get_medicines_by_company(company: str):
    """Get medicines from a specific company."""
    try:
        medicines = retrieval_service.get_medicines_by_company(company)
        return {
            "company": company,
            "count": len(medicines),
            "medicines": medicines,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
