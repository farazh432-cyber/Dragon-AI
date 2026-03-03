import streamlit as st
from groq import Groq

# --- 1. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Key: Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Dragon AI", page_icon="🐉", layout="wide")

# --- 2. DRAGON THEME & BUTTON STYLING ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 55px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
    }
    
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
        margin-bottom: 20px;
    }

    /* 🟡 THE GOLD "+" BUTTON STYLING */
    .stPopover button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        border: 2px solid #fff !important;
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CHAT MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR (ADD NEW CHAT) ---
with st.sidebar:
    st.markdown("### 📜 SCROLLS")
    # THE "ADD CHAT" BUTTON
    if st.button("➕ New Dragon Scroll", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- 6. INPUT AREA (UPLOADS + CHAT) ---
footer_col1, footer_col2 = st.columns([0.1, 0.9])

with footer_col1:
    # THE UPLOAD BUTTON
    with st.popover("➕"):
        st.markdown("### 📁 Upload Offering")
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt', 'png', 'jpg'])
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")

with footer_col2:
    prompt = st.chat_input("Speak to the dragon...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are a wise dragon."}] + st.session_state.messages
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=context,
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_resp += chunk.choices[0].delta.content
                resp_area.markdown(full_resp + " ☄️")
        
        st.session_state.messages.append({"role": "assistant", "content": full_resp})
