import streamlit as st
from groq import Groq
from supabase import create_client, Client

# --- 1. CONNECTION ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Secrets Error: Verify SUPABASE_URL and Keys in Streamlit Settings.")
    st.stop()

st.set_page_config(page_title="Dragon AI", page_icon="🐉", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE SETUP (Fixed Session) ---
# Since we removed login, we'll use a constant "Main Scroll" ID
MAIN_SESSION_ID = "00000000-0000-0000-0000-000000000000"

# --- 4. MAIN INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Load History for the Main Scroll
try:
    db_msgs = supabase.table("messages").select("*").eq("session_id", MAIN_SESSION_ID).order("created_at").execute()
    history = [{"role": m['role'], "content": m['content']} for m in db_msgs.data]
except:
    history = []

# Display History
for m in history:
    with st.chat_message(m["role"], avatar="🐉" if m["role"]=="assistant" else "👤"):
        st.markdown(m["content"])

# Chat Input
if prompt := st.chat_input("Speak to the dragon..."):
    # 1. Save User Message
    try:
        supabase.table("messages").insert({
            "session_id": MAIN_SESSION_ID, 
            "role": "user", 
            "content": prompt
        }).execute()
    except:
        pass # If table doesn't exist, it still shows in UI

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Stream AI Response
    with st.chat_message("assistant", avatar="🐉"):
        r_area = st.empty()
        full_r = ""
        context = [{"role": "system", "content": "You are a wise legendary dragon."}] + history + [{"role": "user", "content": prompt}]
        
        comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context, stream=True)
        for chunk in comp:
            if chunk.choices[0].delta.content:
                full_r += chunk.choices[0].delta.content
                r_area.markdown(full_r + " ☄️")
        
        # 3. Save Assistant Message
        try:
            supabase.table("messages").insert({
                "session_id": MAIN_SESSION_ID, 
                "role": "assistant", 
                "content": full_r
            }).execute()
        except:
            pass
        
        st.rerun()
