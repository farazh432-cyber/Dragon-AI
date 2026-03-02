import streamlit as st
from groq import Groq
from supabase import create_client, Client

# --- 1. CONNECTION ---
try:
    # Use API URL ending in .supabase.co
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Secrets Error: Verify SUPABASE_URL and Keys in Streamlit Settings.")
    st.stop()

st.set_page_config(page_title="Dragon AI Pro", page_icon="🐉", layout="wide")

# --- 2. DRAGON THEME ---
st.markdown("""
    <style>
    .stApp { background: #050505; }
    .stMarkdown, p, span, label, div { color: #ffffff !important; }
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
    }
    .top-credit { text-align: center; color: #ffcc33; font-size: 12px; letter-spacing: 4px; font-weight: bold; }
    
    /* Mobile Visibility Fix */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] .stButton>button { color: #000000 !important; font-weight: bold; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #000000 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if "user" not in st.session_state:
    st.session_state.user = None

def auth_screen():
    st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='dragon-header'>DRAGON ACCESS</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Login", "Sign Up"])
    
    with t1:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Enter Lair"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Login Denied: {str(e)}")
                
    with t2:
        nem = st.text_input("New Email")
        npw = st.text_input("New Password", type="password")
        if st.button("Register"):
            try:
                supabase.auth.sign_up({"email": nem, "password": npw})
                st.success("Account Created! Use the Login tab now.")
            except Exception as e:
                st.error(f"Registration Failed: {str(e)}")

if not st.session_state.user:
    auth_screen()
    st.stop()

# --- 4. SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.write(f"Logged in: {st.session_state.user.email}")
    
    if st.button("➕ New Dragon Chat", use_container_width=True):
        try:
            # Fixing the UUID/User ID insertion
            new_s = supabase.table("chat_sessions").insert({"user_id": st.session_state.user.id}).execute()
            if new_s.data:
                st.session_state.current_session = new_s.data[0]['id']
                st.rerun()
        except Exception as e:
            st.error(f"DB Error: {str(e)}")

    st.divider()
    try:
        sessions = supabase.table("chat_sessions").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        for s in sessions.data:
            title = s['title'][:20] if s['title'] else "Ancient Scroll"
            if st.button(f"🐉 {title}", key=s['id'], use_container_width=True):
                st.session_state.current_session = s['id']
                st.rerun()
    except:
        st.write("No scrolls found.")
    
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

if "current_session" not in st.session_state:
    st.info("Start a new chat from the sidebar!")
    st.stop()

# Load History
try:
    db_msgs = supabase.table("messages").select("*").eq("session_id", st.session_state.current_session).order("created_at").execute()
    history = [{"role": m['role'], "content": m['content']} for m in db_msgs.data]
except:
    history = []

for m in history:
    with st.chat_message(m["role"], avatar="🐉" if m["role"]=="assistant" else "👤"):
        st.markdown(m["content"])

# Chat Input
if prompt := st.chat_input("Speak..."):
    try:
        # Save User Message
        supabase.table("messages").insert({"session_id": st.session_state.current_session, "role": "user", "content": prompt}).execute()
        
        # Update Title if first message
        if not history:
            supabase.table("chat_sessions").update({"title": prompt[:25]}).eq("id", st.session_state.current_session).execute()
        
        with st.chat_message("assistant", avatar="🐉"):
            r_area = st.empty()
            full_r = ""
            context = [{"role": "system", "content": "You are a wise dragon."}] + history + [{"role": "user", "content": prompt}]
            
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context, stream=True)
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_r += chunk.choices[0].delta.content
                    r_area.markdown(full_r + " ☄️")
            
            # Save Assistant Message
            supabase.table("messages").insert({"session_id": st.session_state.current_session, "role": "assistant", "content": full_r}).execute()
            st.rerun()
    except Exception as e:
        st.error(f"Chat Error: {str(e)}")
