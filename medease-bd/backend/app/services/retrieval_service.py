from sqlalchemy import or_, case
from app.database import SessionLocal
from app.models.medicine import Medicine
from typing import List, Dict, Any


class RetrievalService:
    def __init__(self):
        self.db = SessionLocal()

    def search_medicines(
        self, query: str, company: str = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search medicines using ILIKE text search with exact brand name priority."""
        try:
            search_query = self.db.query(Medicine)

            conditions = []
            if query:
                search_term = f"%{query}%"
                conditions.append(
                    or_(
                        Medicine.brand_name.ilike(search_term),
                        Medicine.generic_name.ilike(search_term),
                        Medicine.company.ilike(search_term),
                    )
                )

            if company:
                conditions.append(Medicine.company.ilike(f"%{company}%"))

            if conditions:
                search_query = search_query.filter(*conditions)

            # Sort: exact brand name match first, then others
            if query:
                exact_match = Medicine.brand_name.ilike(query)
                starts_with = Medicine.brand_name.ilike(f"{query}%")
                search_query = search_query.order_by(
                    case((exact_match, 0), else_=1),  # Exact brand match first
                    case((starts_with, 0), else_=1),  # Starts with query second
                    Medicine.brand_name  # Alphabetical as tiebreaker
                )

            medicines = search_query.limit(limit).all()
            return [med.to_dict() for med in medicines]

        except Exception as e:
            print(f"Search error: {e}")
            return []
        finally:
            self.db.close()

    def get_medicines_by_company(self, company: str) -> List[Dict[str, Any]]:
        """Get all medicines from a specific company."""
        medicines = (
            self.db.query(Medicine)
            .filter(Medicine.company.ilike(f"%{company}%"))
            .limit(50)
            .all()
        )
        return [med.to_dict() for med in medicines]

    def format_context(self, medicines: List[Dict[str, Any]]) -> str:
        """Format medicine data for LLM prompt."""
        if not medicines:
            return "No matching medicines found."

        context = "Found the following medicines:\n\n"
        for i, med in enumerate(medicines, 1):
            context += f"{i}. Brand: {med['brand_name']}\n"
            context += f"   Generic: {med['generic_name']}\n"
            context += f"   Company: {med['company']}\n"
            context += f"   Strength: {med['strength'] or 'N/A'}\n"
            context += f"   Form: {med['form'] or 'N/A'}\n"
            if med["price_bdt"]:
                context += f"   Price: ৳{med['price_bdt']:.2f}\n\n"
            else:
                context += "   Price: N/A\n\n"

        return context