import streamlit as st
import random
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

# --- 3. GENERATE STARS (PYTHON LOGIC) ---
# Denser starfield
star_html = ""
for _ in range(120):
    top = random.randint(0, 100)
    left = random.randint(0, 100)
    size = random.choice([1, 2, 2, 3]) 
    opacity = random.choice([0.3, 0.5, 0.8, 1.0])
    # Blinking animation duration
    duration = random.choice([3, 4, 5, 6])
    star_html += f'''
    <div class="star" style="
        top:{top}%; left:{left}%; 
        width:{size}px; height:{size}px; 
        opacity:{opacity};
        animation-duration: {duration}s;
    "></div>'''

# --- 4. CSS STYLING ---
st.markdown("""
<style>
    /* NEW FONT: MICHROMA (Wide, Square, Sci-Fi) */
    @import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

    /* GLOBAL RESET */
    body {
        background-color: #000000;
        overflow: hidden;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { margin-top: -60px; }

    /* --- DEEP VOID BACKGROUND --- */
    .space-background {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        /* Deep radial gradient for depth */
        background: radial-gradient(circle at 60% 40%, #0d121f 0%, #000000 85%);
        z-index: 0;
        pointer-events: none;
    }

    /* STARS */
    .star {
        position: absolute;
        background: white;
        border-radius: 50%;
        box-shadow: 0 0 3px rgba(255, 255, 255, 0.6);
        animation: twinkle infinite ease-in-out;
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.1); }
    }

    /* --- NEW COMET ANIMATION (Top-Right -> Bottom-Left) --- */
    .comet {
        position: absolute;
        opacity: 0;
        /* The "Head" and "Tail" Gradient - Tapered look, not a stick */
        width: 300px; height: 3px;
        background: linear-gradient(to left, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 100%);
        border-radius: 50%; /* Rounded head */
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.8));
        animation: shoot 4s linear infinite;
    }
    
    @keyframes shoot {
        0% {
            /* Start: Top Right (Off Screen) */
            transform: translate(50vw, -50vh) rotate(225deg);
            opacity: 0;
        }
        10% {
            /* Fade In & Brighten */
            opacity: 1;
        }
        100% {
            /* End: Bottom Left (Off Screen) */
            transform: translate(-100vw, 100vh) rotate(225deg);
            opacity: 0;
        }
    }

    /* --- CENTER CONTENT --- */
    .center-stage {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
        width: 100%;
    }

    /* --- THE LOGO --- */
    .royce-title {
        font-family: 'Michroma', sans-serif; /* The new font */
        font-size: 12rem; /* MASSIVE */
        color: #FFFFFF;
        margin: 0;
        line-height: 1;
        letter-spacing: 10px;
        
        /* Bloom Effect */
        text-shadow: 
            0 0 15px rgba(255, 255, 255, 0.6),
            0 0 30px rgba(255, 255, 255, 0.3);
    }

    /* --- THE BUTTON --- */
    div.stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: #cccccc !important;
        font-family: 'Michroma', sans-serif !important;
        font-size: 1rem !important;
        letter-spacing: 4px;
        padding: 18px 60px !important;
        margin-top: 80px !important;
        border-radius: 0px !important;
        transition: all 0.4s ease;
    }

    div.stButton > button:hover {
        border-color: #ffffff !important;
        color: #ffffff !important;
        background: rgba(255,255,255,0.05) !important;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.5);
        transform: scale(1.05);
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .royce-title { font-size: 5rem; letter-spacing: 2px; }
    }
    
    /* COCKPIT HEADER */
    .cockpit-header {
        font-family: 'Michroma', sans-serif;
        border-bottom: 1px solid #333;
        padding-bottom: 15px;
        color: white;
        font-size: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

</style>
""", unsafe_allow_html=True)

# --- 5. BACKGROUND RENDER ---
# We inject the python-generated stars + manual comets
st.markdown(f"""
<div class="space-background">
    {star_html}
    <div class="comet" style="top:0%; right:0%; animation-delay:0s;"></div>
    <div class="comet" style="top:20%; right:-10%; animation-delay:2.5s;"></div>
    <div class="comet" style="top:-10%; right:20%; animation-delay:4s;"></div>
</div>
""", unsafe_allow_html=True)

# --- 6. LANDING PAGE ---
def show_landing():
    # THE LOGO
    st.markdown("""
    <div class="center-stage">
        <h1 class="royce-title">ROYCE</h1>
    </div>
    """, unsafe_allow_html=True)

    # THE BUTTON
    # We place the button, using columns to center it perfectly below the text
    _, col, _ = st.columns([1, 0.6, 1])
    with col:
        # Pushing it down visually via CSS margin, but placing it here logically
        if st.button("ENTER THE COSMOS"):
            st.session_state.page = "cockpit"
            st.rerun()

# --- 7. COCKPIT PAGE ---
def show_cockpit():
    st.markdown("""
        <div class='cockpit-header'>
            <span>ROYCE // SYSTEM CORE</span>
            <span style='font-size:0.8rem; color:#00ff00;'>● ONLINE</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Render Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Logic
    if prompt := st.chat_input("Enter coordinates..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            msg_p = st.empty()
            msg_p.markdown("`Calculating...`")
            
            # Backend Call
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            data = client.send_chat(prompt, history)
            
            if "error" in data:
                msg_p.error(data["error"])
            else:
                msg_p.markdown(data["response"])
                st.session_state.messages.append({"role": "assistant", "content": data["response"]})

# --- 8. MAIN ROUTER ---
if __name__ == "__main__":
    if st.session_state.page == "landing":
        show_landing()
    else:
        show_cockpit()