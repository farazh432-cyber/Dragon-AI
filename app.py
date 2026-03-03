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

# --- 2. ADVANCED FUTURISTIC THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0505 0%, #000000 100%) !important;
        border-right: 2px solid #ff4b2b !important;
    }
    
    /* MAIN DRAGON HEADER */
    .dragon-header {
        background: linear-gradient(90deg, #ff0000, #ffcc33, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 70px; text-align: center;
        filter: drop-shadow(0 0 20px rgba(255, 69, 0, 0.9));
        margin-bottom: 0px;
        line-height: 1;
    }

    /* CLASSICAL LADDER SIGNATURE */
    .signature {
        background: linear-gradient(90deg, #ffcc33, #ffffff, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 22px; text-align: center;
        letter-spacing: 8px; text-transform: uppercase;
        margin-top: -10px;
        margin-bottom: 30px;
        filter: drop-shadow(0 0 5px rgba(255, 204, 51, 0.5));
    }
    
    .stChatMessage {
        border: 1px solid #440000 !important;
        background: rgba(20, 5, 5, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
    }

    div[data-testid="stPopover"] > button {
        background: radial-gradient(circle, #ffcc33 0%, #ff4b2b 100%) !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 32px !important;
        border-radius: 50% !important;
        width: 75px !important;
        height: 75px !important;
        border: 4px solid #ffffff !important;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. VISION UTILITY ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- 4. SESSION LOGIC ---
if "all_scrolls" not in st.session_state:
    st.session_state.all_scrolls = {} 

if "current_scroll_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_scroll_id = new_id
    st.session_state.all_scrolls[new_id] = {"name": "Empty Scroll", "msgs": []}

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🐲 SYSTEM STATUS: ONLINE")
    if st.button("🔥 FORGE NEW SCROLL", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_scroll_id = new_id
        st.session_state.all_scrolls[new_id] = {"name": "New Scroll", "msgs": []}
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 ACTIVE DATA CORES")
    
    for sid in list(st.session_state.all_scrolls.keys()):
        data = st.session_state.all_scrolls[sid]
        
        # Self-healing logic for old data formats
        if not isinstance(data, dict):
            st.session_state.all_scrolls[sid] = {"name": "Recovered Scroll", "msgs": data}
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
                if st.session_state.current_scroll_id == sid:
                    st.session_state.current_scroll_id = next(iter(st.session_state.all_scrolls)) if st.session_state.all_scrolls else None
                st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>MADE BY CLASSICAL LADDER</p>", unsafe_allow_html=True)

if not st.session_state.current_scroll_id:
    st.info("The Lair is empty. Click 'Forge New Scroll' to start.")
    st.stop()

current_data = st.session_state.all_scrolls[st.session_state.current_scroll_id]

# Display history
for message in current_data["msgs"]:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- 7. INPUT & MULTIMODAL UPLOADS ---
col_btn, col_txt = st.columns([0.15, 0.85])

with col_btn:
    with st.popover("+"):
        st.markdown("### 🏺 SACRIFICE DATA")
        img_offer = st.file_uploader("🖼️ IMAGE SCAN", type=['png','jpg','jpeg'], key="img_up")
        st.divider()
        doc_offer = st.file_uploader("📁 FILE SCAN", type=['pdf','txt','csv'], key="doc_up")

with col_txt:
    prompt = st.chat_input("Input command, bro...")

# --- 8. AI PROCESSING ---
if prompt:
    current_data["msgs"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        
        # Prepare context
        content_list = [{"type": "text", "text": prompt}]
        if img_offer:
            base64_image = encode_image(img_offer)
            content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
        
        context = [
            {"role": "system", "content": "You are Dragon AI, an authentic, cool, and adaptive AI bro. You act exactly like Gemini. You're witty but grounded, you understand slang like 'wsp', and you're helpful without being a robot."}
        ] + current_data["msgs"][:-1] + [{"role": "user", "content": content_list}]
        
        try:
            model_to_use = "llama-3.2-11b-vision-preview" if img_offer else "llama-3.3-70b-versatile"
            completion = client.chat.completions.create(model=model_to_use, messages=context, stream=True)
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_area.markdown(full_resp + " 🔥") # FIREBALL TYPING EFFECT
            
            current_data["msgs"].append({"role": "assistant", "content": full_resp})
            
            if len(current_data["msgs"]) <= 2:
                current_data["name"] = prompt[:15].upper()
            
            st.rerun()
        except Exception as e:
            st.error(f"System Glitch: {e}")
