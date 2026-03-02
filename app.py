import streamlit as st
from groq import Groq
import uuid
import time

# --- 1. CONFIGURATION & SECURITY ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. ADVANCED ANIMATIONS & THEME ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    
    /* Global Text Visibility */
    .stMarkdown, p, span, label, div { color: #ffffff !important; }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(20, 20, 20, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 75, 75, 0.2);
    }

    /* Animation for Chat Bubbles */
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
        margin-bottom: 15px;
    }

    /* Dragon Header Gradient */
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.5));
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chats" not in st.session_state:
    st.session_state.chats = {} # Dictionary of chat_id: list_of_messages
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# --- 4. LOGIN & SIGN-UP PAGE ---
def show_login():
    st.markdown("<h1 class='dragon-header'>DRAGON LAIR</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Enter Lair"):
            if u == "admin" and p == "dragon123": # Default credentials
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Access Denied.")
    
    with tab2:
        st.text_input("New Username")
        st.text_input("New Password", type="password")
        st.button("Create Account", disabled=True, help="Database connection required for Sign-up")

# --- 5. MAIN CHAT APP ---
if not st.session_state.logged_in:
    show_login()
else:
    # --- SIDEBAR: HISTORY ---
    with st.sidebar:
        st.markdown("### 📜 Ancient Scrolls")
        if st.button("➕ New Dragon Chat", use_container_width=True):
            st.session_state.current_chat_id = str(uuid.uuid4())
            st.rerun()
        
        st.divider()
        # Display list of past chats
        for cid in list(st.session_state.chats.keys()):
            # Use the first user message as the title
            title = st.session_state.chats[cid][1]["content"][:20] if len(st.session_state.chats[cid]) > 1 else "Empty Chat"
            if st.button(f"🐉 {title}...", key=cid, use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Get current chat messages
    if st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.chats[st.session_state.current_chat_id] = [
            {"role": "system", "content": "You are a wise legendary dragon. Speak with power and fire."}
        ]
    
    messages = st.session_state.chats[st.session_state.current_chat_id]

    # --- CHAT INTERFACE ---
    st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

    for msg in messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

    # --- INPUT WITH "+" ICON ---
    # In Streamlit 2026, 'accept_file' adds the plus icon automatically
    prompt = st.chat_input(
        "Speak to the dragon...",
        accept_file="multiple", # Enables the '+' icon
        file_type=["png", "jpg", "pdf", "txt"]
    )

    if prompt:
        # Handle file upload notification
        user_content = prompt.text
        if prompt.files:
            user_content += f"\n\n*(Uploaded {len(prompt.files)} file(s))*"
        
        # Add to history
        messages.append({"role": "user", "content": user_content})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_content)
            for f in prompt.files:
                st.caption(f"📎 {f.name}")

        # Dragon AI Response
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
