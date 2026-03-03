import streamlit as st
from groq import Groq

# --- 1. CONNECTION ---
try:
    # Now you ONLY need your Groq API Key in Streamlit Secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Key: Please add GROQ_API_KEY to your Streamlit Secrets.")
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
        font-weight: 800; font-size: 55px; text-align: center;
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.4));
    }
    .top-credit {
        text-align: center; color: #ffcc33; font-size: 12px;
        letter-spacing: 5px; text-transform: uppercase; font-weight: bold;
        margin-bottom: 20px;
    }
    /* Simple Chat Bubble Styling */
    .stChatMessage { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CHAT LOGIC (In-Memory Only) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. INTERFACE ---
st.markdown("<p class='top-credit'>Powered by Classical_Ladder</p>", unsafe_allow_html=True)
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown("### 🐉 Dragon Controls")
    if st.button("🔥 Clear Dragon Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.info("Note: Without a database, refreshing the page will reset the chat.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Speak to the dragon..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant", avatar="🐉"):
        resp_area = st.empty()
        full_resp = ""
        
        # Build context from current session memory
        context = [{"role": "system", "content": "You are a wise legendary dragon."}] + st.session_state.messages
        
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
            
            # Save assistant response to state
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Groq Error: {e}")
