# BantayText
AI-Powered Scam Text Detector and Safety Advisor for Taglish and Bisaya Messages.

**Team:** Jewel Sabang and Ryle Reymond Mulet (Section 3-B)
**Live URL:** [paste Streamlit Cloud link here]

## How it works
1. User pastes a suspicious text message.
2. **Gemini API** (zero-shot, JSON output) returns verdict, risk score, scam type, red flags and advice.
3. A local **TF-IDF + Logistic Regression** model (trained on `data/training_messages.csv`) gives a second opinion.
4. If Gemini is unavailable, the app falls back to the ML model only.

## Project structure
```
app.py                    Streamlit UI
services/gemini_service.py  Gemini API call
services/ml_service.py      TF-IDF + Logistic Regression
services/analyzer.py        Combines both results
data/training_messages.csv  Labeled sample messages
```

## Run locally
```
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml   (then put your real key)
streamlit run app.py
```
Get a free key at https://aistudio.google.com. Never commit `secrets.toml`.

## Deploy (Streamlit Community Cloud)
Push to GitHub > share.streamlit.io > New app > pick repo and `app.py` > Advanced settings > Secrets > paste the contents of `secrets.toml.example` with your real key.

## Libraries and AI models
Streamlit, Pandas, Plotly, scikit-learn, google-genai. Models: Gemini (zero-shot classifier), TF-IDF + Logistic Regression.

## Disclaimer
BantayText is a student project and can make mistakes. Always verify with the official bank, e-wallet or courier.
