import streamlit as st
from groq import Groq
from supabase import create_client, Client
import uuid

# --- 1. CONNECTIONS ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Connection Error: Please check your Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. THEME & MOBILE UI FIXES ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    
    /* Header & Credits */
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 55px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
    }
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
        margin-bottom: 10px;
    }

    /* 📱 MOBILE SIDEBAR FIX: Force black text for white mobile sidebars */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] .stButton>button { color: #000000 !important; font-weight: bold; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #000000 !important;
        }
    }

    /* 🟡 GOLD "+" POPOVER BUTTON */
    .stPopover button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: #000000 !important; font-weight: bold !important;
        border-radius: 50% !important; border: 2px solid white !important;
        width: 50px !important; height: 50px !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }

    /* 🟢 GREEN NEW CHAT BUTTON */
    div[data-testid="stSidebar"] .stButton>button:first-child {
        background: linear-gradient(135deg, #00b300, #004d00) !important;
        color: white !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN / SIGNUP LOGIC ---
if "user" not in st.session_state:
    st.session_state.user = None

def auth_page():
    st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='dragon-header'>DRAGON ACCESS</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔥 Login", "📜 Sign Up"])
    
    with t1:
        email = st.text_input("Email", key="l_email")
        pwd = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Enter Lair", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.rerun()
            except: st.error("Invalid credentials.")

    with t2:
        n_email = st.text_input("New Email", key="s_email")
        n_pwd = st.text_input("New Password", type="password", key="s_pwd")
        if st.button("Create Account", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": n_email, "password": n_pwd})
                st.success("Account created! You can now log in.")
            except: st.error("Sign up failed.")

if not st.session_state.user:
    auth_page()
    st.stop()

# --- 4. SIDEBAR: HISTORY & LOGOUT ---
with st.sidebar:
    st.markdown(f"**Member:** {st.session_state.user.email}")
    
    if st.button("➕ New Dragon Chat", use_container_width=True):
        new_sess = supabase.table("chat_sessions").insert({"user_id": st.session_state.user.id}).execute()
        st.session_state.current_session_id = new_sess.data[0]['id']
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 Ancient Scrolls")
    
    # Load history from Supabase
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

# --- 5. MAIN INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if "current_session_id" not in st.session_state:
    st.info("👈 Start a new chat in the sidebar to begin!")
    st.stop()

# Get messages from DB
db_msgs = supabase.table("messages").select("*").eq("session_id", st.session_state.current_session_id).order("created_at").execute()
history = [{"role": m['role'], "content": m['content']} for m in db_msgs.data]

# Display history
for msg in history:
    with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# --- 6. "+" MENU & CHAT INPUT ---
with st.container():
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        with st.popover("➕"):
            st.write("### Add Offering")
            img = st.file_uploader("🖼️ Add Image", type=["png", "jpg", "jpeg"])
            doc = st.file_uploader("📁 Add Files", type=["pdf", "txt"])
    with col2:
        prompt = st.chat_input("Speak to the dragon...")

# --- 7. CHAT LOGIC ---
if prompt:
    # Save User to DB
    supabase.table("messages").insert({"session_id": st.session_state.current_session_id, "role": "user", "content": prompt}).execute()
    
    # Update Scroll Title if first message
    if not history:
        supabase.table("chat_sessions").update({"title": prompt[:30]}).eq("id", st.session_state.current_session_id).execute()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        context = [{"role": "system", "content": "You are a wise legendary dragon."}] + history + [{"role": "user", "content": prompt}]
        
        # Stream from Groq
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context, stream=True)
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_resp += chunk.choices[0].delta.content
                resp_area.markdown(full_resp + " ☄️")
        
        # Save AI to DB
        supabase.table("messages").insert({"session_id": st.session_state.current_session_id, "role": "assistant", "content": full_resp}).execute()
        
        # 📜 AUTO-SCROLL FIX
        st.components.v1.html(
            f"<script>window.parent.document.querySelector('.main').scrollTo(0, 100000);</script>",
            height=0
        )
        st.rerun()
