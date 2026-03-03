import streamlit as st
from groq import Groq
import uuid

# --- 1. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Key: Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Dragon AI", page_icon="🐉", layout="wide")

# --- 2. THE "NO-HOVER" UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    
    /* Header */
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
    }
    
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
    }

    /* 🟡 ALWAYS VISIBLE GOLD "+" BUTTON */
    div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%) !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 26px !important;
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5) !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333;
    }

    /* Make File Uploader Icons & Text Always Visible */
    .stFileUploader label { color: #ffcc33 !important; font-weight: bold !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION & HISTORY STORAGE ---
if "all_scrolls" not in st.session_state:
    st.session_state.all_scrolls = {} # Stores {id: [messages]}
if "current_scroll_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_scroll_id = new_id
    st.session_state.all_scrolls[new_id] = []

# --- 4. SIDEBAR (CHATS LIST) ---
with st.sidebar:
    st.markdown("### 🐉 DRAGON CONTROLS")
    
    # NEW SCROLL BUTTON
    if st.button("➕ START NEW SCROLL", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_scroll_id = new_id
        st.session_state.all_scrolls[new_id] = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 RECENT SCROLLS")
    
    # List all chat sessions
    for sid in list(st.session_state.all_scrolls.keys()):
        msgs = st.session_state.all_scrolls[sid]
        # Title is the first message or "New Scroll"
        title = msgs[0]["content"][:15] + "..." if msgs else "Empty Scroll"
        
        # Highlight active scroll
        btn_label = f"🔥 {title}" if sid == st.session_state.current_scroll_id else f"📜 {title}"
        if st.button(btn_label, key=sid, use_container_width=True):
            st.session_state.current_scroll_id = sid
            st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Get current messages
current_msgs = st.session_state.all_scrolls[st.session_state.current_scroll_id]

# Display Messages
for message in current_msgs:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- 6. FLOATING INPUT & VISIBLE UPLOADS ---
col_btn, col_txt = st.columns([0.15, 0.85])

with col_btn:
    # THE GOLD "+" BUTTON
    with st.popover("+"):
        st.markdown("### 📤 UPLOAD CENTER")
        
        # Options are now fully visible inside the popover
        st.write("🖼️ **IMAGES**")
        img = st.file_uploader("Upload Image", type=['png','jpg','jpeg'], key="img_up")
        
        st.divider()
        
        st.write("📁 **FILES**")
        doc = st.file_uploader("Upload Doc", type=['pdf','txt','csv'], key="doc_up")
        
        if img or doc:
            st.success("Dragon Received!")

with col_txt:
    prompt = st.chat_input("Speak to the dragon...")

# --- 7. CHAT PROCESSING ---
if prompt:
    # Save to current scroll
    current_msgs.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are a wise dragon."}] + current_msgs
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=context,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_area.markdown(full_resp + " ☄️")
            
            current_msgs.append({"role": "assistant", "content": full_resp})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
