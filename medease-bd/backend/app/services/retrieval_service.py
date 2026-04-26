from sqlalchemy import or_, case
from app.database import SessionLocal
from app.models.medicine import Medicine, Generic
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

            if query:
                exact_match = Medicine.brand_name.ilike(query)
                starts_with = Medicine.brand_name.ilike(f"{query}%")
                search_query = search_query.order_by(
                    case((exact_match, 0), else_=1),
                    case((starts_with, 0), else_=1),
                    Medicine.brand_name
                )

            medicines = search_query.limit(limit).all()
            return [med.to_dict() for med in medicines]

        except Exception as e:
            print(f"Search error: {e}")
            return []
        finally:
            self.db.close()

    def search_generics(self, generic_name: str) -> Dict[str, Any]:
        """Search generics table for drug info."""
        try:
            gen = (
                self.db.query(Generic)
                .filter(Generic.generic_name.ilike(f"%{generic_name}%"))
                .first()
            )
            if gen:
                return gen.to_dict()
            return {}
        except Exception as e:
            print(f"Generic search error: {e}")
            return {}
        finally:
            self.db.close()

    def get_medicines_by_company(self, company: str) -> List[Dict[str, Any]]:
        medicines = (
            self.db.query(Medicine)
            .filter(Medicine.company.ilike(f"%{company}%"))
            .limit(50)
            .all()
        )
        return [med.to_dict() for med in medicines]

    def format_context(self, medicines: List[Dict[str, Any]], generic_info: Dict[str, Any] = None) -> str:
        if not medicines:
            return "No matching medicines found."

        context = "Found the following medicines:\n\n"
        for i, med in enumerate(medicines, 1):
            context += f"{i}. Brand: {med['brand_name']}\n"
            context += f"   Generic: {med['generic_name']}\n"
            context += f"   Company: {med['company']}\n"
            context += f"   Strength: {med['strength'] or 'N/A'}\n"
            context += f"   Form: {med['form'] or 'N/A'}\n"
            if med.get("price_bdt") and med["price_bdt"] > 0:
                context += f"   Price: ৳{med['price_bdt']:.2f}\n"
            else:
                context += "   Price: N/A\n"
            if med.get("package_info"):
                context += f"   Package: {med['package_info']}\n"
            context += "\n"

        if generic_info:
            context += "\nGeneric Drug Information:\n"
            context += f"Generic Name: {generic_info.get('generic_name', 'N/A')}\n"
            if generic_info.get("drug_class"):
                context += f"Drug Class: {generic_info['drug_class']}\n"
            if generic_info.get("indication"):
                context += f"Indication: {generic_info['indication']}\n"
            if generic_info.get("indication_desc"):
                context += f"Uses: {generic_info['indication_desc'][:500]}\n"
            if generic_info.get("dosage"):
                context += f"Dosage: {generic_info['dosage'][:300]}\n"
            if generic_info.get("side_effects"):
                context += f"Side Effects: {generic_info['side_effects'][:300]}\n"

        return context