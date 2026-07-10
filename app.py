import streamlit as st
import datetime
import os
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")

DB_FILE = "database.json"

# --- 2. SECURE DATABASE SYSTEM ---
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

# Session states for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""

# --- 3. SIDEBAR (ONLY FOR PROFILE & LOGOUT ONCE LOGGED IN) ---
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
            st.session_state.current_user = ""
            st.session_state.current_role = ""
            st.rerun()
    else:
        st.write("🔒 Please login to access your dashboard.")
            
    st.divider()
    st.write("📍 **Operating in:** Vepagunta, AP")
    st.write("📧 contact@annamithra.org")


# --- 4. MAIN PAGE: NEAT LOGIN & PERSONALIZED DASHBOARDS ---

if not st.session_state.logged_in:
    # NEAT MAIN PAGE LOGIN SCREEN
    st.markdown("<h1 style='text-align: center;'>Welcome to Annamithra 🤝</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Connecting surplus food with NGOs and Orphanages.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1]) # Centers the login box perfectly
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login to Account", "📝 Register New Account"])
        
        with auth_tab1:
            with st.container(border=True):
                log_user = st.text_input("Username")
                log_pass = st.text_input("Password", type="password")
                if st.button("Login", type="primary", use_container_width=True):
                    user_found = False
                    for u in st.session_state.db["users"]:
                        if u["username"] == log_user and u["password"] == log_pass:
                            st.session_state.logged_in = True
                            st.session_state.current_user = u["username"]
                            st.session_state.current_role = u["role"]
                            user_found = True
                            st.rerun()
                    if not user_found:
                        st.error("Invalid Username or Password!")
                        
        with auth_tab2:
            with st.container(border=True):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Create Password", type="password")
                new_role = st.selectbox("I am a:", ["Donor (Individual/Hotel)", "NGO / Orphanage"])
                if st.button("Create Account", type="primary", use_container_width=True):
                    if any(u["username"] == new_user for u in st.session_state.db["users"]):
                        st.error("Username already taken! Try another.")
                    elif new_user and new_pass:
                        st.session_state.db["users"].append({
                            "username": new_user, "password": new_pass, "role": new_role
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Account created! Please switch to Login tab.")
                    else:
                        st.error("Please fill all fields.")

else:
    # ==========================================
    # ROLE 1: DONOR PERSONALIZED DASHBOARD
    # ==========================================
    if st.session_state.current_role == "Donor (Individual/Hotel)":
        st.title(f"👋 Hello, {st.session_state.current_user}!")
        
        tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📂 My Donation History"])
        
        with tab1:
            st.subheader("Submit Surplus Food Details")
            with st.form("donation_form"):
                food_type = st.radio("Food Type", ["Veg", "Non-Veg"], horizontal=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    servings = st.number_input("Serves (Persons)", min_value=1, step=1)
                with col_b:
                    boxes = st.number_input("Items / Boxes", min_value=1, step=1)
                location = st.text_input("Pickup Address")
                
                if st.form_submit_button("Alert Nearby NGOs", use_container_width=True):
                    if location:
                        new_donation = {
                            "id": len(st.session_state.db["donations"]) + 1,
                            "donor": st.session_state.current_user,
                            "type": food_type, "servings": servings, "boxes": boxes, 
                            "location": location, "time": datetime.datetime.now().strftime("%I:%M %p"), "status": "Available"
                        }
                        st.session_state.db["donations"].append(new_donation)
                        save_data(st.session_state.db)
                        st.success("✅ Food details posted successfully!")
                    else:
                        st.error("⚠️ Please provide location.")

        with tab2:
            st.subheader("Active NGO Requests")
            active_requests = [r for r in st.session_state.db["fund_requests"] if r["status"] == "Active"]
            if not active_requests:
                st.info("No active requests right now.")
            else:
                for req in active_requests:
                    with st.container(border=True):
                        st.write(f"**🏢 {req['ngo']}** needs funds for: {req['reason']}")
                        st.progress(min(req['raised'] / req['goal'], 1.0))
                        st.write(f"₹{req['raised']} raised of ₹{req['goal']} goal")
                        
                        amt = st.number_input(f"Donate (₹)", min_value=100, step=100, key=f"amt_{req['id']}")
                        if st.button(f"Donate ₹{amt}", key=f"btn_{req['id']}"):
                            for db_req in st.session_state.db["fund_requests"]:
                                if db_req["id"] == req["id"]:
                                    db_req['raised'] += amt
                                    if db_req['raised'] >= db_req['goal']:
                                        db_req['status'] = "Completed"
                                    save_data(st.session_state.db)
                            st.success(f"💖 Donated ₹{amt} to {req['ngo']}!")
                            st.rerun()

        # PERSONALIZED VIEW FOR DONOR
        with tab3:
            st.subheader("My Past Contributions")
            my_donations = [d for d in st.session_state.db["donations"] if d["donor"] == st.session_state.current_user]
            if not my_donations:
                st.info("You haven't made any donations yet.")
            else:
                for d in reversed(my_donations): # Shows latest first
                    st.write(f"- 🍱 {d['type']} food for {d['servings']} people at {d['location']} (Status: **{d['status']}**)")


    # ==========================================
    # ROLE 2: NGO PERSONALIZED DASHBOARD
    # ==========================================
    elif st.session_state.current_role == "NGO / Orphanage":
        st.title(f"🏢 {st.session_state.current_user} Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["🔔 Available Food", "📢 Request Funds", "📂 My Fund Requests"])
        
        with tab1:
            st.subheader("Available Food Alerts")
            available_donations = [d for d in st.session_state.db["donations"] if d["status"] == "Available"]
            if not available_donations:
                st.info("No food alerts right now.")
            else:
                for donation in available_donations:
                    with st.container(border=True):
                        st.write(f"🚨 **From:** {donation['donor']} | 📍 **Location:** {donation['location']}")
                        st.write(f"🍱 Serves {donation['servings']} people ({donation['type']})")
                        if st.button(f"Accept Pickup #{donation['id']}", key=f"acc_{donation['id']}", use_container_width=True):
                            for db_don in st.session_state.db["donations"]:
                                if db_don["id"] == donation["id"]:
                                    db_don['status'] = f"Accepted by {st.session_state.current_user}"
                                    save_data(st.session_state.db)
                            st.success("🎉 Food pickup accepted!")
                            st.rerun()

        with tab2:
            st.subheader("Post a Need (Funds/Groceries)")
            with st.form("fund_form"):
                reason = st.text_input("Emergency Reason (e.g., Groceries)")
                goal_amount = st.number_input("Target Amount (₹)", min_value=500, step=500)
                if st.form_submit_button("Submit Request", use_container_width=True):
                    if reason:
                        new_req = {
                            "id": len(st.session_state.db["fund_requests"]) + 1,
                            "ngo": st.session_state.current_user,
                            "reason": reason, "goal": goal_amount, "raised": 0, "status": "Active"
                        }
                        st.session_state.db["fund_requests"].append(new_req)
                        save_data(st.session_state.db)
                        st.success("✅ Request posted to donors!")
                    else:
                        st.error("⚠️ Fill all fields.")
                        
        # PERSONALIZED VIEW FOR NGO
        with tab3:
            st.subheader("My Fund Requests & Progress")
            my_requests = [r for r in st.session_state.db["fund_requests"] if r["ngo"] == st.session_state.current_user]
            if not my_requests:
                st.info("You haven't posted any requests.")
            else:
                for req in reversed(my_requests):
                    with st.container(border=True):
                        st.write(f"**Reason:** {req['reason']}")
                        st.progress(min(req['raised'] / req['goal'], 1.0))
                        st.write(f"Raised: ₹{req['raised']} / Goal: ₹{req['goal']} (Status: **{req['status']}**)")


    # ==========================================
    # ROLE 3: ADMIN PORTAL
    # ==========================================
    elif st.session_state.current_role == "Admin Portal":
        st.title("⚙️ Admin Control Panel")
        st.write("Complete Database Overview")
        
        st.subheader("Registered Users")
        st.json(st.session_state.db["users"])
        st.subheader("All Food Donations")
        st.json(st.session_state.db["donations"])
        st.subheader("All Fund Requests")
        st.json(st.session_state.db["fund_requests"])
                                         
