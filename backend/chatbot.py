# backend/chatbot.py
# Powered by Groq API (llama-3.1-8b-instant)

from groq import Groq
from flask import Blueprint, request, jsonify, session, render_template

from backend.config import GROQ_API_KEY
from backend.chat_context import get_full_context
from backend.chat_router import detect_intent
from backend.chat_language import detect_language

chatbot_bp = Blueprint("chatbot", __name__)
client = Groq(api_key=GROQ_API_KEY)


def build_system_prompt(language, context, is_admin=False):
    admin_note = "\nYou are assisting an ADMIN user with full access.\n" if is_admin else ""

    if language == "TA":
        return f"""நீங்கள் InnoSphere Club இன் அதிகாரப்பூர்வ AI உதவியாளர் "Inno".
Paavai Innovation Forum, Paavai Engineering College.
{admin_note}
விதிகள்:
- அரசியல், மதம், தீங்கான தகவல்கள் பேச வேண்டாம்
- தவறான தகவல் கொடுக்க கூடாது
- தெரியாவிட்டால் "InnoSphere குழுவை தொடர்பு கொள்ளுங்கள்" என்று கூறவும்
- நிகழ்நேர தரவைப் பயன்படுத்தி மட்டுமே பதிலளிக்கவும்

நிகழ்நேர தரவு:
{context}"""

    return f"""You are "Inno", the official AI assistant of InnoSphere Club,
Paavai Innovation Forum, Paavai Engineering College.
{admin_note}
Rules:
- Only discuss: InnoSphere events, projects, team members, certificates, and club information
- Do NOT discuss politics, religion, or anything unrelated to InnoSphere
- Do NOT make up information — use only the Live Data below
- If unsure, say "Please contact the InnoSphere team for more details"
- Be warm, concise, and helpful
- When asked about specific people (e.g. "who is the president"), give their name, role, department and ID

Live Data:
{context}"""


@chatbot_bp.route("/chat")
def chat_page():
    return render_template("chatbot.html")


@chatbot_bp.route("/chat/api", methods=["POST"])
def chat_api():
    data         = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message."})

    language = detect_language(user_message)
    intent   = detect_intent(user_message)
    is_admin = session.get("admin_logged_in", False)

    if intent == "ADMIN" and not is_admin:
        return jsonify({"reply": "Admin access only. Please log in as admin."})

    context       = get_full_context(intent=intent)
    system_prompt = build_system_prompt(language=language, context=context, is_admin=is_admin)

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.3,
            max_tokens=400,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print("GROQ ERROR:", e)
        reply = "⚠️ Sorry, I couldn't connect right now. Please try again or contact the InnoSphere team."

    return jsonify({"reply": reply})
