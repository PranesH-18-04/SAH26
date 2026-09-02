"""
summarizer.py
Uses an LLM (Gemini) to turn a structured alert into a plain-language explanation.
This is a summarization layer only — it does NOT do detection itself.
Detection stays fully local/deterministic in detector.py.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
_model = None

if API_KEY and API_KEY != "your_key_here" and API_KEY != "paste_your_actual_key_here":
    genai.configure(api_key=API_KEY)
    _model = genai.GenerativeModel("gemini-1.5-flash")


def summarize_alert(alert: dict) -> str:
    """
    Returns a one-sentence plain-English explanation of the alert.
    Falls back gracefully if no API key is configured or the call fails,
    so the demo never breaks because of a missing/expired key.
    """
    if _model is None:
        return _fallback_summary(alert)

    prompt = (
        "Explain this network security alert in one plain-English sentence "
        f"for a non-technical reviewer:\n{alert}"
    )
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return _fallback_summary(alert, error=str(e))


def _fallback_summary(alert: dict, error: str = None) -> str:
    base = f"{alert.get('reason', 'Suspicious activity')} from {alert.get('src_ip')} to {alert.get('dst_ip')}:{alert.get('dst_port')}."
    if error:
        return f"{base} (AI summary unavailable: {error})"
    return f"{base} (AI summary unavailable: no API key configured)"
