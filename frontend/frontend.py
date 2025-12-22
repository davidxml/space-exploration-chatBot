import streamlit as st
import requests
import time
import base64
import os

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="ROYCE | Hyperdrive Uplink",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ASSET CONFIGURATION ---
# 1. Define the Avatar Source for the Chat Stream
# Streamlit accepts a local file path or a URL directly for the 'avatar' parameter.
local_image_path = os.path.join("assets", "astronaut.png")

if os.path.exists(local_image_path):
    ROYCE_AVATAR = local_image_path  # Use your local file
else:
    # Fallback if you haven't put the file there yet
    ROYCE_AVATAR = "https://cdn-icons-png.flaticon.com/512/2026/2026521.png"

# 2. Helper for the Header (HTML requires Base64)
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Get Base64 for the top header (HTML only)
header_img_b64 = get_img_as_base64(local_image_path)
if header_img_b64:
    header_img_src = f"data:image/png;base64,{header_img_b64}"
else:
    header_img_src = ROYCE_AVATAR

# --- CSS STYLING (The "Void" Theme) ---
st.markdown(f"""
<style>
    /* DARK VOID BACKGROUND */
    .stApp {{ background-color: #050505; color: #e0e0e0; }}
    
    /* REMOVE PADDING */
    .block-container {{ padding-top: 2rem; padding-bottom: 5rem; }}

    /* CENTERED CHAT INPUT */
    [data-testid="stChatInput"] {{
        max-width: 900px !important;
        margin: 0 auto;
        position: fixed; bottom: 30px; left: 0; right: 0; z-index: 100;
    }}
    .stChatInput textarea {{
        background-color: #1a1a1a !important; color: white !important;
        border: 1px solid #333 !important; border-radius: 12px;
    }}
    
    /* HIDE STREAMLIT BRANDING */
    header, footer {{visibility: hidden;}}

    /* COMET ANIMATION */
    .star-field {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }}
    .comet {{ position: absolute; width: 3px; height: 3px; background: rgba(255, 255, 255, 0.8); box-shadow: 0 0 15px 3px rgba(255, 255, 255, 0.3); border-radius: 50%; animation: fly 2.5s linear infinite; }}
    .comet::before {{ content: ''; position: absolute; top: 50%; transform: translateY(-50%); width: 100px; height: 1px; right: 0; background: linear-gradient(90deg, rgba(255,255,255,0.6), transparent); }}
    @keyframes fly {{ 0% {{ transform: translateX(110vw) translateY(-10vh) rotate(-35deg); opacity: 0; }} 20% {{ opacity: 1; }} 100% {{ transform: translateX(-10vw) translateY(110vh) rotate(-35deg); opacity: 0; }} }}
</style>
<div class="star-field" id="starField"></div>
<script>
    function createComet() {{
        const starField = document.getElementById('starField');
        if (!starField) return;
        const comet = document.createElement('div');
        comet.className = 'comet';
        comet.style.top = Math.random() * 70 + '%'; 
        comet.style.animationDuration = (Math.random() * 1.5 + 1.5) + 's';
        starField.appendChild(comet);
        setTimeout(() => {{ comet.remove(); }}, 3000);
    }}
    setInterval(createComet, 250);
</script>
""", unsafe_allow_html=True)

# --- HEADER (Using HTML Base64 Image) ---
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown(f"""
        <img src="{header_img_src}" width="85" 
        style="border-radius: 50%; border: 3px solid #00ff00; box-shadow: 0 0 15px #00ff00;">
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="padding-top: 20px; padding-left: 10px;">
        <h1 style="margin:0; font-size: 3rem; color: white; letter-spacing: 2px;">ROYCE</h1>
        <p style="margin:0; color: #00ff00; font-family: monospace; font-size: 0.9rem;">
        ▶ SYSTEM ONLINE // ORBIT: LAGOS // LLAMA-3.3-70B ACTIVE</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render History
for msg in st.session_state.messages:
    # --- CHANGE 1: Use ROYCE_AVATAR variable instead of "🤖" ---
    # If role is user, use User Icon. If assistant, use the Astronaut Image.
    icon = "🧑‍🚀" if msg["role"] == "user" else ROYCE_AVATAR
    
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])

# Handle Input
if prompt := st.chat_input("Enter command coordinates..."):
    # Render User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    # Render Assistant (Waiting...)
    # --- CHANGE 2: Use ROYCE_AVATAR here too ---
    with st.chat_message("assistant", avatar=ROYCE_AVATAR):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("`Decrypting subspace transmission...`")
        
        try:
            history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            response = requests.post(
                API_URL, 
                json={"message": prompt, "history": history_payload},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_text = data["response"]
                
                # Render Final Text
                msg_placeholder.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                
                # Footer Telemetry
                st.markdown(f"""
                <div style='font-size: 0.8rem; color: #00ff00; margin-top: 10px; font-family: monospace;'>
                ⚡ Latency: {data['latency']}s | 🛰️ Sources: {len(data['sources'])}
                </div>
                """, unsafe_allow_html=True)
            else:
                msg_placeholder.error(f"🚨 COMMS FAILURE (Code {response.status_code})")
                
        except Exception as e:
            msg_placeholder.error(f"🚨 SIGNAL LOST: {e}")