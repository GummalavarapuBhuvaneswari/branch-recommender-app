import streamlit as st
import json
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# 👉 API Configuration
genai.configure(api_key=os.getenv("AIzaSyCScPGMp7JzCtSGFs-Ofn138O9KktSS-k4"))
model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")

# 👉 Load data
with open("branch_data.json", "r") as f:
    branch_data = json.load(f)
with open("weighted_branch_keywords.json", "r") as f:
    branch_keywords = json.load(f)

# 👉 Gemini Answer
def ask_gemini(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"

# 👉 Scoring
def get_weighted_branch_scores(interests, strengths, goal, keywords):
    scores = {}
    weights = {"interest": 2, "strength": 1.5, "goal": 3}
    inputs = {
        "interest": [i.lower() for i in interests],
        "strength": [s.lower() for s in strengths],
        "goal": [goal.lower()] if goal else []
    }
    for branch, branch_words in keywords.items():
        score = 0
        matched = []
        for category, words in inputs.items():
            for word in words:
                if word in branch_words:
                    score += weights[category]
                    matched.append(word)
        if score > 0:
            scores[branch] = {"score": score, "matched": list(set(matched))}
    return dict(sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True))

# 👉 Resource display
def display_resource(res):
    return f"- [{res['name']}]({res['link']})" if res.get("link") else f"- {res.get('name', 'Resource')}"

# 👉 Styling
st.set_page_config(
    page_title="Smart Branch Recommender", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit elements
hide_default = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
</style>
"""
st.markdown(hide_default, unsafe_allow_html=True)

st.markdown("""
<style>
body {
    background-color: #f4fdfd;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, h5 {
    color: #008B8B;
}
.stTextInput>div>div>input {
    background-color: white;
    border: 1px solid #008B8B;
    border-radius: 6px;
    color: #000;
}
.stTextInput>div>label {
    color: #008B8B;
    font-weight: bold;
}
.stMultiSelect>label {
    color: #008B8B;
    font-weight: bold;
}
.stButton>button {
    background-color: #008B8B;
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
.recommend-box {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 10px;
    border: 2px solid #008B8B20;
    margin-bottom: 20px;
}
.note-box {
    padding: 16px;
    border-radius: 10px;
    border: 2px solid #008B8B;
    margin-top: 10px;
    font-weight: 500;
    background: linear-gradient(145deg, rgba(0,139,139,0.15), rgba(0,139,139,0.05));
}
</style>
""", unsafe_allow_html=True)

# 👉 Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI Career Assistant. How can I help you with engineering careers today?"}
    ]

# 👉 Header
st.markdown("<h1 style='text-align: center;'>🎓 Smart Branch Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>An intelligent system to help you choose the best engineering branch!</p>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div class='note-box'>
    ⚠️ <strong>Note:</strong> This tool provides career guidance based on your inputs and does not guarantee outcomes or placements. Use it as a support for informed decision-making.
</div>
""", unsafe_allow_html=True)

# 👉 Inputs
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("👤 Your Name")
    interests = st.multiselect("💡 Your Interests", [
        "Coding", "Circuits", "Machines", "Design", "Chemistry",
        "Physics", "Research", "Environment"
    ])
with col2:
    strengths = st.multiselect("💪 Your Strengths", [
        "Problem Solving", "Creativity", "Math", "Communication", "Hands-on work"
    ])
    goal = st.text_input("🎯 Career Goal (Optional)")

# 👉 Recommendations
if st.button("🚀 Recommend My Branch"):
    scores = get_weighted_branch_scores(interests, strengths, goal, branch_keywords)
    if scores:
        st.success(f"Hi {name}! Based on your input, here are your top 2 branch suggestions:")
        top_recommendations = dict(list(scores.items())[:2])
        for branch, data in top_recommendations.items():
            info = branch_data[branch]
            st.markdown(f"<div class='recommend-box'>", unsafe_allow_html=True)
            st.markdown(f"### ✅ {branch} - {info['title']}")
            st.markdown(f"**Score:** {data['score']} | **Matched Keywords:** _{', '.join(data['matched'])}_")
            st.write(f"**Ideal For:** {info['ideal_for']}")
            st.write(f"**Future Scope:** {info['future_scope']}")
            st.write(f"**Average Salary:** {info['avg_salary']}")
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**📘 Core Subjects:**")
                for s in info["subjects"]:
                    st.markdown(display_resource(s), unsafe_allow_html=True)
            with cols[1]:
                st.markdown("**🛠 Skills to Learn:**")
                for s in info["skills"]:
                    st.markdown(display_resource(s), unsafe_allow_html=True)
            st.markdown("**💼 Job Roles:**")
            for role in info["job_roles"]:
                if isinstance(role, dict):
                    st.markdown(f"**{role['title']}**")
                    st.markdown(f"👉 _{role['description']}_")
                    st.markdown("**Responsibilities:**")
                    for r in role["responsibilities"]:
                        st.markdown(f"- {r}")
                    st.markdown(f"**💰 Avg Salary:** {role['avg_salary']}")
                else:
                    st.markdown(f"- {role}")
            st.markdown("**📺 YouTube Resources:**")
            for y in info["youtube"]:
                st.markdown(f"- [Watch]({y})")
            st.markdown("**📚 More Resources:**")
            for res in info["resources"]:
                st.markdown(display_resource(res), unsafe_allow_html=True)
            st.markdown(f"📍 [View Roadmap]({info['roadmap']})")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No strong match found. Try different selections.")

# 👉 Charts
st.markdown("### 📊 Career Insights")
chart_data = pd.DataFrame({
    "Branch": ["CSE", "ECE", "EEE", "Mechanical", "Civil", "Chemical", "Metallurgical"],
    "Average Salary (LPA)": [15, 10, 9, 8, 7, 8, 7],
    "Job Growth (%)": [95, 85, 75, 70, 60, 68, 55]
})
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(px.bar(chart_data, x="Branch", y="Average Salary (LPA)", color="Branch", title="💰 Average Salaries"), use_container_width=True)
with chart_col2:
    st.plotly_chart(px.bar(chart_data, x="Branch", y="Job Growth (%)", color="Branch", title="📈 Job Growth by 2030"), use_container_width=True)

# 👉 Chat Interface
st.markdown("---")
st.markdown("### 💬 AI Career Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and logic
if prompt := st.chat_input("Ask about engineering careers..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Combine conversation history for context
                conversation = "\n".join(
                    f"{m['role']}: {m['content']}" 
                    for m in st.session_state.messages
                )
                response = model.generate_content(conversation)
                full_response = response.text
            except Exception as e:
                full_response = f"⚠️ Error: {str(e)}"
            
            st.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 👉 Footer

