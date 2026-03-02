import streamlit as st
from groq import Groq
import uuid

# --- 1. CONFIGURATION ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. ADVANCED THEME & ANIMATIONS ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    
    /* Animation for the chat input and sub-menus */
    @keyframes popUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Styling the Chat Input and + Button area */
    .stChatInputContainer {
        animation: popUp 0.5s ease-out;
        padding-bottom: 40px !important; /* Space for the footer */
    }

    /* Powered by Classical_Ladder Text */
    .footer-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 12px;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* Chat Bubbles Slide-in */
    @keyframes slideIn { 
        from { opacity: 0; transform: translateX(-20px); } 
        to { opacity: 1; transform: translateX(0); } 
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px);
        animation: slideIn 0.5s ease-out;
    }

    /* Header Gradient */
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.5));
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {} 
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# --- 4. SIDEBAR HISTORY ---
with st.sidebar:
    st.markdown("### 📜 Ancient Scrolls")
    if st.button("➕ New Dragon Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    st.divider()
    for cid in list(st.session_state.chats.keys()):
        chat_msgs = st.session_state.chats[cid]
        title = chat_msgs[1]["content"][:20] if len(chat_msgs) > 1 else "New Scroll"
        if st.button(f"🐉 {title}...", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat_id] = [
        {"role": "system", "content": "You are a wise legendary dragon. Speak with fire metaphors."}
    ]

messages = st.session_state.chats[st.session_state.current_chat_id]

# Display history
for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

# --- 6. THE "+" INPUT & FOOTER ---
# Using Streamlit's bottom container for the "Powered by" label
with st._bottom:
    st.markdown("<p class='footer-text'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)

# The chat input with multi-file support (This adds the + icon)
prompt_data = st.chat_input(
    "Ask your dragon or share an image/file...",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg", "pdf", "txt", "docx"]
)

if prompt_data:
    user_text = prompt_data.text
    # Handling visual feedback for files
    if prompt_data.files:
        file_names = [f.name for f in prompt_data.files]
        user_text += f"\n\n*Uploaded Offering: {', '.join(file_names)}*"

    messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)
        # Display images directly in the chat if uploaded
        for f in prompt_data.files:
            if f.type.startswith("image/"):
                st.image(f, width=300)

    # Dragon Response
    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_area.markdown(full_resp + " ☄️")
            resp_area.markdown(full_resp)
        except Exception as e:
            st.error(f"The dragon is resting: {e}")
    
    messages.append({"role": "assistant", "content": full_resp})
