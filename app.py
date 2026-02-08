import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Teacher Profile & Planning Assistant", layout="wide")
st.title("Teacher Profile & Planning Assistant (Phase 1)")
st.caption("Paste your profile, choose a task, and generate classroom-ready output.")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it in Streamlit Secrets.")
    st.stop()

client = OpenAI()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1) Teacher Profile")
    profile_text = st.text_area(
        "Paste your Teacher AI-Ready Profile here (no student names).",
        height=240
    )

    st.subheader("2) Choose a task")
    task = st.radio(
        "Task type",
        ["Lesson / Unit Planning", "Assessment / Rubric", "Report Card Comment", "Weekly Planning & Organization"],
        index=0
    )

    st.subheader("3) Your request")
    user_request = st.text_area(
        "Describe what you want. Include grade, subject, timeframe, and outcomes if you have them.",
        height=160
    )

    generate = st.button("Generate", type="primary", use_container_width=True)

with col2:
    st.subheader("Output")
    output_box = st.empty()

SYSTEM = (
    "You are a teacher-support assistant. "
    "Use the teacher profile to tailor outputs (tone, format, constraints). "
    "Ask minimal clarifying questions only if essential. "
    "Never include student names or identifying information. "
    "If outcomes are requested but not provided, ask the teacher to paste them or list the outcome codes. "
    "Return clean, classroom-ready output with headings and bullet points."
)

def task_instructions(task_name: str) -> str:
    if task_name == "Lesson / Unit Planning":
        return "Create a lesson or unit plan aligned to provided outcomes. Include lesson flow, materials, and at least one assessment/check-for-understanding."
    if task_name == "Assessment / Rubric":
        return "Create an assessment or rubric. Include an answer key or sample responses when appropriate. Make it efficient to mark."
    if task_name == "Report Card Comment":
        return "Draft report card comment(s) in a professional, supportive, parent-friendly tone. Follow any constraints the teacher provides."
    return "Create a realistic weekly/cycle plan with top priorities, small doable steps, and a supportive tone. Avoid overload."

if generate:
    if not profile_text.strip():
        st.warning("Please paste a teacher profile first (even a short one).")
        st.stop()
    if not user_request.strip():
        st.warning("Please enter your request.")
        st.stop()

    prompt = f"""TEACHER PROFILE:
{profile_text}

TASK TYPE:
{task}

TASK INSTRUCTIONS:
{task_instructions(task)}

REQUEST:
{user_request}
"""

    with st.spinner("Generating..."):
        resp = client.responses.create(
            model="gpt-5",
            input=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
        )

        text_out = ""
        for item in resp.output:
            if item.type == "message":
                for c in item.content:
                    if c.type == "output_text":
                        text_out += c.text

        output_box.markdown(text_out if text_out.strip() else "No text output received. Try again with more detail.")
