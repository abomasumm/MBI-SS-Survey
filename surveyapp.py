import streamlit as st
import pandas as pd
import datetime

# Define MBI-SS questions
MBI_SS_QUESTIONS = {
    "Emotional Exhaustion": [
        "I feel emotionally drained by my studies.",
        "I feel used up at the end of a day at university.",
        "I feel tired when I get up in the morning and have to face another day at university.",
        "Studying or attending class is a strain for me.",
        "I feel burned out from my studies."
    ],
    "Cynicism": [
        "I have become less interested in my studies since my enrollment at university.",
        "I have become more cynical about the potential usefulness of my studies.",
        "I doubt the significance of my studies.",
        "I just want to get my degree and get out."
    ],
    "Academic Efficacy": [
        "I can effectively solve the problems that arise in my studies.",
        "I believe that I make an effective contribution to the classes that I attend.",
        "In my opinion, I am a good student.",
        "I feel stimulated when I achieve my study goals.",
        "During class I feel confident that I am effective in getting things done.",
        "I am proud of my academic accomplishments."
    ]
}

# Thresholds for burnout classification
THRESHOLDS = {
    "Emotional Exhaustion": 14,
    "Cynicism": 6,
    "Academic Efficacy": 18  # Lower than this = burnout risk
}

# Web App UI
st.title("MBI-SS Burnout Assessment")
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
    # Score each category
    scores = {cat: sum(responses[cat]) for cat in responses}

    # Determine burnout
    ee_burn = scores["Emotional Exhaustion"] >= THRESHOLDS["Emotional Exhaustion"]
    cy_burn = scores["Cynicism"] >= THRESHOLDS["Cynicism"]
    ae_burn = scores["Academic Efficacy"] <= THRESHOLDS["Academic Efficacy"]

    if (ee_burn and cy_burn) or ae_burn:
        classification = "Burned Out"
    else:
        classification = "Not Burned Out"

    # Display results
    st.markdown("### Results")
    st.write(f"**Emotional Exhaustion Score:** {scores['Emotional Exhaustion']} (Threshold: ≥14)")
    st.write(f"**Cynicism Score:** {scores['Cynicism']} (Threshold: ≥6)")
    st.write(f"**Academic Efficacy Score:** {scores['Academic Efficacy']} (Threshold: ≤18)")
    st.write(f"### 🔹 Burnout Classification: **{classification}**")

    # Save responses to CSV
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "Timestamp": timestamp,
        "Emotional Exhaustion": scores['Emotional Exhaustion'],
        "Cynicism": scores['Cynicism'],
        "Academic Efficacy": scores['Academic Efficacy'],
        "Classification": classification
    }
    df = pd.DataFrame([record])

    try:
        existing = pd.read_csv("mbi_results.csv")
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv("mbi_results.csv", index=False)
    st.success("Your responses have been saved.")
