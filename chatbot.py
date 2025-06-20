import streamlit as st
import google.generativeai as genai

# ✅ Your Gemini API key
GEMINI_API_KEY = "AIzaSyBL0HLQ0VBeAXYyISxY8Y__MNvCKh_GHCU"

# ✅ Configure the Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Streamlit UI
st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("💬 AI Career Counselor Chatbot")

# Chat input box
user_input = st.text_input("🤔 Ask me anything about engineering careers")

if user_input:
    with st.spinner("Thinking..."):
        try:
            response = model.generate_content(user_input)
            st.success(response.text)
        except Exception as e:
            st.error(f"❌ Error: {e}")
