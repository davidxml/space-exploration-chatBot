import streamlit as st
from api_client import client

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="ROYCE",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. PRODUCTION CSS & ASSETS ---
st.markdown("""
<style>
    /* IMPORT FONT FOR 'ROYC' (We build 'E' manually) */
    @import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

    /* FIX 1: GLOBAL SCROLL LOCK (Applied to Body) */
    body {
        overflow: hidden;
        background-color: #000000;
    }
    
    /* REMOVE STREAMLIT CHROME */
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { margin-top: -80px; } /* Pull content up to cover header gap */

    /* --- BACKGROUND ANIMATION LAYER --- */
    .space-background {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at center, #0b0f15 0%, #000000 70%);
        z-index: 0;
        pointer-events: none; /* Let clicks pass through */
    }
    
    .star {
        position: absolute; background: white; border-radius: 50%;
        box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
    }
    
    .comet {
        position: absolute;
        width: 150px; height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.8));
        opacity: 0;
        transform: rotate(-45deg);
        animation: meteor 6s linear infinite;
    }

    /* FIX 3: ROBUST METEOR ANIMATION */
    @keyframes meteor {
        0% {
            transform: translateX(0) translateY(0) rotate(-45deg);
            opacity: 0;
        }
        10% { opacity: 1; }
        100% {
            transform: translateX(140vw) translateY(140vh) rotate(-45deg);
            opacity: 0;
        }
    }

    /* --- CENTER STAGE LAYOUT (Flexbox) --- */
    .center-stage {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        width: 100%;
    }

    /* --- LOGO TYPOGRAPHY --- */
    .royce-wrapper {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .royce-text {
        font-family: 'Michroma', sans-serif;
        font-size: 8rem;
        color: #ffffff;
        letter-spacing: 5px;
        margin: 0;
        /* Metallic Gradient */
        background: linear-gradient(to bottom, #ffffff 0%, #a0a0a0 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
    }
    
    /* Mobile Responsiveness for Text */
    @media (max-width: 768px) {
        .royce-text { font-size: 4rem; }
        .custom-e { width: 35px; height: 45px; }
        .e-bar { height: 7px; }
    }

    /* --- CUSTOM 'E' CONSTRUCTION --- */
    .custom-e {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 70px; height: 90px;
        margin-left: 5px;
    }
    .e-bar {
        height: 14px; width: 100%;
        background: linear-gradient(90deg, #e0e0e0, #ffffff);
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    .e-top { border-top-right-radius: 10px; border-bottom-right-radius: 2px; }
    .e-mid { width: 85%; border-radius: 2px; }
    .e-bot { border-bottom-right-radius: 10px; border-top-right-radius: 2px; }

    /* --- CTA BUTTON STYLING (Applied to Real Streamlit Button) --- */
    div.stButton > button {
        background: transparent !important;
        border: 1px solid rgba(192, 192, 192, 0.5) !important;
        color: silver !important;
        font-family: 'Michroma', sans-serif !important;
        letter-spacing: 3px;
        padding: 15px 40px !important;
        font-size: 1rem !important;
        margin-top: 50px !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    div.stButton > button:hover {
        border-color: #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);
        transform: scale(1.05);
    }
    
    /* Center the Streamlit button container */
    div.stButton {
        text-align: center;
        width: 100%;
        display: flex;
        justify-content: center;
    }
    
    /* --- COCKPIT SPECIFIC --- */
    .cockpit-header {
        font-family: 'Michroma', sans-serif;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
        margin-bottom: 20px;
        color: white;
    }

</style>
""", unsafe_allow_html=True)

# --- FIX 2: GLOBAL BACKGROUND INJECTION ---
st.markdown("""
<div class="space-background">
    <div class="star" style="top:10%; left:20%; width:2px; height:2px;"></div>
    <div class="star" style="top:30%; left:80%; width:3px; height:3px; opacity:0.7;"></div>
    <div class="star" style="top:70%; left:10%; width:2px; height:2px;"></div>
    <div class="star" style="top:85%; left:60%; width:2px; height:2px;"></div>

    <div class="comet" style="top:15%; left:-20%; animation-delay:0s;"></div>
    <div class="comet" style="top:45%; left:-30%; animation-delay:2.5s;"></div>
    <div class="comet" style="top:75%; left:-25%; animation-delay:4s;"></div>
</div>
""", unsafe_allow_html=True)

# --- 4. LANDING PAGE ---
def show_landing():
    # FIX 4: Center Stage Layout (Logo only)
    st.markdown("""
    <div class="center-stage">
        <div class="royce-wrapper">
            <span class="royce-text">ROYC</span>
            <div class="custom-e">
                <div class="e-bar e-top"></div>
                <div class="e-bar e-mid"></div>
                <div class="e-bar e-bot"></div>
            </div>
        </div>
        <div style="height: 20px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # FIX 5: Native Button Logic
    # We use columns to "push" the button into the center-stage area visually
    # using the CSS rules defined above (div.stButton > button { margin-top: 50px })
    _, col, _ = st.columns([1, 1, 1])
    with col:
        # This button is styled by the CSS to look exactly like the design
        if st.button("ENTER THE COSMOS", key="enter_btn"):
            st.session_state.page = "cockpit"
            st.rerun()

# --- 5. COCKPIT PAGE ---
def show_cockpit():
    st.markdown("<div class='cockpit-header'>ROYCE // TERMINAL</div>", unsafe_allow_html=True)
    
    # Chat Logic
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Input command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            msg_p = st.empty()
            msg_p.markdown("`Processing...`")
            
            # Use Backend Client
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            data = client.send_chat(prompt, history)
            
            if "error" in data:
                msg_p.error(data["error"])
            else:
                msg_p.markdown(data["response"])
                st.session_state.messages.append({"role": "assistant", "content": data["response"]})

# --- 6. ROUTER ---
if __name__ == "__main__":
    if st.session_state.page == "landing":
        show_landing()
    else:
        show_cockpit()