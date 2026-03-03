import streamlit as st
from groq import Groq
import uuid

# --- 1. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Key: Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. THE DRAGON THEME (Visuals) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0505 0%, #050505 100%) !important;
        border-right: 2px solid #ff4b2b !important;
    }
    
    .dragon-header {
        background: linear-gradient(90deg, #ff0000, #ffcc33, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 65px; text-align: center;
        filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.8));
    }
    
    .stChatMessage {
        border: 1px solid #330000 !important;
        border-radius: 15px !important;
        background: rgba(40, 10, 10, 0.4) !important;
    }

    div[data-testid="stPopover"] > button {
        background: radial-gradient(circle, #ffcc33 0%, #ff4b2b 100%) !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 30px !important;
        border-radius: 50% !important;
        width: 70px !important;
        height: 70px !important;
        border: 4px solid #ffffff !important;
        box-shadow: 0 0 25px rgba(255, 75, 43, 0.7) !important;
    }

    .stButton button {
        background: #2a0505 !important;
        color: #ffffff !important;
        border: 1px solid #ff4b2b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION LOGIC ---
if "all_scrolls" not in st.session_state:
    st.session_state.all_scrolls = {} 
if "current_scroll_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_scroll_id = new_id
    st.session_state.all_scrolls[new_id] = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🐲 DRAGON LAIR")
    if st.button("🔥 FORGE NEW SCROLL", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_scroll_id = new_id
        st.session_state.all_scrolls[new_id] = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 ANCIENT RECORDS")
    for sid in list(st.session_state.all_scrolls.keys()):
        msgs = st.session_state.all_scrolls[sid]
        title = msgs[0]["content"][:15] + "..." if msgs else "Empty Scroll"
        col_select, col_del = st.columns([0.8, 0.2])
        with col_select:
            label = f"🔥 {title}" if sid == st.session_state.current_scroll_id else f"🌑 {title}"
            if st.button(label, key=f"sel_{sid}", use_container_width=True):
                st.session_state.current_scroll_id = sid
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{sid}"):
                del st.session_state.all_scrolls[sid]
                st.rerun()

# --- 5. MAIN STAGE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if not st.session_state.current_scroll_id or st.session_state.current_scroll_id not in st.session_state.all_scrolls:
    st.info("The Dragon is ready. Click 'Forge New Scroll' to start.")
    st.stop()

current_msgs = st.session_state.all_scrolls[st.session_state.current_scroll_id]
for message in current_msgs:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- 6. INPUT & UPLOADS ---
col_btn, col_txt = st.columns([0.15, 0.85])
with col_btn:
    with st.popover("+"):
        st.markdown("### 🏺 SACRIFICE DATA")
        st.file_uploader("img", type=['png','jpg','jpeg'], key="img_up", label_visibility="collapsed")
        st.divider()
        st.file_uploader("doc", type=['pdf','txt','csv'], key="doc_up", label_visibility="collapsed")

with col_txt:
    prompt = st.chat_input("What's on your mind, bro?")

# --- 7. GEMINI-STYLE PROCESSING ---
if prompt:
    current_msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        
        # GEMINI-INSPIRED SYSTEM PROMPT
        context = [
            {"role": "system", "content": """You are Dragon AI, an authentic, adaptive AI collaborator with a touch of wit. 
            Your goal is to address the user's true intent with insightful, clear, and concise responses. 
            Balance empathy with candor: be supportive and grounded. 
            Subtly adapt your tone and humor to the user's style. 
            If they use slang like 'wsp', 'wassup', or 'bro', respond naturally like a cool peer. 
            Don't be a rigid lecturer and don't give nonsense 'I don't understand' replies to simple slang."""}
        ] + current_msgs
        
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
