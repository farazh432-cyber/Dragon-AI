import streamlit as st
from groq import Groq
import os

# --- 1. CONFIGURATION & SECURITY ---
# This is the SAFE way. It pulls the key from Streamlit's hidden vault.
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("Please set the GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Dragon AI", page_icon="🐉", layout="wide")

# --- 2. DRAGON THEME (Glassmorphism & Animations) ---
st.markdown("""
    <style>
    .stApp { background: #050505; color: #e0e0e0; }
    
    /* Animation for appearing messages */
    @keyframes fadeInUp { 
        from { opacity: 0; transform: translateY(15px); } 
        to { opacity: 1; transform: translateY(0); } 
    }

    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 75, 75, 0.2) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 10px;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.4s ease-out;
    }

    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 50px; text-align: center;
        filter: drop-shadow(0 0 12px rgba(255, 75, 75, 0.4));
        margin-bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE INTERFACE ---
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.5;'>Ancient Wisdom • Powered by Groq</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Dragon AI. You are a wise, legendary dragon. Use a powerful tone and dragon metaphors."}
    ]

# Display history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Speak to the Dragon..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐉"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using the fastest Llama model on Groq
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + " ●")
            
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"The dragon is resting: {e}")
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})