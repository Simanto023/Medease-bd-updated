from app.services.retrieval_service import RetrievalService
from app.services.llm_service import llm_service
from typing import Dict, Any


class RAGService:
    def __init__(self):
        self.retrieval = RetrievalService()

    def process_query(
        self, query: str, company: str = None, language: str = "en"
    ) -> Dict[str, Any]:
        """Process user query through RAG pipeline."""

        medicines = self.retrieval.search_medicines(query, company, limit=5)
        
        # If we found medicines, also look up generic info for the first match
        generic_info = None
        if medicines:
            first_generic = medicines[0].get("generic_name", "")
            generic_info = self.retrieval.search_generics(first_generic)
        
        context = self.retrieval.format_context(medicines, generic_info)

        if language == "bn":
            prompt = self._build_bangla_prompt(query, context, company)
        else:
            prompt = self._build_english_prompt(query, context, company)

        response = llm_service.generate_response(prompt)
        disclaimer = self._get_disclaimer(language)

        return {
            "query": query,
            "response": response,
            "disclaimer": disclaimer,
            "medicines": medicines,
            "context": context,
        }

    def _build_english_prompt(self, query: str, context: str, company: str = None) -> str:
        company_info = f" from {company}" if company else ""
        prompt = (
            f"Medicine database results:\n{context}\n\n"
            f"User question: {query}{company_info}\n\n"
            "Rules:\n"
            "- Only report medicines from the database above\n"
            "- State brand name, generic name, company, strength, form, price\n"
            "- If the context includes Generic Drug Information (indication, uses, dosage), include that in your answer\n"
            "- If price is N/A, say 'Price not available'\n"
            "- Do not mention any medicine or company not in the database\n"
            "- Do not invent dosages or prices\n"
            "- Keep answer short\n"
            "- End with: 'Consult your doctor before taking any medicine.'\n\n"
            "Answer: "
        )
        return prompt

    def _build_bangla_prompt(self, query: str, context: str, company: str = None) -> str:
        company_info = f" {company} থেকে" if company else ""
        prompt = (
            f"ওষুধের ডাটাবেজ:\n{context}\n\n"
            f"প্রশ্ন: {query}{company_info}\n\n"
            "নিয়ম:\n"
            "- শুধুমাত্র উপরের ডাটাবেজের ওষুধ সম্পর্কে বলুন\n"
            "- ব্র্যান্ড নাম, জেনেরিক নাম, কোম্পানি, শক্তি, ফর্ম, মূল্য উল্লেখ করুন\n"
            "- যদি জেনেরিক ওষুধের তথ্য (ব্যবহার, ডোজ) থাকে, উত্তর দিন\n"
            "- মূল্য না থাকলে 'মূল্য পাওয়া যায়নি' বলুন\n"
            "- ডাটাবেজে নেই এমন কিছু বলবেন না\n"
            "- ছোট উত্তর দিন\n"
            "- শেষে বলুন: 'ওষুধ সেবনের আগে ডাক্তারের পরামর্শ নিন।'\n\n"
            "উত্তর: "
        )
        return prompt

    def _get_disclaimer(self, language: str) -> str:
        if language == "bn":
            return (
                "⚠️ গুরুত্বপূর্ণ সতর্কতা: এই তথ্যটি শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে। "
                "কোনো ওষুধ গ্রহণের আগে অবশ্যই একজন নিবন্ধিত চিকিৎসকের পরামর্শ নিন। "
                "MedEase BD কোনো চিকিৎসা পরামর্শ প্রদান করে না।"
            )
        return (
            "⚠️ Important Disclaimer: This information is for educational purposes only. "
            "Always consult a registered healthcare professional before taking any medication. "
            "MedEase BD does not provide medical advice."
        )


rag_service = RAGService()