import streamlit as st
import pandas as pd
import datetime
import os

# Define MBI-SS questions
MBI_SS_QUESTIONS = {
    "Emotional Exhaustion": [
        "I feel emotionally drained by my studies.",
        "I feel used up at the end of a day at university.",
        "I feel tired when I get up in the morning and have to face another day at university.",
        "Attending classes all day is really a strain for me.",
        "I feel burned out from my studies."
    ],
    "Cynicism": [
        "I have become less interested in my studies since my enrollment.",
        "I have become less enthusiastic about my studies.",
        "I have become more cynical about the potential usefulness of my studies.",
        "I doubt the significance of my studies."
    ],
    "Academic Efficacy": [
        "I can effectively solve the problems that arise in my studies.",
        "I feel I am making an effective contribution in the classes I attend.",
        "In my opinion, I am a good student.",
        "I have accomplished many worthwhile things in my studies.",
        "While at university, I feel confident that I am effective at getting things done.",
        "I feel exhilarated when I accomplish something at the university."
    ]
}

# Thresholds for burnout classification
THRESHOLDS = {
    "Emotional Exhaustion": 20,
    "Cynicism": 17,
    "Academic Efficacy": 18  # Lower than this = burnout risk
}

# Web App UI
st.title("MBI-SS Burnout Assessment")

st.write("This study aims to assess student burnout using the Maslach Burnout Inventory-Student Survey (MBI-SS). Please answer honestly. Your responses are confidential.")

# Consent checkbox
consent = st.checkbox("I confirm that I am at least 18 years old and I consent to participate in this study. I understand that my responses and any uploaded media may be used for academic research purposes in accordance with ethical research standards.")

if not consent:
    st.warning("You must consent to participate in the study to proceed.")
    st.stop()

# Optional image upload
uploaded_image = st.file_uploader("(Optional) Upload a screenshot or image of a recent social media post you'd like to include:", type=["jpg", "jpeg", "png"])

st.write("Please respond to the following questions based on how often you feel this way. (0 = Never, 6 = Always)")

responses = {}

# Input form
with st.form("mbi_form"):
    for category, questions in MBI_SS_QUESTIONS.items():
        st.subheader(category)
        responses[category] = []
        for q in questions:
            response = st.slider(q, 0, 6, key=q)
            responses[category].append(response)
    submitted = st.form_submit_button("Submit")

if submitted:
    # Reverse score Academic Efficacy responses
    ae_scores = [6 - val for val in responses["Academic Efficacy"]]

    # Score each category
    scores = {
        "Emotional Exhaustion": sum(responses["Emotional Exhaustion"]),
        "Cynicism": sum(responses["Cynicism"]),
        "Academic Efficacy": sum(ae_scores)
    }

    # Determine burnout level
    if scores["Emotional Exhaustion"] > 20 and scores["Cynicism"] > 17 and scores["Academic Efficacy"] < 18:
        classification = "High Burnout"
    elif 15 <= scores["Emotional Exhaustion"] <= 20 or 13 <= scores["Cynicism"] <= 17:
        classification = "Moderate Burnout"
    elif scores["Emotional Exhaustion"] < 15 and scores["Cynicism"] < 12 and scores["Academic Efficacy"] > 20:
        classification = "Low Burnout"
    else:
        classification = "Borderline/Undefined Burnout"

    # Display results
    st.markdown("### Results")
    st.write(f"**Emotional Exhaustion Score:** {scores['Emotional Exhaustion']} (High if > 20)")
    st.write(f"**Cynicism Score:** {scores['Cynicism']} (High if > 17)")
    st.write(f"**Academic Efficacy Score (Reverse Scored):** {scores['Academic Efficacy']} (Low if < 18)")
    st.write(f"### 🔹 Burnout Classification: **{classification}**")

    # Save responses to CSV
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    record = {
        "Timestamp": timestamp,
        "Emotional Exhaustion": scores['Emotional Exhaustion'],
        "Cynicism": scores['Cynicism'],
        "Academic Efficacy": scores['Academic Efficacy'],
        "Classification": classification,
        "Image Provided": bool(uploaded_image)
    }
    df = pd.DataFrame([record])

    try:
        existing = pd.read_csv("mbi_results.csv")
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv("mbi_results.csv", index=False)
    st.success("Your responses have been saved.")

    # Save uploaded image to a folder if provided
    if uploaded_image:
        image_folder = "uploaded_images"
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join(image_folder, f"{timestamp}.png")
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        st.success(f"Image saved to: {image_path}")
