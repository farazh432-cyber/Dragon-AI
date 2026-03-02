import streamlit as st
from groq import Groq
from supabase import create_client, Client
import uuid

# --- 1. SECURE CONNECTION ---
try:
    # Fetches from your Streamlit Secrets
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error(f"Secret Error: Ensure SUPABASE_URL, SUPABASE_KEY, and GROQ_API_KEY are in Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. DRAGON THEME & MOBILE UI FIX ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 55px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
        margin-bottom: 0px;
    }
    
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
    }

    /* 📱 MOBILE SIDEBAR FIX: Force text to black for white mobile sidebar */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] .stButton>button { color: #000000 !important; font-weight: bold; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #000000 !important;
        }
    }

    /* 🟡 GOLD "+" POPOVER */
    .stPopover button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: #000000 !important; font-weight: bold !important;
        border-radius: 50% !important; border: 2px solid white !important;
        width: 50px !important; height: 50px !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & SIGN-UP LOGIC ---
if "user" not in st.session_state:
    st.session_state.user = None

def auth_page():
    st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='dragon-header'>DRAGON ACCESS</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔥 Login", "📜 Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="l_email")
        pwd = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Enter the Lair", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Login Failed: {str(e)}")

    with tab2:
        n_email = st.text_input("New Email", key="s_email")
        n_pwd = st.text_input("New Password", type="password", key="s_pwd")
        if st.button("Create Account", use_container_width=True):
            try:
                # Password must be at least 6 characters
                res = supabase.auth.sign_up({"email": n_email, "password": n_pwd})
                st.success("Account created! You can now switch to the Login tab.")
            except Exception as e:
                st.error(f"Sign Up Failed: {str(e)}")

if not st.session_state.user:
    auth_page()
    st.stop()

# --- 4. SIDEBAR: ACCOUNT & SCROLLS ---
with st.sidebar:
    st.markdown(f"**Member:** {st.session_state.user.email}")
    
    if st.button("➕ New Dragon Chat", use_container_width=True):
        new_sess = supabase.table("chat_sessions").insert({"user_id": st.session_state.user.id}).execute()
        st.session_state.current_session_id = new_sess.data[0]['id']
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 Ancient Scrolls")
    
    # Fetch sessions from DB
    sessions = supabase.table("chat_sessions").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
    for s in sessions.data:
        title = s['title'][:20] if s['title'] else "Empty Scroll"
        if st.button(f"🐉 {title}...", key=s['id'], use_container_width=True):
            st.session_state.current_session_id = s['id']
            st.rerun()
            
    st.divider()
    if st.button("🚪 Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

# --- 5. MAIN CHAT AREA ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if "current_session_id" not in st.session_state:
    st.info("👈 Use the sidebar to open a scroll or start a new chat!")
    st.stop()

# Load Message History from DB
db_msgs = supabase.table("messages").select("*").eq("session_id", st.session_state.current_session_id).order("created_at").execute()
history = [{"role": m['role'], "content": m['content']} for m in db_msgs.data]

# Show History
for msg in history:
    with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# --- 6. INPUT & ATTACHMENTS ---
with st.container():
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        with st.popover("➕"):
            st.write("### Offering")
            img = st.file_uploader("🖼️ Image", type=["png", "jpg", "jpeg"])
            doc = st.file_uploader("📁 File", type=["pdf", "txt"])
    with col2:
        prompt = st.chat_input("Speak to the dragon...")

# --- 7. CHAT PROCESSING ---
if prompt:
    # Save User Msg to DB
    supabase.table("messages").insert({
        "session_id": st.session_state.current_session_id, 
        "role": "user", 
        "content": prompt
    }).execute()
    
    # Auto-title the scroll if it's the first message
    if not history:
        supabase.table("chat_sessions").update({"title": prompt[:30]}).eq("id", st.session_state.current_session_id).execute()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are a wise legendary dragon."}] + history + [{"role": "user", "content": prompt}]
        
        # AI Logic
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context, stream=True)
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_resp += chunk.choices[0].delta.content
                resp_area.markdown(full_resp + " ☄️")
        
        # Save AI Msg to DB
        supabase.table("messages").insert({
            "session_id": st.session_state.current_session_id, 
            "role": "assistant", 
            "content": full_resp
        }).execute()
        
        # 📜 AUTO-SCROLL JS
        st.components.v1.html(
            f"<script>window.parent.document.querySelector('.main').scrollTo(0, 100000);</script>",
            height=0
        )
        st.rerun()
