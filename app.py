import streamlit as st
import datetime
import os
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")

DB_FILE = "database.json"

# --- 2. DATABASE SYSTEM ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = [{"username": "admin", "password": "123", "role": "Admin Portal"}]
                save_data(data)
            return data
    else:
        return {
            "users": [{"username": "admin", "password": "123", "role": "Admin Portal"}],
            "donations": [],
            "fund_requests": []
        }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align: center; color: #FF8C00;'>📦🤝🍲 Annamithra</h2>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.logged_in:
        st.success(f"👤 **{st.session_state.current_user}**")
        st.info(f"Role: {st.session_state.current_role}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.write("🔒 Please login.")
    st.divider()
    st.write("📍 Vepagunta, AP | 📧 contact@annamithra.org")

# --- 4. MAIN PAGE ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Welcome to Annamithra 🤝</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Register"])
        with auth_tab1:
            with st.container(border=True):
                log_user = st.text_input("Username")
                log_pass = st.text_input("Password", type="password")
                if st.button("Login", type="primary", use_container_width=True):
                    for u in st.session_state.db["users"]:
                        if u["username"] == log_user and u["password"] == log_pass:
                            st.session_state.logged_in = True
                            st.session_state.current_user = u["username"]
                            st.session_state.current_role = u["role"]
                            st.rerun()
        with auth_tab2:
            with st.container(border=True):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Create Password", type="password")
                new_role = st.selectbox("I am a:", ["Donor (Individual/Hotel)", "NGO / Orphanage"])
                if st.button("Create Account", type="primary", use_container_width=True):
                    st.session_state.db["users"].append({"username": new_user, "password": new_pass, "role": new_role})
                    save_data(st.session_state.db)
                    st.success("✅ Account created!")

else:
    # --- DONOR DASHBOARD ---
    if st.session_state.current_role == "Donor (Individual/Hotel)":
        st.title(f"👋 Welcome, {st.session_state.current_user}!")
        tab1, tab2 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs"])
        
        with tab1:
            st.subheader("Submit Surplus Food")
            with st.form("donation_form"):
                location = st.text_input("Pickup Address")
                if st.form_submit_button("Submit"):
                    st.session_state.db["donations"].append({"donor": st.session_state.current_user, "location": location, "status": "Available"})
                    save_data(st.session_state.db)
                    st.success("✅ Posted!")
        
        with tab2:
            st.subheader("Emergency NGO Requests")
            for req in [r for r in st.session_state.db["fund_requests"] if r["status"] == "Active"]:
                with st.expander(f"🏢 {req['ngo']} - Need: {req['reason']}", expanded=True):
                    st.write(f"Goal: ₹{req['goal']} | Raised: ₹{req['raised']}")
                    # PAYMENT SECTION FOR DONOR
                    st.info(f"**Payment Details:** UPI ID: `{req['upi']}`")
                    if req.get("qr_url"):
                        st.image(req['qr_url'], width=150, caption="Scan to Pay")
                    
                    amt = st.number_input("Donate (₹)", min_value=100, step=100, key=f"amt_{req['id']}")
                    if st.button(f"Donate ₹{amt}", key=f"btn_{req['id']}"):
                        req['raised'] += amt
                        save_data(st.session_state.db)
                        st.success("💖 Thank you!")
                        st.rerun()

    # --- NGO DASHBOARD ---
    elif st.session_state.current_role == "NGO / Orphanage":
        st.title(f"🏢 {st.session_state.current_user}")
        tab1, tab2 = st.tabs(["📢 Request Funds", "📂 My Requests"])
        
        with tab1:
            st.subheader("Post Emergency Need")
            with st.form("fund_form"):
                reason = st.text_input("Reason (e.g. Groceries)")
                goal = st.number_input("Target Amount (₹)", 500)
                upi = st.text_input("Your UPI ID")
                qr = st.text_input("QR Code Image URL (Optional)")
                if st.form_submit_button("Post Request"):
                    st.session_state.db["fund_requests"].append({
                        "id": len(st.session_state.db["fund_requests"]) + 1,
                        "ngo": st.session_state.current_user, "reason": reason, 
                        "goal": goal, "raised": 0, "status": "Active", 
                        "upi": upi, "qr_url": qr
                    })
                    save_data(st.session_state.db)
                    st.success("✅ Posted!")

        with tab2:
            for req in [r for r in st.session_state.db["fund_requests"] if r["ngo"] == st.session_state.current_user]:
                st.write(f"**Reason:** {req['reason']} | Raised: ₹{req['raised']}/{req['goal']}")

    elif st.session_state.current_role == "Admin Portal":
        st.title("⚙️ Admin Panel")
        st.dataframe(st.session_state.db["fund_requests"], use_container_width=True)
    
