import streamlit as st
from groq import Groq
from supabase import create_client, Client

# --- 1. CONNECTION & INITIALIZATION ---
try:
    # Connect to Supabase and Groq using Streamlit Secrets
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("🚨 Secret Error: Please verify your SUPABASE_URL and Keys in Streamlit Settings.")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. DRAGON UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
        margin-bottom: 0px;
    }
    .top-credit { text-align: center; color: #ffcc33; font-size: 12px; letter-spacing: 4px; font-weight: bold; }
    
    /* MOBILE SIDEBAR VISIBILITY FIX */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] .stButton>button { color: #000000 !important; font-weight: bold; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #000000 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & SIGN-UP SYSTEM ---
if "user" not in st.session_state:
    st.session_state.user = None

def login_signup_ui():
    st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='dragon-header'>DRAGON ACCESS</h1>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔥 Login", "📜 Sign Up"])
    
    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Enter Lair", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Login Denied: {str(e)}")

    with tab_signup:
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Create Account", use_container_width=True):
            try:
                # Sign up the user; note: 'Confirm Email' must be OFF in Supabase
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Account created! Switch to the Login tab.")
            except Exception as e:
                st.error(f"Failed to register: {str(e)}")

# If not logged in, show the login page and stop execution
if not st.session_state.user:
    login_signup_ui()
    st.stop()

# --- 4. SIDEBAR: NAVIGATION & LOGOUT ---
with st.sidebar:
    st.markdown(f"### 🐉 {st.session_state.user.email}")
    
    # Button to start a new chat session
    if st.button("➕ New Dragon Chat", use_container_width=True):
        try:
            # Ensure the user ID is a clean string for the UUID column
            user_id_str = str(st.session_state.user.id)
            new_sess = supabase.table("chat_sessions").insert({"user_id": user_id_str}).execute()
            if new_sess.data:
                st.session_state.current_session_id = new_sess.data[0]['id']
                st.rerun()
        except Exception as e:
            st.error(f"DB Error: {str(e)}")

    st.divider()
    st.markdown("### 📜 Ancient Scrolls")
    
    # Load previous sessions for the logged-in user
    try:
        sessions = supabase.table("chat_sessions").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        for s in sessions.data:
            scroll_title = s['title'][:20] if s['title'] else "Empty Scroll"
            if st.button(f"🔮 {scroll_title}...", key=s['id'], use_container_width=True):
                st.session_state.current_session_id = s['id']
                st.rerun()
    except:
        st.write("No scrolls found.")

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if "current_session_id" not in st.session_state:
    st.info("👈 Use the sidebar to start a new chat or select an ancient scroll!")
    st.stop()

# Fetch chat history for the current session from Supabase
try:
    db_msgs = supabase.table("messages").select("*").eq("session_id", st.session_state.current_session_id).order("created_at").execute()
    history = [{"role": m['role'], "content": m['content']} for m in db_msgs.data]
except Exception:
    history = []

# Display history
for msg in history:
    with st.chat_message(msg["role"], avatar="🐉" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# User Input Logic
if prompt := st.chat_input("Speak to the dragon..."):
    try:
        # 1. Save User Message to Database
        supabase.table("messages").insert({
            "session_id": st.session_state.current_session_id, 
            "role": "user", 
            "content": prompt
        }).execute()
        
        # 2. Update the session title if it's the first message
        if not history:
            supabase.table("chat_sessions").update({"title": prompt[:30]}).eq("id", st.session_state.current_session_id).execute()
        
        # 3. Stream AI Response
        with st.chat_message("assistant", avatar="🐉"):
            resp_area = st.empty()
            full_resp = ""
            context = [{"role": "system", "content": "You are a wise legendary dragon."}] + history + [{"role": "user", "content": prompt}]
            
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_area.markdown(full_resp + " ☄️")
            
            # 4. Save AI Response to Database
            supabase.table("messages").insert({
                "session_id": st.session_state.current_session_id, 
                "role": "assistant", 
                "content": full_resp
            }).execute()
            
            # Auto-scroll to bottom using Javascript
            st.components.v1.html(
                f"<script>window.parent.document.querySelector('.main').scrollTo(0, 100000);</script>",
                height=0
            )
            st.rerun()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
