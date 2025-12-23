import streamlit as st
import os
import base64
from PIL import Image

# Import the Production Client
from api_client import client

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="ROYCE | Hyperdrive Uplink",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Royce: Enterprise Space Exploration AI"
    }
)

# --- 2. ASSET MANAGEMENT ---
# Robust path resolution using os.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "royce.png")

# Fallback Avatar if local file is missing
DEFAULT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/2026/2026521.png"
royce_avatar = DEFAULT_AVATAR_URL
header_img_src = DEFAULT_AVATAR_URL

# Safe Image Loading
if os.path.exists(ICON_PATH):
    try:
        # For Streamlit chat bubbles
        royce_avatar = Image.open(ICON_PATH)
        
        # For HTML Header (Base64)
        with open(ICON_PATH, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
            header_img_src = f"data:image/png;base64,{b64_data}"
    except Exception as e:
        print(f"Asset Warning: Could not load local image. Using fallback. {e}")

# --- 3. CSS INJECTION (Theme) ---
st.markdown(f"""
<style>
    /* Global Theme */
    .stApp {{ background-color: #0b0f19; color: #e0e0e0; font-family: 'Inter', sans-serif; }}
    
    /* Input Container Styling */
    .stChatInput {{
        position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; z-index: 999;
    }}
    
    /* Clean Input Box */
    .stChatInput textarea {{
        background-color: #1a1e29 !important; 
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER UI ---
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown(f'<img src="{header_img_src}" width="70" style="border-radius: 50%; border: 2px solid #10b981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);">', unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="padding-top: 15px; padding-left: 10px;">
        <h1 style="margin:0; font-size: 2.2rem; color: #f8fafc; font-weight: 700; letter-spacing: 1px;">ROYCE</h1>
        <p style="margin:0; color: #10b981; font-family: monospace; font-size: 0.85rem;">
        ● SYSTEM ONLINE // SECURE UPLINK // LLAMA-3.3-70B</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("<hr style='border-color: #334155; margin-top: 0;'>", unsafe_allow_html=True)

# --- 5. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Mission Control")
    
    # State Management Controls
    temperature = st.slider("Creativity Index", 0.0, 1.0, 0.6, 0.1, help="Higher values make Royce more imaginative.")
    
    if st.button("🗑️ Purge Logs (Reset)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # Live Health Check
    if client.get_health():
        st.success("🟢 Uplink Active")
    else:
        st.error("🔴 Uplink Offline")
        st.caption("Check Docker/Backend logs.")

# --- 6. CHAT ENGINE ---
# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render Conversation History
for msg in st.session_state.messages:
    icon = "🧑‍🚀" if msg["role"] == "user" else royce_avatar
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])

# Handle User Input
if prompt := st.chat_input("Enter coordinates or query..."):
    # 1. Append User Message to State
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant", avatar=royce_avatar):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("`Processing telemetry...`")
        
        # Prepare Context Payload
        history_payload = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        # 3. Call Backend (Via Robust Client)
        data = client.send_chat(prompt, history_payload, temperature)
        
        # 4. Handle Result
        if "error" in data:
            msg_placeholder.error(f"🚨 {data['error']}")
        else:
            ai_text = data["response"]
            sources = data.get("sources", [])
            latency = data.get("latency", 0.0)
            
            # Display Answer
            msg_placeholder.markdown(ai_text)
            
            # Display Citations (Production Style: Clean Cards)
            if sources:
                with st.expander(f"📚 Verified Sources ({len(sources)} refs | {latency}s)"):
                    for src in sources:
                        st.markdown(f"**{src.get('topic', 'General')}**")
                        st.caption(f"Source: `{src.get('source_file', 'Unknown')}`")
                        st.info(f"\"{src.get('content_snippet', '...')}\"")
            
            # Append AI Message to State
            st.session_state.messages.append({"role": "assistant", "content": ai_text})