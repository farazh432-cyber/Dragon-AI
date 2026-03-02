import streamlit as st
from groq import Groq
import uuid

# --- 1. CONFIGURATION & SECURITY ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. THEME & ANIMATIONS ---
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
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {} # Stores chat history: {id: [messages]}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# --- 4. SIDEBAR: HISTORY ---
with st.sidebar:
    st.markdown("### 📜 Ancient Scrolls")
    if st.button("➕ New Dragon Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    # List previous chats
    for cid in list(st.session_state.chats.keys()):
        # Title is the first user message or "Empty Chat"
        chat_msgs = st.session_state.chats[cid]
        title = chat_msgs[1]["content"][:20] if len(chat_msgs) > 1 else "New Scroll"
        
        if st.button(f"🐉 {title}...", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- 5. MAIN CHAT LOGIC ---
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Ensure current chat exists in state
if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat_id] = [
        {"role": "system", "content": "You are a wise legendary dragon. Speak with power and fire metaphors."}
    ]

messages = st.session_state.chats[st.session_state.current_chat_id]

# Display current chat history
for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

# --- 6. INPUT WITH "+" ICON ---
prompt = st.chat_input(
    "Speak to the dragon...",
    accept_file="multiple", # This enables the '+' icon for files/images
    file_type=["png", "jpg", "pdf", "txt"]
)

if prompt:
    # Process text + file info
    user_text = prompt.text
    if prompt.files:
        user_text += f"\n\n*(Uploaded {len(prompt.files)} file(s))*"
    
    # Add to history
    messages.append({"role": "user", "content": user_text})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)
        for f in prompt.files:
            st.caption(f"📎 {f.name}")

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
