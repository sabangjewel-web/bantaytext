"""BantayText: AI-Powered Scam Text Detector and Safety Advisor for Taglish and Bisaya Messages."""
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from services import ml_service
from services.analyzer import analyze_message
from services.gemini_service import DEFAULT_MODEL

st.set_page_config(page_title="BantayText", page_icon="🛡️", layout="centered")

SAMPLES = {
    "Fake GCash": "ALERT: Ang GCash account mo ay LIMITED na. I-verify agad sa gcash-verify-ph.xyz/login at ilagay ang OTP o ma-block permanently within 24 hrs.",
    "Raffle (Bisaya)": "Nakadaog ka ug PHP 50,000 sa Smart Mega Raffle! Pagbayad lang ug PHP 500 processing fee aron madawat ang premyo. Pindota: bit.ly/claim50k",
    "Job offer": "HIRING! Work from home, PHP 3,000 DAILY, like lang sa videos. Magdeposit lang ng PHP 1,000 for activation. Message us sa Telegram.",
    "Fake delivery": "J&T Express: Hindi ma-deliver ang parcel mo. I-update ang address at magbayad ng PHP 35 sa jnt-redelivery-ph.top",
    "Safe message": "Ma, nasa terminal na ako. Susunod ako sa Colon, may bibilhin lang ako. Kita tayo mamaya.",
}
COLORS = {"Safe": "green", "Suspicious": "orange", "Scam": "red"}
ICONS = {"Safe": "✅", "Suspicious": "⚠️", "Scam": "🚨"}


def get_secret(name: str, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name, default)


@st.cache_resource
def load_model():
    return ml_service.train_model()


model = load_model()
api_key = get_secret("GEMINI_API_KEY")
model_name = get_secret("GEMINI_MODEL", DEFAULT_MODEL)

if "history" not in st.session_state:
    st.session_state.history = []
if "text" not in st.session_state:
    st.session_state.text = ""

st.title("🛡️ BantayText")
st.caption("AI Scam Text Detector and Safety Advisor for Taglish and Bisaya messages")

with st.sidebar:
    st.header("Settings")
    language = st.radio("Language ng explanation", ["Taglish", "English", "Bisaya"])
    st.markdown("---")
    st.markdown("**Paano gamitin**\n1. I-paste ang text message\n2. I-click ang *Analyze*\n3. Basahin ang verdict at payo")
    st.markdown("---")
    st.info("Huwag mag-paste ng personal na info (OTP, password, buong account number).")
    if not api_key:
        st.warning("Walang Gemini API key. ML-only mode muna.")

st.subheader("Sample messages")
cols = st.columns(len(SAMPLES))
for col, (name, msg) in zip(cols, SAMPLES.items()):
    if col.button(name, use_container_width=True):
        st.session_state.text = msg

text = st.text_area("I-paste ang suspicious na message dito:", key="text", height=140, max_chars=1000)

if st.button("🔍 Analyze", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Maglagay muna ng message.")
    else:
        with st.spinner("Sinusuri ang message..."):
            res = analyze_message(text.strip(), model, api_key, language, model_name)
        if "error" in res:
            st.error(f"Hindi nakonekta sa Gemini, ML result ang ipinapakita. ({res['error'][:150]})")

        color = COLORS[res["verdict"]]
        st.markdown(f"## {ICONS[res['verdict']]} :{color}[{res['verdict'].upper()}]")
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk score", f"{res['risk_score']}/100")
        c2.metric("Scam type", res["scam_type"])
        c3.metric("ML second opinion", f"{res['ml']['scam_probability']}%")
        st.progress(res["risk_score"] / 100)

        st.markdown(f"**Explanation:** {res['explanation']}")
        if res["red_flags"]:
            st.markdown("**Red flags:**")
            for flag in res["red_flags"]:
                st.markdown(f"- 🚩 {flag}")
        st.success(f"**Gagawin mo:** {res['advice']}")
        if res.get("agreement") is True:
            st.caption("Parehong nagkasundo ang Gemini at ML model.")
        elif res.get("agreement") is False:
            st.caption("Magkaiba ang resulta ng Gemini at ML. Mag-ingat pa rin.")
        st.caption(f"Source: {res['source']}")

        st.session_state.history.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Message": text.strip()[:60] + ("..." if len(text.strip()) > 60 else ""),
            "Verdict": res["verdict"],
            "Risk": res["risk_score"],
            "Type": res["scam_type"],
        })

st.markdown("---")
st.subheader("📊 History at Dashboard")
if st.session_state.history:
    hist = pd.DataFrame(st.session_state.history)
    st.dataframe(hist, use_container_width=True, hide_index=True)
    scams = hist[hist["Type"] != "None"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.pie(hist, names="Verdict", title="Verdicts",
                               color="Verdict", color_discrete_map=COLORS), use_container_width=True)
    with right:
        if not scams.empty:
            st.plotly_chart(px.pie(scams, names="Type", title="Scam types"), use_container_width=True)
        else:
            st.caption("Wala pang scam na na-detect.")
    if st.button("Clear history"):
        st.session_state.history = []
        st.rerun()
else:
    st.caption("Wala pang history. Mag-analyze ng message para lumabas dito.")
