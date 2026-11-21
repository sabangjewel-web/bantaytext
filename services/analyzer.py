"""Combines the Gemini result with the local ML model into one final result."""
from services import gemini_service, ml_service

FALLBACK_ADVICE = {
    "Scam": "Huwag mag-click ng link o magbigay ng OTP/PIN. I-block ang number at i-report sa GCash/bank o sa 7726.",
    "Suspicious": "Mag-ingat. Huwag munang mag-click o mag-reply. I-verify sa official app o hotline ng kompanya.",
    "Safe": "Mukhang okay ang message, pero huwag pa rin magbigay ng OTP o password sa kahit sino.",
}


def verdict_from_score(score: int) -> str:
    if score >= 70:
        return "Scam"
    if score >= 45:
        return "Suspicious"
    return "Safe"


def analyze_message(text: str, ml_model, api_key: str | None, language: str, model_name: str) -> dict:
    ml = ml_service.predict(ml_model, text)
    result = {"ml": ml, "source": "Gemini + ML"}

    if api_key:
        try:
            ai = gemini_service.analyze(text, api_key, language, model_name)
            result.update(ai)
            ml_verdict = verdict_from_score(ml["scam_probability"])
            result["agreement"] = ml_verdict == ai["verdict"]
            return result
        except Exception as exc:  # network, quota, bad key, bad JSON...
            result["error"] = f"{type(exc).__name__}: {exc}"

    # Fallback: ML-only result so the app still works without the API
    score = ml["scam_probability"]
    verdict = verdict_from_score(score)
    result.update({
        "source": "ML only",
        "verdict": verdict,
        "risk_score": score,
        "scam_type": ml["category"] if verdict != "Safe" else "None",
        "red_flags": [],
        "explanation": "Resulta ito ng local ML model (walang AI explanation dahil hindi available ang Gemini).",
        "advice": FALLBACK_ADVICE[verdict],
        "agreement": None,
    })
    return result
