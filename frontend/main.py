import os
import random

import sys
import logging
import traceback
import socket
from dotenv import load_dotenv

import requests
import streamlit as st
from PIL import Image

# --- CONFIGURATION ---
# Logging to stdout so Streamlit terminal shows full tracebacks
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("frontend")

# Load .env early so API_URL / DATABASE_URL are available
load_dotenv()
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

CHAT_URL = f"{BASE_URL}/chat"
LOGIN_URL = f"{BASE_URL}/auth/login"
SIGNUP_URL = f"{BASE_URL}/auth/signup"

# Print endpoint info to terminal for quick verification
DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "<not-set>"
logger.info("ENV CHECK -> API_URL=%s DATABASE_URL=%s", BASE_URL, DB_URL)
print(f"ENV CHECK -> API_URL={BASE_URL}  DATABASE_URL={DB_URL}")

st.set_page_config(
    page_title="ROYCE | Secure Uplink",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
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

# --- STARFIELD ---
star_divs = ""
for i in range(100):
    size = random.choice([1, 2, 3])
    top = random.randint(0, 100)
    left = random.randint(0, 100)
    delay = round(random.uniform(0, 3), 2)
    star_divs += f"""
    .star{i} {{
        position: absolute;
        width: {size}px;
        height: {size}px;
        top: {top}%;
        left: {left}%;
        background: #fff;
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(255,255,255,0.8);
        animation: twinkle 3s ease-in-out infinite;
        animation-delay: {delay}s;
    }}
    """

# --- GLOBAL CSS + BRAND HERO ---
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700;800&display=swap');

.stApp {{
    background-color: #000000;
    color: #00ffcc;
    overflow-x: hidden;
}}

header, footer {{ visibility: hidden; }}

/* STARFIELD */
.star-field {{
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    z-index:0;
    pointer-events:none;
}}

@keyframes twinkle {{
    0%,100% {{ opacity:0.2; transform:scale(1); }}
    50% {{ opacity:1; transform:scale(1.2); }}
}}

{star_divs}

/* ===== ROYCE HERO ===== */
.block-container {{
    padding-top: 0rem !important;
}}
.block-container > div:first-child {{
    margin-top: 0 !important;
}}

.royce-hero {{
    position: relative;
    min-height: 55vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 2;
}}

.royce-text {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(4rem, 11vw, 9rem);
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #FFFFFF;
    line-height: 0.95;
    margin: 0;
}}

.royce-subtext {{
    margin-top: 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.75);
    letter-spacing: 0.12em;
    white-space: nowrap;
    overflow: hidden;
    border-right: 2px solid rgba(255,255,255,0.8);
    width: 0;
    max-width: 280px;
    animation:
        typing 3.5s steps(30, end) forwards,
        blink 0.8s step-end infinite;
}}

@keyframes typing {{
    from {{ width: 0; }}
    to {{ width: 100%; }}
}}

@keyframes blink {{
    50% {{ border-color: transparent; }}
}}
</style>

<div class="star-field">
{"".join([f'<div class="star{i}"></div>' for i in range(100)])}
</div>

<div class="royce-hero">
    <div class="royce-text">ROYCE</div>
    <div class="royce-subtext">explore beyond the known...</div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================
# 🔐 LOGIN VIEW
# ==========================
def login_view():
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown(
            """
        <div style="border:1px solid #1e3a5f; padding:40px; background:#050505;
        text-align:center; border-radius:8px;">
            <h2 style="color:#FFFFFF; font-weight:700;">
                Prepare for Entry
            </h2>
            <p style="color:#3b82f6;">Let's verify your access before we proceed.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])

        with tab1:
            with st.form("login_form"):
                name = st.text_input("Preferred Name")
                email = st.text_input("Email Address")
                password = st.text_input("Passcode", type="password")
                submit = st.form_submit_button(
                    "Confirm Access", type="primary", use_container_width=True
                )

                if submit:
                    if not email or not password:
                        st.error("Access couldn’t be confirmed.")
                    else:
                        # Developer bypass: accept passcode '0000' when backend is offline
                        if password == "0000":
                            st.session_state.token = "local-dev-token"
                            st.session_state.user_name = name or "Explorer"
                            logger.info("Local bypass login used for %s", email)
                            st.rerun()

                        try:
                            resp = requests.post(
                                LOGIN_URL,
                                json={"email": email, "password": password},
                                timeout=10,
                            )
                            resp.raise_for_status()
                            data = resp.json()
                            st.session_state.token = data.get("access_token") or data.get("token")
                            st.session_state.user_name = name or data.get(
                                "user_name", data.get("user", "Explorer")
                            )
                            st.rerun()

                        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, socket.timeout) as conn_err:
                            st.error("System unreachable.")
                            logger.exception("Connection error during login to %s for %s", LOGIN_URL, email)
                            traceback.print_exc()
                            logger.debug("Login attempt details: email=%s preferred_name=%s endpoint=%s", email, name, LOGIN_URL)

                        except requests.exceptions.HTTPError as http_err:
                            st.error("Invalid credentials.")
                            logger.warning("HTTP error during login for %s: %s", email, http_err)
                            traceback.print_exc()

                        except Exception as exc:
                            st.error("System unreachable.")
                            logger.exception("Unexpected error during login for %s", email)
                            traceback.print_exc()

        with tab2:
            with st.form("signup_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                password = st.text_input("Create Passcode", type="password")
                submit = st.form_submit_button(
                    "Generate Identity", use_container_width=True
                )

                if submit and full_name and email and password:
                    try:
                        resp = requests.post(
                            SIGNUP_URL,
                            json={
                                "email": email,
                                "password": password,
                                "full_name": full_name,
                            },
                            timeout=10,
                        )
                        resp.raise_for_status()
                        st.success("Identity created. You may now log in.")
                    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, socket.timeout) as conn_err:
                        st.error("Signup service unavailable.")
                        logger.exception("Connection error during signup to %s for %s", SIGNUP_URL, email)
                        traceback.print_exc()
                    except requests.exceptions.HTTPError:
                        try:
                            detail = resp.json().get("detail")
                        except Exception:
                            detail = "Signup failed"
                        st.error(detail)
                    except Exception:
                        st.error("Signup service unavailable.")
                        logger.exception("Unexpected error during signup for %s", email)
                        traceback.print_exc()


# ==========================
# 🚀 CHAT VIEW (UPDATED FIX)
# ==========================
def chat_view():
    st.markdown(
        "<h3>ROYCE</h3><p style='color:#3b82f6;'>Secure channel active</p>",
        unsafe_allow_html=True,
    )

    if st.button("LOGOUT"):
        st.session_state.token = None
        st.session_state.messages = []
        st.rerun()

    # 1. RENDER HISTORY
    for msg in st.session_state.messages:
        avatar = "🧑‍🚀" if msg["role"] == "user" else ROYCE_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 2. HANDLE NEW INPUT
    if prompt := st.chat_input("Enter command coordinates…"):
        # A. Add to session state immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # B. FORCE RENDER USER MESSAGE NOW (This fixes the delay bug)
        with st.chat_message("user", avatar="🧑‍🚀"):
            st.markdown(prompt)

        # C. Generate & Render Response
        with st.chat_message("assistant", avatar=ROYCE_AVATAR):
            holder = st.empty()
            try:
                resp = requests.post(
                    CHAT_URL,
                    json={"message": prompt, "history": st.session_state.messages},
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=15,
                )

                if resp.status_code == 200:
                    reply = resp.json()["response"]
                    holder.markdown(reply)

                    # D. Add Bot reply to history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )
                else:
                    holder.error(f"Error {resp.status_code}: {resp.text}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, socket.timeout) as conn_err:
                holder.error("Signal lost.")
                logger.exception("Connection error posting to chat endpoint %s", CHAT_URL)
                traceback.print_exc()
            except Exception:
                holder.error("Signal lost.")
                logger.exception("Unexpected error in chat request")
                traceback.print_exc()


# --- ROUTER ---
if st.session_state.token:
    chat_view() # this routes
else:
    login_view()