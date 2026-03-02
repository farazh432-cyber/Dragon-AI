import streamlit as st
from groq import Groq
import os

# --- 1. CONFIGURATION & SECURITY ---
# This pulls the key from Streamlit's hidden "Secrets" vault for safety.
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Missing GROQ_API_KEY! Please add it to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Dragon AI", page_icon="🐉", layout="wide")

# --- 2. DRAGON THEME (Optimized for Mobile Visibility) ---
st.markdown("""
    <style>
    /* Force main app background and base text color */
    .stApp { 
        background-color: #050505 !important; 
    }
    
    /* Global text color fix for high contrast on dark background */
    .stMarkdown, p, span, label, div {
        color: #ffffff !important;
    }

    /* Animation for appearing messages */
    @keyframes fadeInUp { 
        from { opacity: 0; transform: translateY(15px); } 
        to { opacity: 1; transform: translateY(0); } 
    }

    /* Glassmorphism Chat Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 75, 75, 0.4) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 10px;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.4s ease-out;
    }

    /* Styling the Header */
    .dragon-header {
        background: linear-gradient(90deg, #ff4b2b, #ffcc33);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; 
        font-size: clamp(30px, 8vw, 60px); /* Responsive size for mobile */
        text-align: center;
        filter: drop-shadow(0 0 12px rgba(255, 75, 75, 0.6));
        margin-bottom: 5px;
    }
    
    .dragon-subtitle {
        text-align: center; 
        opacity: 0.8; 
        font-style: italic;
        margin-bottom: 20px;
    }

    /* Input box styling to make it visible */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE INTERFACE ---
st.markdown("<h1 class='dragon-header'>DRAGON AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='dragon-subtitle'>Ancient Wisdom • Powered by Groq</p>", unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Dragon AI. You are a wise, legendary dragon. Use a powerful, ancient tone and fire/dragon metaphors. Speak as if you are breathing life into words."}
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🐉" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Speak to the Dragon..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate Assistant response
    with st.chat_message("assistant", avatar="🐉"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using Llama 3.3-70b via Groq
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # Added a "cursor" effect while typing
                    response_placeholder.markdown(full_response + " ☄️")
            
            # Final output without the cursor
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"The dragon is resting: {e}")
    
    # Save the full response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
