import streamlit as st
import random
from api_client import client

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="ROYCE",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- STAR GENERATION ----------------
star_html = ""
for _ in range(150):
    top = random.randint(0, 100)
    left = random.randint(0, 100)
    size = random.choice([1, 2, 3])
    opacity = random.choice([0.3, 0.6, 0.9])
    duration = random.choice([2, 3, 4, 5])

    star_html += f"""
    <div class="star" style="
        top:{top}%;
        left:{left}%;
        width:{size}px;
        height:{size}px;
        opacity:{opacity};
        animation-duration:{duration}s;
    "></div>
    """

# ---------------- CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

#MainMenu, footer, header { visibility: hidden; }
body { overflow: hidden; background:black; }

/* BACKGROUND */
.space-background {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle at 50% 30%, #050608 0%, #020204 40%, #000000 70%);
    z-index: -5;
}

/* STARS */
.star {
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: twinkle infinite ease-in-out;
}
@keyframes twinkle {
    0%,100% { opacity: 0.2; }
    50% { opacity: 1; }
}

/* COMETS */
.comet {
    position: absolute;
    width: 220px;
    height: 2px;
    background: linear-gradient(to left, rgba(255,255,255,0.9), rgba(255,255,255,0));
    filter: drop-shadow(0 0 10px rgba(255,255,255,0.7));
    animation: shoot 5s linear infinite;
}
@keyframes shoot {
    0% { transform: translate(40vw, -40vh) rotate(225deg); opacity: 0; }
    15% { opacity: 1; }
    100% { transform: translate(-80vw, 80vh) rotate(225deg); opacity: 0; }
}

/* TITLE */
.royce-title {
    position: fixed;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Michroma', sans-serif;
    font-size: 10vw;
    letter-spacing: 0.12em;
    color: white;
    text-shadow: 0 0 25px rgba(255,255,255,0.7);
    z-index: 5;
}

/* BUTTON */
div.stButton {
    position: fixed;
    top: 65%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}

div.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(200,200,200,0.5) !important;
    color: #cfcfcf !important;
    font-family: 'Michroma', sans-serif !important;
    letter-spacing: 3px;
    padding: 16px 46px !important;
    transition: all 0.35s ease;
}

div.stButton > button:hover {
    border-color: #ffffff !important;
    color: #ffffff !important;
    box-shadow: 0 0 25px rgba(255,255,255,0.5);
    transform: scale(1.04);
}
</style>
""", unsafe_allow_html=True)

# ---------------- BACKGROUND HTML ----------------
st.markdown(f"""
<div class="space-background">
    {star_html}
    <div class="comet" style="top:15%; right:-10%; animation-delay:0s;"></div>
    <div class="comet" style="top:35%; right:-20%; animation-delay:2s;"></div>
    <div class="comet" style="top:5%; right:10%; animation-delay:4s;"></div>
</div>
""", unsafe_allow_html=True)

# ---------------- LANDING ----------------
def show_landing():
    st.markdown("<div class='royce-title'>ROYCE</div>", unsafe_allow_html=True)

    if st.button("ENTER THE COSMOS"):
        st.session_state.page = "cockpit"
        st.rerun()

# ---------------- COCKPIT ----------------
def show_cockpit():
    st.markdown("<h3 style='color:white;font-family:Michroma;'>ROYCE // CORE</h3>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter coordinates..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("`Calculating...`")
            data = client.send_chat(prompt, st.session_state.messages)
            placeholder.markdown(data.get("response","Error"))

# ---------------- ROUTER ----------------
if st.session_state.page == "landing":
    show_landing()
else:
    show_cockpit()
