import streamlit as st
from groq import Groq
import uuid
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. THEME & MOBILE FIXES ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }

    /* 🟢 GREEN BUTTON: New Chat */
    div[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, #00b300, #004d00) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        border-radius: 10px !important;
    }

    /* 📱 MOBILE ONLY FIX: Make Sidebar Text/Icons Black */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] .stButton>button {
            color: #000000 !important;
            font-weight: 800 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #000000 !important;
        }
    }

    /* 🟡 GOLD BUTTON: The + Popover */
    .stPopover button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 50% !important;
        border: 2px solid #ffffff !important;
        width: 50px !important;
        height: 50px !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    }

    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 55px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
    }
    
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {} 
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📜 Ancient Scrolls")
    if st.button("➕ New Dragon Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    st.divider()
    for cid in list(st.session_state.chats.keys()):
        msgs = st.session_state.chats[cid]
        title = msgs[1]["content"][:20] if len(msgs) > 1 else "New Scroll"
        if st.button(f"🐉 {title}...", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- 5. INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat_id] = [
        {"role": "system", "content": "You are a wise legendary dragon."}
    ]

messages = st.session_state.chats[st.session_state.current_chat_id]

# Container for chat messages to help with scrolling
chat_placeholder = st.container()

with chat_placeholder:
    for msg in messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

# --- 6. INPUT & AUTO-SCROLL SCRIPT ---
with st.container():
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        with st.popover("➕"):
            img_file = st.file_uploader("🖼️ Add Image", type=["png", "jpg", "jpeg"])
            doc_file = st.file_uploader("📁 Add Files", type=["pdf", "txt"])
    with c2:
        prompt = st.chat_input("Speak to the Dragon...")

if prompt:
    user_msg = prompt
    messages.append({"role": "user", "content": user_msg})
    with chat_placeholder:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_msg)

    with chat_placeholder:
        with st.chat_message("assistant", avatar="🐉"):
            resp_area = st.empty()
            full_resp = ""
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
    
    messages.append({"role": "assistant", "content": full_resp})
    
    # 📜 THE FIX: JS TO SCROLL TO BOTTOM
    st.components.v1.html(
        """
        <script>
        var windowParent = window.parent;
        windowParent.document.querySelector('.main').scrollTo({
            top: windowParent.document.querySelector('.main').scrollHeight,
            behavior: 'smooth'
        });
        </script>
        """,
        height=0
    )
    st.rerun()
