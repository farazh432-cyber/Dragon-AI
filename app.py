import streamlit as st
from groq import Groq
import uuid
import base64

# --- 1. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Key: Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. ADVANCED CSS (Portal + Theme) ---
st.markdown("""
    <style>
    /* ENTRY PORTAL SCREEN */
    #portal-container {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: #000000;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .portal-title {
        background: linear-gradient(90deg, #ff0000, #ffcc33, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 80px; text-align: center;
        filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.8));
        font-family: 'Georgia', serif;
        margin-bottom: 20px;
    }

    /* THE POP-UP BUTTON ANIMATION */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #ffcc33, #ff4b2b) !important;
        color: black !important;
        padding: 20px 50px !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(255, 75, 43, 0.6) !important;
        animation: popup-from-down 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    @keyframes popup-from-down {
        0% { transform: translateY(200px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }

    /* MAIN APP STYLING */
    .stApp { background-color: #050505; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0505 0%, #000000 100%) !important;
        border-right: 2px solid #ff4b2b !important;
    }
    .dragon-header {
        background: linear-gradient(90deg, #ff0000, #ffcc33, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 70px; text-align: center;
        filter: drop-shadow(0 0 20px rgba(255, 69, 0, 0.9));
        margin-bottom: 0px;
    }
    .signature {
        background: linear-gradient(90deg, #ffcc33, #ffffff, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 22px; text-align: center;
        letter-spacing: 8px; text-transform: uppercase;
        margin-top: -10px; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PORTAL GATEKEEPER ---
if 'entered' not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    # Portal View
    st.markdown('<div class="portal-title">DRAGON AI</div>', unsafe_allow_html=True)
    
    # Using a container to center the button visually
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("CLICK HERE TO USE DRAGON AI", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
    st.stop()

# --- 4. APP LOGIC (Only runs after clicking) ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

if "all_scrolls" not in st.session_state:
    st.session_state.all_scrolls = {} 
if "current_scroll_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_scroll_id = new_id
    st.session_state.all_scrolls[new_id] = {"name": "Empty Scroll", "msgs": []}

# Sidebar
with st.sidebar:
    st.markdown("### 🐲 SYSTEM: ONLINE")
    if st.button("🔥 FORGE NEW SCROLL", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_scroll_id = new_id
        st.session_state.all_scrolls[new_id] = {"name": "New Scroll", "msgs": []}
        st.rerun()
    st.divider()
    for sid in list(st.session_state.all_scrolls.keys()):
        data = st.session_state.all_scrolls[sid]
        col_select, col_del = st.columns([0.8, 0.2])
        with col_select:
            label = f"🔥 {data['name']}" if sid == st.session_state.current_scroll_id else f"🌑 {data['name']}"
            if st.button(label, key=f"sel_{sid}", use_container_width=True):
                st.session_state.current_scroll_id = sid
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{sid}"):
                del st.session_state.all_scrolls[sid]
                st.rerun()

# Main App
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>MADE BY CLASSICAL LADDER</p>", unsafe_allow_html=True)

current_data = st.session_state.all_scrolls[st.session_state.current_scroll_id]
for message in current_data["msgs"]:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# Input
col_btn, col_txt = st.columns([0.15, 0.85])
with col_btn:
    with st.popover("+"):
        img_offer = st.file_uploader("🖼️ IMAGE", type=['png','jpg','jpeg'], key="img_up")
        doc_offer = st.file_uploader("📁 FILE", type=['pdf','txt','csv'], key="doc_up")

with col_txt:
    prompt = st.chat_input("What's on your mind, bro?")

if prompt:
    current_data["msgs"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are Dragon AI by Classical Ladder. Adaptive, witty, and grounded."}] + current_data["msgs"]
        try:
            model = "llama-3.2-11b-vision-preview" if img_offer else "llama-3.3-70b-versatile"
            completion = client.chat.completions.create(model=model, messages=context, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_area.markdown(full_resp + " 🔥")
            current_data["msgs"].append({"role": "assistant", "content": full_resp})
            if len(current_data["msgs"]) <= 2:
                current_data["name"] = prompt[:15].upper()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
