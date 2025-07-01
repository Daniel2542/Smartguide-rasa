import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

# --- Load environment and Gemini ---
load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
gen_ai_model = genai.GenerativeModel("gemini-1.5-flash")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# --- Load and cache FAQ + sentence vectors ---
@st.cache_resource
def load_faq_data():
    with open("faq.json", "r") as f:
        data = json.load(f)["intents"]
    corpus = [(q, item["answer"], encoder.encode(q, convert_to_tensor=True))
              for item in data for q in item["questions"]]
    return data, corpus

faq_data, corpus = load_faq_data()
RASA_ENDPOINT = "http://localhost:5005/model/parse"

# --- Logging ---
def log_interaction(prompt, response, source):
    os.makedirs("logs", exist_ok=True)
    path = "logs/chat_logs.json"
    logs = []
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                logs = json.load(f)
        except:
            pass
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "source": source
    })
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

# --- Smart response logic ---
def get_response(prompt):
    try:
        res = requests.post(RASA_ENDPOINT, json={"text": prompt}, timeout=4).json()
        intent = res.get("intent", {}).get("name")
        conf = res.get("intent", {}).get("confidence", 0)
        if conf > 0.7:
            for item in faq_data:
                if intent == item["title"].lower().replace(" ", "_"):
                    log_interaction(prompt, item["answer"], f"Intent: {intent}")
                    return item["answer"]
    except Exception as e:
        print("Rasa error:", e)

    # Semantic similarity fallback
    vec = encoder.encode(prompt, convert_to_tensor=True)
    best_score, best_answer = 0, None
    for q, a, q_vec in corpus:
        sim = util.cos_sim(vec, q_vec).item()
        if sim > best_score:
            best_score = sim
            best_answer = a
    if best_score > 0.65:
        log_interaction(prompt, best_answer, f"Semantic Match ({best_score:.2f})")
        return best_answer

    # Gemini escalation fallback
    try:
        gemini_reply = gen_ai_model.generate_content(
            f"You are a Smart Academy expert. Only respond if sure.\nUser: {prompt}"
        ).text.strip()
    except:
        gemini_reply = ""

    if len(gemini_reply) < 30 or any(kw in gemini_reply.lower() for kw in ["i don't know", "sorry", "unfortunately"]):
        fallback = (
            "I'm not confident I can help with that.\n\n"
            "📞 Contact Smart Academy Support:\n"
            "- Phone: +254 712 345 678\n- Email: support@smartacademy.go.ke"
        )
        log_interaction(prompt, fallback, "Escalation")
        return fallback

    log_interaction(prompt, gemini_reply, "Gemini")
    return gemini_reply

# --- UI setup ---
st.set_page_config(page_title="Smart Academy Assistant", page_icon="💬")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .chatbox {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 360px;
        max-height: 600px;
        background: #f5f5f5;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        padding: 10px;
        overflow-y: auto;
        z-index: 1000;
    }
    .msg {
        padding: 10px 15px;
        margin: 8px;
        border-radius: 20px;
        max-width: 75%;
        word-wrap: break-word;
    }
    .user { background: #dcf8c6; margin-left: auto; text-align: right; }
    .bot { background: #fff; margin-right: auto; text-align: left; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chatbox">', unsafe_allow_html=True)

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Hello 👋, how may I help you today?"}
    ]

# Render chat messages
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="msg {role}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User input
user_input = st.chat_input("Type your question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Typing..."):
        reply = get_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": reply})
