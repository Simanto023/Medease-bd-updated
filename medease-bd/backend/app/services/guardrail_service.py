import re
from typing import Tuple


class GuardrailService:
    def __init__(self):
        self.blocked_keywords = [
            "illegal", "drug abuse", "overdose", "suicide",
            "drug trafficking", "narcotics",
            "অবৈধ", "মাদক", "আত্মহত্যা", "ওভারডোজ",
        ]

    def check_query(self, query: str) -> Tuple[bool, str]:
        """Check if query is safe to process."""
        if not query or len(query.strip()) < 2:
            return False, "Query is too short"

        query_lower = query.lower()
        for keyword in self.blocked_keywords:
            if keyword.lower() in query_lower:
                return False, "Query contains inappropriate content"

        if len(query) > 500:
            return False, "Query is too long"

        return True, "OK"

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        text = re.sub(r"[<>{}]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


guardrail_service = GuardrailService()
