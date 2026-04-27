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
        """Search medicines - extracts keywords and also searches generics indications."""
        try:
            stop_words = {
                "what", "is", "the", "of", "a", "an", "for", "used", "in", "to",
                "price", "dosage", "side", "effects", "does", "how", "much", "cost",
                "tell", "me", "about", "can", "you", "i", "need", "want", "know",
                "and", "or", "its", "have", "with", "my", "has", "any", "some",
                "am", "facing", "severe", "mild", "which", "would", "be", "should",
                "feel", "back", "pain", "cold", "fever", "headache", "depression",
                "কি", "কেন", "কিভাবে", "কখন", "কার", "কিসের", "ঔষধ", "ব্যবহার", "দাম"
            }

            words = query.lower().split()
            search_terms = [w for w in words if w not in stop_words and len(w) >= 2]

            if not search_terms:
                search_terms = [query]

            medicines = []
            seen_ids = set()

            # First: Search medicine names (brand, generic, company)
            for term in search_terms[:3]:
                search_query = self.db.query(Medicine)
                search_pattern = f"%{term}%"

                conditions = [
                    or_(
                        Medicine.brand_name.ilike(search_pattern),
                        Medicine.generic_name.ilike(search_pattern),
                        Medicine.company.ilike(search_pattern),
                    )
                ]

                if company:
                    conditions.append(Medicine.company.ilike(f"%{company}%"))

                search_query = search_query.filter(*conditions)

                exact_match = Medicine.brand_name.ilike(term)
                starts_with = Medicine.brand_name.ilike(f"{term}%")
                search_query = search_query.order_by(
                    case((exact_match, 0), else_=1),
                    case((starts_with, 0), else_=1),
                    Medicine.brand_name
                )

                results = search_query.limit(limit).all()
                for med in results:
                    if med.id not in seen_ids:
                        seen_ids.add(med.id)
                        medicines.append(med.to_dict())

            # Second: If no results, search generics indications
            if not medicines:
                for term in search_terms[:3]:
                    gen_results = (
                        self.db.query(Generic)
                        .filter(
                            or_(
                                Generic.indication.ilike(f"%{term}%"),
                                Generic.indication_desc.ilike(f"%{term}%"),
                                Generic.generic_name.ilike(f"%{term}%"),
                            )
                        )
                        .limit(3)
                        .all()
                    )

                    for gen in gen_results:
                        # Find medicines matching this generic
                        matching_meds = (
                            self.db.query(Medicine)
                            .filter(Medicine.generic_name.ilike(f"%{gen.generic_name}%"))
                            .limit(5)
                            .all()
                        )
                        for med in matching_meds:
                            if med.id not in seen_ids:
                                seen_ids.add(med.id)
                                medicines.append(med.to_dict())

            # Third: If still nothing, search symptom keywords in full database
            if not medicines and len(search_terms) > 0:
                # Try each word individually
                for word in words:
                    if len(word) >= 2 and word not in stop_words:
                        full_search = (
                            self.db.query(Medicine)
                            .filter(
                                or_(
                                    Medicine.brand_name.ilike(f"%{word}%"),
                                    Medicine.generic_name.ilike(f"%{word}%"),
                                )
                            )
                            .limit(limit)
                            .all()
                        )
                        for med in full_search:
                            if med.id not in seen_ids:
                                seen_ids.add(med.id)
                                medicines.append(med.to_dict())
                        if len(medicines) >= limit:
                            break

            return medicines[:limit]

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
                context += f"Uses: {generic_info['indication_desc'][:300]}\n"
            if generic_info.get("dosage"):
                context += f"Dosage: {generic_info['dosage'][:200]}\n"
            if generic_info.get("side_effects"):
                context += f"Side Effects: {generic_info['side_effects'][:150]}\n"

        return context