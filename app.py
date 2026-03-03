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

# --- 2. THE ULTIMATE DRAGON THEME (CSS) ---
st.markdown("""
    <style>
    /* Main Background: Deep Black Hole */
    .stApp { background-color: #050505; }
    
    /* SIDEBAR: Dragon Scales & Blood Red Gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0505 0%, #050505 100%) !important;
        border-right: 2px solid #ff4b2b !important;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] h3 {
        color: #ffcc33 !important;
        text-shadow: 2px 2px #5a0000;
        letter-spacing: 2px;
    }

    /* DRAGON HEADER */
    .dragon-header {
        background: linear-gradient(90deg, #ff0000, #ffcc33, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 65px; text-align: center;
        filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.8));
        margin-bottom: 0px;
        font-family: 'Georgia', serif;
    }
    
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 14px;
        letter-spacing: 6px; text-transform: uppercase; font-weight: bold;
        opacity: 0.8;
    }

    /* CHAT BUBBLES: Dragon Scale Style */
    .stChatMessage {
        border: 1px solid #330000 !important;
        border-radius: 15px !important;
        background: rgba(40, 10, 10, 0.4) !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }

    /* ALWAYS VISIBLE GOLD "+" BUTTON */
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
        opacity: 1 !important;
    }

    /* Sidebar Buttons (Visible White & Gold) */
    .stButton button {
        background: #2a0505 !important;
        color: #ffffff !important;
        border: 1px solid #ff4b2b !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        border: 1px solid #ffcc33 !important;
        box-shadow: 0 0 10px #ff4b2b;
    }
    
    /* Make Text Inputs White */
    input { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION LOGIC ---
if "all_scrolls" not in st.session_state:
    st.session_state.all_scrolls = {} 
if "current_scroll_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_scroll_id = new_id
    st.session_state.all_scrolls[new_id] = []

# --- 4. SIDEBAR (DRAGON LAIR CONTROLS) ---
with st.sidebar:
    st.markdown("### 🐲 DRAGON LAIR")
    
    if st.button("🔥 FORGE NEW SCROLL", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_scroll_id = new_id
        st.session_state.all_scrolls[new_id] = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 ANCIENT RECORDS")
    
    # List all chat sessions with a delete option
    for sid in list(st.session_state.all_scrolls.keys()):
        msgs = st.session_state.all_scrolls[sid]
        title = msgs[0]["content"][:15] + "..." if msgs else "Empty Scroll"
        
        col_select, col_del = st.columns([0.8, 0.2])
        with col_select:
            # High-visibility labels
            label = f"🔥 {title}" if sid == st.session_state.current_scroll_id else f"🌑 {title}"
            if st.button(label, key=f"sel_{sid}", use_container_width=True):
                st.session_state.current_scroll_id = sid
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{sid}"):
                del st.session_state.all_scrolls[sid]
                if st.session_state.current_scroll_id == sid:
                    st.session_state.current_scroll_id = None
                st.rerun()

# --- 5. MAIN STAGE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Safety check for deleted current scroll
if not st.session_state.current_scroll_id or st.session_state.current_scroll_id not in st.session_state.all_scrolls:
    st.info("The Dragon awaits... Click 'Forge New Scroll' to begin.")
    st.stop()

# Display Current Messages
current_msgs = st.session_state.all_scrolls[st.session_state.current_scroll_id]
for message in current_msgs:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- 6. FLOATING INPUT & VISIBLE UPLOADS ---
col_btn, col_txt = st.columns([0.15, 0.85])

with col_btn:
    # THE BIG GOLDEN "+"
    with st.popover("+"):
        st.markdown("### 🏺 SACRIFICE DATA")
        
        st.write("🖼️ **IMAGES**")
        st.file_uploader("img", type=['png','jpg','jpeg'], key="img_up", label_visibility="collapsed")
        
        st.divider()
        
        st.write("📁 **FILES**")
        st.file_uploader("doc", type=['pdf','txt','csv'], key="doc_up", label_visibility="collapsed")

with col_txt:
    prompt = st.chat_input("Whisper to the beast...")

# --- 7. CHAT PROCESSING ---
if prompt:
    current_msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are a wise legendary dragon. Speak with authority and ancient wisdom."}] + current_msgs
        
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
            st.error(f"The Dragon is sleeping: {e}")
