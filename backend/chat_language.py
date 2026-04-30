# backend/chat_language.py

import re

def detect_language(message: str) -> str:
    """
    Detect language of the message.
    Returns:
    - 'TA'  → Tamil / Tanglish
    - 'EN'  → English
    """

    if not message:
        return "EN"

    msg = message.lower().strip()

    # ============================
    # PURE TAMIL (Unicode check)
    # ============================
    tamil_unicode_pattern = re.compile(r"[\u0B80-\u0BFF]")

    if tamil_unicode_pattern.search(msg):
        return "TA"

    # ============================
    # TANGLISH KEYWORDS
    # ============================
    tanglish_keywords = [
        "vanakkam",
        "epdi",
        "enna",
        "enna da",
        "epdi iruku",
        "event iruka",
        "certificate iruka",
        "team members",
        "innosphere",
        "paavai",
        "sir",
        "madam"
    ]

    if any(word in msg for word in tanglish_keywords):
        return "TA"

    # ============================
    # DEFAULT → ENGLISH
    # ============================
    return "EN"
