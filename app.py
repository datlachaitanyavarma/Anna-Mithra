import streamlit as st
import datetime
import os
import json
import smtplib
from email.message import EmailMessage

# --- EMAIL CONFIGURATION ---
EMAIL_USER = "AnnaMithra.alert@gmail.com"
EMAIL_PASS = "uoqisnadymhiyiqy"

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except:
        return False

# --- SETUP ---
st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")
DB_FILE = "database.json"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": [{"username": "Admin", "password": "5979", "role": "Admin Portal", "mobile": "Admin", "email": ""}], "donations": [], "fund_requests": [], "fund_transactions": []}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- MAIN PAGE ---
if not st.session_state.logged_in:
    st.title("Welcome to Annamithra 🤝")
    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with auth_tab1:
        log_user = st.text_input("Username")
        log_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            for u in st.session_state.db["users"]:
                if u["username"].lower() == log_user.lower() and u["password"] == log_pass:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u["username"]
                    st.session_state.current_role = u["role"]
                    st.rerun()
    with auth_tab2:
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_mobile = st.text_input("Mobile")
        new_email = st.text_input("Email")
        new_role = st.selectbox("Role", ["Donor (Individual/Hotel)", "NGO / Orphanage"])
        if st.button("Register"):
            st.session_state.db["users"].append({"username": new_user, "password": new_pass, "role": new_role, "mobile": new_mobile, "email": new_email})
            save_data(st.session_state.db)
            st.success("Registered!")
else:
    # DASHBOARD LOGIC
    if st.session_state.current_role == "Donor (Individual/Hotel)":
        with st.form("donation_form"):
            donor_email = st.text_input("Your Email (For Confirmation)")
            food_items = st.text_area("Food Items")
            location = st.text_input("Location")
            ngo_email = st.text_input("NGO Email (For Alert)")
            if st.form_submit_button("Submit"):
                st.session_state.db["donations"].append({"donor": st.session_state.current_user, "items": food_items, "status": "Available"})
                save_data(st.session_state.db)
                send_email(ngo_email, "🚨 New Food Alert", f"Food from {st.session_state.current_user}: {food_items}")
                send_email(donor_email, "🙏 Thank You!", "Donation received!")
                st.success("✅ Success!")
    
    elif st.session_state.current_role == "NGO / Orphanage":
        st.subheader("Available Food")
        for d in st.session_state.db["donations"]:
            st.write(f"{d['items']} - {d['status']}")
            
    elif st.session_state.current_role == "Admin Portal":
        st.subheader("Admin Panel")
        st.write(st.session_state.db)
            
