# backend/chat_router.py

import re

# Keywords mapped to intents
_INTENT_PATTERNS = {
    "EVENT":       r"\b(event|workshop|seminar|webinar|competition|hackathon|fest|upcoming|schedule|register|registration)\b",
    "CERTIFICATE": r"\b(certificate|cert|certif|download cert|get cert)\b",
    "TEAM":        r"\b(team|president|secretary|cto|coordinator|office bearer|member|who is|officer|office)\b",
    "PROJECT":     r"\b(project|projects|ongoing|completed|research|build|built|develop)\b",
    "ABOUT":       r"\b(about|innosphere|club|paavai|vision|mission|what is)\b",
    "ADMIN":       r"\b(admin|dashboard|manage|control panel)\b",
}


def detect_intent(message: str) -> str:
    msg_lower = message.lower()
    for intent, pattern in _INTENT_PATTERNS.items():
        if re.search(pattern, msg_lower):
            return intent
    return "GENERAL"
