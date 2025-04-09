import re
import random
import string
import streamlit as st
from datetime import datetime
import pandas as pd
import os

HISTORY_FILE = "password_history.csv"
COMMON_PASSWORDS = ["password", "123456", "12345678", "1234", "qwerty", "letmein", "admin", "welcome", "password1", "12345"]

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["timestamp", "password", "strength"]).to_csv(HISTORY_FILE, index=False)

def load_password_history():
    try:
        return pd.read_csv(HISTORY_FILE)
    except:
        return pd.DataFrame(columns=["timestamp", "password", "strength"])

def save_to_history(password, strength):
    history = load_password_history()
    new_entry = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "password": password,
        "strength": strength
    }])
    history = pd.concat([history, new_entry], ignore_index=True)
    history.to_csv(HISTORY_FILE, index=False)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def check_password_strength(password):
    score = 0.0
    feedback = []
    is_blacklisted = False

    if password.lower() in COMMON_PASSWORDS or "password123" in password.lower():
        feedback.append("This password is blacklisted and extremely common.")
        is_blacklisted = True
        return 0, feedback, is_blacklisted  # Immediately return 0 with flag

    max_score = 4.5

    if len(password) >= 8:
        score += 1.0
    else:
        feedback.append("Password should be at least 8 characters long.")

    if re.search(r'[A-Z]', password):
        score += 0.5
    else:
        feedback.append("Add uppercase letters (A-Z).")

    if re.search(r'[a-z]', password):
        score += 0.5
    else:
        feedback.append("Add lowercase letters (a-z).")

    if re.search(r'[0-9]', password):
        score += 1.0
    else:
        feedback.append("Add numbers (0-9).")

    if re.search(r'[!@#$%^&*()_+{}\[\]:;,.<>?/\\|`~\-]', password):
        score += 1.5
    else:
        feedback.append("Add special characters (!@#$%^&*).")

    if re.search(r'(.)\1{2,}', password.lower()):
        feedback.append("Avoid repeating characters (aaa, 111).")

    if re.search(r'(123|abc|qwe)', password.lower()):
        feedback.append("Avoid common sequences (123, abc).")

    normalized_score = round((score / max_score) * 5)
    normalized_score = min(5, max(0, normalized_score))

    return normalized_score, feedback, is_blacklisted

def generate_strong_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    strong_special = '!@#$%^&*()_+{}:><?[]$%^&#*&'
    selected_sets = []

    if use_lower: selected_sets.append(string.ascii_lowercase)
    if use_upper: selected_sets.append(string.ascii_uppercase)
    if use_digits: selected_sets.append(string.digits)
    if use_special: selected_sets.append(strong_special)

    if not selected_sets:
        return "Please select at least one character type."

    password = [random.choice(char_set) for char_set in selected_sets]
    all_chars = ''.join(selected_sets)
    password += random.choices(all_chars, k=length - len(password))
    random.shuffle(password)

    return ''.join(password)

def get_strength_description(score):
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Moderate"
    else:
        return "Strong"

def main():
    st.set_page_config(page_title="Password Strength Meter", page_icon="🔒", layout="wide")
    st.markdown("""
<style>
input, div, label, .markdown-text-container {
    font-family: 'Times New Roman', Times, serif !important;
    font-weight: bold !important;
    font-size: 17px !important;
}
.main-heading {
    font-family: 'Times New Roman', serif;
    color: #0D47A1;
    font-size: 33px;
    font-weight: bold;
}
footer {
    position: fixed;
    bottom: 10px;
    left: 0;
    right: 0;
    text-align: center;
    font-family: 'Times New Roman', serif;
    font-size: 14px;
    color: gray;
}
.uzma {
    color: #E91E63 !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

    
    st.sidebar.title("🔧 Tools")
    app_mode = st.sidebar.radio("Choose Action:", ["🔍 Check Password", "🔐 Generate Password", "📜 View History"])

    st.markdown('<h1 style="font-family: Times New Roman; color: #0000FF; font-size: 33px; font-weight: bold;">Password Strength Meter</h1>', unsafe_allow_html=True)

    st.markdown("Check your password strength, generate secure passwords, and view history.")

    if app_mode == "🔍 Check Password":
        st.markdown('<h2 style="font-family: Times New Roman; color: #0000FF; font-size: 31px; font-weight: bold;">🔍 Check Password Strength</h2>', unsafe_allow_html=True)

        password = st.text_input("Enter your password", type="password", placeholder="Type or paste your password here...")

        if password:
            score, feedback, is_blacklisted = check_password_strength(password)
            strength = get_strength_description(score)
            save_to_history(password, strength)

            if is_blacklisted:
                st.error("❌ This password is blacklisted and extremely common. Please choose a more secure password.")
            else:
                # Change progress bar color dynamically
                if strength == "Weak":
                    bar_color = "#FF0000"
                elif strength == "Moderate":
                    bar_color = "#FFA500"
                else:
                    bar_color = "#32CD32"

                st.markdown(f"""
                    <style>
                    .stProgress > div > div > div > div {{
                        background-color: {bar_color} !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

                st.markdown("**Password Strength:**")
                st.progress(score / 5)

                if strength == "Strong":
                    st.success(f"✅ Strong (Score: {score}/5)")
                    st.info("Awesome! Your password is strong.")
                    st.balloons()
                elif strength == "Moderate":
                    st.warning(f"⚠️ Moderate (Score: {score}/5)")
                else:
                    st.error(f"❌ Weak (Score: {score}/5)")

                if score < 5 and feedback:
                    st.subheader("💡 Improvement Suggestions")
                    for tip in feedback:
                        st.markdown(f"- {tip}")
    

    elif app_mode == "🔐 Generate Password":
        st.markdown('<h2 style="font-family: Times New Roman; font-size: 31px; color: #0000FF;">🔐 Generate a Strong Password</h2>', unsafe_allow_html=True)

        pass_length = st.slider("Password length", 8, 32, 12)
        use_upper = st.checkbox("Include uppercase letters (A-Z)", True)
        use_lower = st.checkbox("Include lowercase letters (a-z)", True)
        use_digits = st.checkbox("Include digits (0-9)", True)
        use_special = st.checkbox("Include special characters (!@#$%^&*)", True)

        if st.button("✨ Generate Strong Password"):
            new_pass = generate_strong_password(pass_length, use_upper, use_lower, use_digits, use_special)
            st.code(new_pass, language="text")

            
            score, _, _ = check_password_strength(new_pass)
            if score == 5:
                st.success("✅ This password is STRONG (5/5). You're good to go!")

    elif app_mode == "📜 View History":
        st.markdown('<h2 style="font-family: Times New Roman; font-size: 31px; color: #0000FF;">📜 Password Check History</h2>', unsafe_allow_html=True)

        history = load_password_history()

        if not history.empty:
            display_history = history.copy()
            display_history['password'] = "••••••••"
            st.dataframe(display_history.sort_values("timestamp", ascending=False), hide_index=True, use_container_width=True)

            if st.button("🧹 Clear History", type="primary"):
                clear_history()
                st.success("Password history cleared!")
        else:
            st.info("No password history yet.")

    st.markdown("""
    <footer>
        © 2025 <strong>Password Strength Meter</strong> | Developed by <span class="uzma">Uzma Azam</span>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()






