import re
from typing import Tuple


class GuardrailService:
    def __init__(self):
        self.blocked_keywords = [
            "illegal", "drug abuse", "overdose", "suicide",
            "drug trafficking", "narcotics",
            "অবৈধ", "মাদক", "আত্মহত্যা", "ওভারডোজ",
        ]
        
        # Patterns that indicate someone is asking for a prescription/recommendation
        self.medical_advice_patterns = [
            r"i have\s+(depression|anxiety|cancer|diabetes|asthma|hypertension|infection|pain|cold|fever)",
            r"i am\s+(suffering|experiencing|facing|having)\s+",
            r"what should i\s+(take|use|do)\s+for",
            r"which\s+(medicine|drug|tablet|med|antibiotic)\s+(is|should|would|can|do you)",
            r"prescribe(\s+me)?",
            r"recommend\s+(a|me|some)\s+(medicine|drug|treatment|antibiotic)",
            r"suitable\s+(medicine|drug|treatment|antibiotic)",
            r"appropriate\s+(medicine|drug|treatment|antibiotic)",
            r"can (you|i)\s+(take|use|have|get)\s+",
            r"give me\s+(a\s+)?(medicine|drug|tablet|antibiotic|prescription)",
        ]

    def check_query(self, query: str) -> tuple:
        """Check if query is safe to process."""
        if not query or len(query.strip()) < 2:
            return False, "Query is too short"

        query_lower = query.lower()
        
        for keyword in self.blocked_keywords:
            if keyword.lower() in query_lower:
                return False, "Query contains inappropriate content"

        if len(query) > 500:
            return False, "Query is too long"

        for pattern in self.medical_advice_patterns:
            if re.search(pattern, query_lower):
                return False, "Please consult a doctor for medical advice. I can only provide medicine information."

        return True, "OK"

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        text = re.sub(r"[<>{}]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


guardrail_service = GuardrailService()