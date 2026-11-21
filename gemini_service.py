"""Gemini API service: zero-shot scam classification with structured JSON output."""
import json
import os

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.5-flash"  # change via GEMINI_MODEL in secrets if Google renames it

SCAM_TYPES = ["Fake GCash/Bank", "Prize/Raffle", "Job Offer", "Loan",
              "Fake Delivery", "Other Scam", "None"]

SYSTEM_PROMPT = f"""You are BantayText, a scam-text analyst for Filipino users.
You understand English, Tagalog, Taglish, and Bisaya/Cebuano.
Analyze the SMS/chat message given and decide if it is Safe, Suspicious, or Scam.

Look for: urgency or threats, requests for OTP/PIN/MPIN/password/CVV, upfront fees for prizes/loans/jobs,
shortened or look-alike links, too-good-to-be-true money offers, unknown sender pretending to be a bank,
e-wallet, courier or government agency, and requests to move to Telegram/WhatsApp.

Return ONLY a JSON object with these keys:
- verdict: one of "Safe", "Suspicious", "Scam"
- risk_score: integer 0-100
- scam_type: one of {SCAM_TYPES}
- red_flags: list of 1-5 short strings (empty list if Safe)
- explanation: 1-3 sentences explaining the verdict
- advice: 1-3 sentences on what the user should do next
Write red_flags, explanation and advice in the requested language."""

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["Safe", "Suspicious", "Scam"]},
        "risk_score": {"type": "integer"},
        "scam_type": {"type": "string", "enum": SCAM_TYPES},
        "red_flags": {"type": "array", "items": {"type": "string"}},
        "explanation": {"type": "string"},
        "advice": {"type": "string"},
    },
    "required": ["verdict", "risk_score", "scam_type", "red_flags", "explanation", "advice"],
}


def analyze(text: str, api_key: str, language: str = "Taglish", model_name: str = DEFAULT_MODEL) -> dict:
    """Call Gemini and return a validated result dict. Raises on API or parsing errors."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=f"Language for the answer: {language}\n\nMessage to analyze:\n\"\"\"\n{text}\n\"\"\"",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=SCHEMA,
            temperature=0.2,
        ),
    )
    raw = (response.text or "").strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(raw)
    data["risk_score"] = max(0, min(100, int(data["risk_score"])))
    if data["verdict"] not in ("Safe", "Suspicious", "Scam"):
        data["verdict"] = "Suspicious"
    if data["scam_type"] not in SCAM_TYPES:
        data["scam_type"] = "Other Scam"
    return data
