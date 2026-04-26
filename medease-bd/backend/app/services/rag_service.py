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
        context = self.retrieval.format_context(medicines)

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
            "You are MedEase BD, a helpful medicine information assistant for Bangladesh.\n\n"
            "You provide information about Bangladeshi medicines.\n\n"
            f"Database Context:\n{context}\n\n"
            f"User Question: {query}{company_info}\n\n"
            "Instructions:\n"
            "1. Use the database context for brand-specific details (company, strength, form, price)\n"
            "2. For questions about usage, what a medicine treats, side effects, or dosage, you may use your general medical knowledge about the generic drug\n"
            "3. Always clearly state which information comes from the database and which is general knowledge\n"
            "4. If the medicine is not in the context at all, say so politely and then provide what general info you can\n"
            "5. Keep answers concise and helpful\n"
            "6. Always remind users to consult healthcare professionals\n"
            "7. Answer in English\n\n"
            "Assistant: "
        )
        return prompt

    def _build_bangla_prompt(self, query: str, context: str, company: str = None) -> str:
        company_info = f" {company} থেকে" if company else ""
        prompt = (
            "আপনি MedEase BD, বাংলাদেশের জন্য একটি সহায়ক ওষুধ তথ্য সহায়ক।\n\n"
            "আপনি বাংলাদেশী ওষুধ সম্পর্কে তথ্য প্রদান করেন।\n\n"
            f"ডাটাবেজ তথ্য:\n{context}\n\n"
            f"ব্যবহারকারীর প্রশ্ন: {query}{company_info}\n\n"
            "নির্দেশাবলী:\n"
            "1. ব্র্যান্ড-নির্দিষ্ট তথ্যের জন্য ডাটাবেজ তথ্য ব্যবহার করুন (কোম্পানি, শক্তি, ফর্ম, মূল্য)\n"
            "2. ব্যবহার, কি চিকিৎসা করে, পার্শ্বপ্রতিক্রিয়া বা ডোজ সম্পর্কে প্রশ্নের জন্য জেনেরিক ওষুধ সম্পর্কে আপনার সাধারণ চিকিৎসা জ্ঞান ব্যবহার করতে পারেন\n"
            "3. স্পষ্টভাবে বলুন কোন তথ্যটি ডাটাবেজ থেকে এবং কোনটি সাধারণ জ্ঞান\n"
            "4. যদি ওষুধটি তথ্যে না থাকে, বিনয়ের সাথে বলুন এবং তারপর সাধারণ তথ্য প্রদান করুন\n"
            "5. উত্তর সংক্ষিপ্ত এবং সহায়ক রাখুন\n"
            "6. সর্বদা স্বাস্থ্যসেবা পেশাদারদের পরামর্শ নিতে স্মরণ করিয়ে দিন\n"
            "7. বাংলায় উত্তর দিন\n\n"
            "সহায়ক: "
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