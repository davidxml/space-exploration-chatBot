import streamlit as st
import requests
import time
import os
from PIL import Image
import random

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_URL}/chat"
LOGIN_URL = f"{BASE_URL}/auth/login"
SIGNUP_URL = f"{BASE_URL}/auth/signup"

st.set_page_config(
    page_title="ROYCE | Secure Uplink",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AUTH STATE ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ASSETS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "royce.png")
ROYCE_AVATAR = "https://cdn-icons-png.flaticon.com/512/2026/2026521.png"

if os.path.exists(image_path):
    try:
        ROYCE_AVATAR = Image.open(image_path)
    except:
        pass

# --- CSS : BLACK + HUD BLUE + BRIGHTER STARS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

.stApp {
    background-color: #010101;
    color: #e6e6e6;
    font-family: 'Michroma', sans-serif;
}

header, footer { visibility: hidden; }

.stTextInput input {
    background: #0b0b0b !important;
    color: #e6e6e6 !important;
    border: 1px solid #1e3a5f !important;
}

button[kind="primary"] {
    background: transparent !important;
    border: 1px solid #3b82f6 !important;
    color: #3b82f6 !important;
    letter-spacing: 2px;
}

button[kind="primary"]:hover {
    background: rgba(59,130,246,0.1) !important;
    box-shadow: 0 0 18px rgba(59,130,246,0.6);
}

button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #333 !important;
    color: #aaa !important;
}

[data-testid="stChatInput"] {
    max-width: 900px;
    margin: 0 auto;
    position: fixed;
    bottom: 30px;
    left: 0;
    right: 0;
}

.star-field {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}

/* BRIGHTER, SPECULAR STARS */
.star {
    position: absolute;
    width: 1px;
    height: 1px;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(255,255,255,0.8), 0 0 12px rgba(255,255,255,0.4);
    opacity: 0.2;
    animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
    0%, 100% { opacity: 0.2; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}
</style>
""", unsafe_allow_html=True)

# --- STATIC STAR FIELD ---
stars_html = ""
for _ in range(150):  # more stars for density
    stars_html += f"<div class='star' style='top:{random.randint(0,100)}%;left:{random.randint(0,100)}%;width:{random.choice([1,2,3])}px;height:{random.choice([1,2,3])}px;'></div>"

st.markdown(f"<div class='star-field'>{stars_html}</div>", unsafe_allow_html=True)

# ==========================================
# 🔐 LOGIN VIEW
# ==========================================
def login_view():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("""
        <div style="border:1px solid #1e3a5f; padding:40px; background:#050505;">
            <h2 style="margin-bottom:5px;">Prepare for Entry</h2>
            <p style="color:#3b82f6;">Let's verify your access before we proceed.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])

        with tab1:
            with st.form("login_form"):
                name = st.text_input("Preferred Name")
                email = st.text_input("Email Address")
                password = st.text_input("Passcode", type="password")
                st.caption("Your data remains private.")
                submit = st.form_submit_button("Confirm Access", type="primary", use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error("Access couldn’t be confirmed. Please check your details.")
                    else:
                        status = st.empty()
                        status.info("Verifying credentials…")
                        time.sleep(0.6)
                        status.info("Confirming access…")
                        time.sleep(0.6)
                        status.info("Establishing secure session…")

                        try:
                            resp = requests.post(LOGIN_URL, json={"email": email, "password": password})
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.token = data["access_token"]
                                st.session_state.user_name = name or data.get("user_name", "Explorer")
                                st.success("Meet ROYCE!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Access couldn’t be confirmed. Please check your details.")
                        except Exception:
                            st.error("System unreachable.")

        with tab2:
            with st.form("signup_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                password = st.text_input("Create Passcode", type="password")
                submit = st.form_submit_button("Generate Identity", use_container_width=True)

                if submit and full_name and email and password:
                    try:
                        resp = requests.post(
                            SIGNUP_URL,
                            json={"email": email, "password": password, "full_name": full_name}
                        )
                        if resp.status_code == 200:
                            st.success("Identity created. You may now log in.")
                        else:
                            st.error(resp.json().get("detail"))
                    except Exception:
                        st.error("Signup service unavailable.")

# ==========================================
# 🚀 CHAT VIEW
# ==========================================
def chat_view():
    st.markdown(f"""
    <h3>ROYCE</h3>
    <p style="color:#3b82f6;">Secure channel active</p>
    """, unsafe_allow_html=True)

    if st.button("LOGOUT", type="secondary"):
        st.session_state.token = None
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    for msg in st.session_state.messages:
        avatar = "🧑‍🚀" if msg["role"] == "user" else ROYCE_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter command coordinates…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant", avatar=ROYCE_AVATAR):
            holder = st.empty()
            holder.markdown("Processing…")

            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                payload = {
                    "message": prompt,
                    "history": st.session_state.messages
                }
                resp = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
                if resp.status_code == 200:
                    reply = resp.json()["response"]
                    holder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                elif resp.status_code == 401:
                    st.error("Session expired.")
                    st.session_state.token = None
                    st.rerun()
                else:
                    holder.error("Transmission error.")
            except Exception:
                holder.error("Signal lost.")

# --- ROUTER ---
if st.session_state.token:
    chat_view()
else:
    login_view()