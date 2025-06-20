import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ✅ Gemini API Configuration
genai.configure(api_key="AIzaSyBL0HLQ0VBeAXYyISxY8Y__MNvCKh_GHCU")
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# 🤖 Gemini Ask Function
def ask_gemini(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"

# ✅ Load Data
with open("branch_data.json", "r") as f:
    branch_data = json.load(f)

with open("weighted_branch_keywords.json", "r") as f:
    branch_keywords = json.load(f)

# 🧠 Branch Scoring
def get_weighted_branch_scores(interests, strengths, goal, branch_keywords):
    scores = {}
    weights = {"interest": 2, "strength": 1.5, "goal": 3}
    inputs = {
        "interest": [i.lower() for i in interests],
        "strength": [s.lower() for s in strengths],
        "goal": [goal.lower()] if goal else []
    }

    for branch, keywords in branch_keywords.items():
        score = 0
        matched_keywords = []
        for category, words in inputs.items():
            for word in words:
                if word in keywords:
                    score += weights[category]
                    matched_keywords.append(word)
        if score > 0:
            scores[branch] = {"score": score, "matched": list(set(matched_keywords))}

    return dict(sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True))

# 🔗 Display Resource Markdown Link
def display_resource(resource):
    name = resource.get("name", "Resource")
    link = resource.get("link", "")
    if link:
        return f'- [{name}]({link})'
    return f'- {name} (No link provided)'

# 🌐 Streamlit Page Config
st.set_page_config(page_title="Smart Branch Recommender", page_icon="🧠", layout="wide")

# 🧾 Header
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #4CAF50;'>🎓 Smart Branch Recommender</h1>
        <p>Your personalized AI counselor to guide you in choosing your perfect engineering branch!</p>
    </div>
    <hr style='border: 1px solid #eee;'>
""", unsafe_allow_html=True)

# 🔒 Disclaimer Message
st.markdown("""
<div style='background-color:#fff3cd; padding: 10px; border-radius: 8px; border: 1px solid #ffeeba; margin-top: -15px;'>
    <strong>⚠️ Note:</strong> This tool is intended for guidance and informational purposes only.
    The recommendations provided are based on user inputs and do not guarantee career success or outcomes.
</div>
""", unsafe_allow_html=True)

# 👤 User Input Section
with st.container():
    st.markdown("### 🧑‍🎓 Tell us about yourself")
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

# 🔍 Recommendation Logic
if st.button("🚀 Recommend My Branch"):
    scores = get_weighted_branch_scores(interests, strengths, goal, branch_keywords)

    if scores:
        st.success(f"Hi {name}! Based on your input, here are your top 2 branch suggestions:")
        top_recommendations = dict(list(scores.items())[:2])

        for branch, data in top_recommendations.items():
            branch_info = branch_data[branch]
            st.markdown(f"### ✅ {branch} - {branch_info['title']}")
            st.write(f"**Match Score:** {data['score']}")
            st.write(f"**Matched on:** {', '.join(data['matched'])}")
            st.write(f"**Why?** {branch_info['ideal_for']}")
            st.write(f"**Future Scope:** {branch_info['future_scope']}")
            st.write(f"**Average Salary:** {branch_info['avg_salary']}")

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Core Subjects:**")
                for sub in branch_info['subjects']:
                    st.markdown(display_resource(sub), unsafe_allow_html=True)
            with col2:
                st.write("**Skills to Learn:**")
                for skill in branch_info['skills']:
                    st.markdown(display_resource(skill), unsafe_allow_html=True)

            st.write("**Job Roles:**")
            for role in branch_info.get("job_roles", []):
                if isinstance(role, dict):
                    st.markdown(f"#### 🧑‍💻 {role['title']}")
                    st.write(f"**Description:** {role['description']}")
                    st.write("**Responsibilities:**")
                    for task in role["responsibilities"]:
                        st.markdown(f"- {task}")
                    st.write(f"**Avg Salary:** {role['avg_salary']}")
                else:
                    st.markdown(f"- {role}")

            st.write("🎥 **YouTube Playlist:**")
            for link in branch_info.get("youtube", []):
                st.markdown(f"- [Watch Video]({link})")

            st.write("📘 **Extra Learning Resources:**")
            for res in branch_info.get("resources", []):
                st.markdown(display_resource(res), unsafe_allow_html=True)

            st.write("📍 **Roadmap PDF:**")
            st.markdown(f"- [Download Roadmap]({branch_info['roadmap']})")

            st.markdown("---")
    else:
        st.warning("No strong matches found. Try selecting more interests or strengths.")

# 📊 Charts
st.markdown("### 📊 Salary & Job Market Analysis")
salary_data = {
    "Branch": ["CSE", "ECE", "EEE", "Mechanical", "Civil", "Chemical", "Metallurgical"],
    "Average Salary (LPA)": [15, 10, 9, 8, 7, 8, 7],
    "Job Growth (2030) %": [95, 85, 75, 70, 60, 68, 55]
}
df = pd.DataFrame(salary_data)
col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(df, x="Branch", y="Average Salary (LPA)", color="Branch", title="Average Salary")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    fig2 = px.bar(df, x="Branch", y="Job Growth (2030) %", color="Branch", title="Job Market Growth")
    st.plotly_chart(fig2, use_container_width=True)

# 🤖 Chatbot Section
st.markdown("---")
st.header("💬 AI Career Counselor Chatbot")
user_input = st.text_input("🤔 Ask me anything about engineering careers")
if user_input:
    with st.spinner("Thinking..."):
        response = ask_gemini(user_input)
        st.success(response)
