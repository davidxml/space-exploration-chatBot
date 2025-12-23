import streamlit as st
import os
import base64
from PIL import Image

# Import our new Client
from api_client import RoyceClient

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ROYCE | Hyperdrive Uplink",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ASSET LOADING SYSTEM ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "royce.png")

# Load Avatar
ROYCE_AVATAR = "https://cdn-icons-png.flaticon.com/512/2026/2026521.png" # Fallback
header_img_src = ROYCE_AVATAR

if os.path.exists(ICON_PATH):
    try:
        ROYCE_AVATAR = Image.open(ICON_PATH)
        with open(ICON_PATH, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
            header_img_src = f"data:image/png;base64,{b64_data}"
    except Exception:
        pass # Fail silently to fallback

# --- CSS STYLING (The Look) ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #050505; color: #e0e0e0; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 5rem; }}
    
    /* Input Box Styling */
    [data-testid="stChatInput"] {{
        max-width: 900px !important;
        margin: 0 auto;
        position: fixed; bottom: 30px; left: 0; right: 0; z-index: 100;
    }}
    .stChatInput textarea {{
        background-color: #1a1a1a !important; color: white !important;
        border: 1px solid #333 !important; border-radius: 12px;
    }}
    
    /* Hide Default Header/Footer */
    header, footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown(f'<img src="{header_img_src}" width="85" style="border-radius: 50%; border: 3px solid #00ff00; box-shadow: 0 0 15px #00ff00;">', unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="padding-top: 20px; padding-left: 10px;">
        <h1 style="margin:0; font-size: 3rem; color: white; letter-spacing: 2px;">ROYCE</h1>
        <p style="margin:0; color: #00ff00; font-family: monospace; font-size: 0.9rem;">
        ▶ SYSTEM ONLINE // ORBIT: LAGOS // LLAMA-3.3 ACTIVE</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Mission Control")
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    if st.button("🗑️ Clear Flight Logs"):
        st.session_state.messages = []
        st.rerun()
    
    # System Status Indicator
    if RoyceClient.get_health():
        st.success("🟢 Backend Online")
    else:
        st.error("🔴 Backend Offline")

# --- CHAT LOOP ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. Render History
for msg in st.session_state.messages:
    icon = "🧑‍🚀" if msg["role"] == "user" else ROYCE_AVATAR
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])

# 2. Handle Input
if prompt := st.chat_input("Enter command coordinates..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    # Get AI Response
    with st.chat_message("assistant", avatar=ROYCE_AVATAR):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("`Decrypting subspace transmission...`")
        
        # Prepare payload
        history_payload = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        # --- CALL THE BACKEND ---
        data = RoyceClient.send_chat(prompt, history_payload, temperature)
        
        if "error" in data:
            msg_placeholder.error(f"🚨 {data['error']}")
        else:
            ai_text = data["response"]
            sources = data.get("sources", [])
            latency = data.get("latency", 0.0)
            
            # Display Text
            msg_placeholder.markdown(ai_text)
            
            # Display Sources (Expandable)
            if sources:
                with st.expander(f"📚 Analyzed {len(sources)} Flight Logs ({latency}s)"):
                    for src in sources:
                        st.markdown(f"**Topic:** {src['topic']} | **File:** `{src['source_file']}`")
                        st.caption(f"\"{src['content_snippet']}\"")
            
            # Update History
            st.session_state.messages.append({"role": "assistant", "content": ai_text})