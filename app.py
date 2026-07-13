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
                    if any(u["username"] == new_user for u in st.session_state.db["users"]):
                        st.error("Username already exists!")
                    elif new_user and new_pass:
                        st.session_state.db["users"].append({"username": new_user, "password": new_pass, "role": new_role})
                        save_data(st.session_state.db)
                        st.success("✅ Account created! You can now Login.")
                    else:
                        st.error("Please fill all fields.")

else:
    # --- DONOR DASHBOARD ---
    if st.session_state.current_role == "Donor (Individual/Hotel)":
        st.title(f"👋 Welcome, {st.session_state.current_user}!")
        tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📜 My History"])
        
        with tab1:
            st.subheader("Submit Surplus Food")
            
            # MOVED OUTSIDE THE FORM TO UPDATE LIVE
            st.info("👇 Select Food Category first, then fill the details in the box.")
            food_category = st.radio("Category of Food", ["Veg", "Non-Veg", "Both (Veg & Non-Veg)"], horizontal=True)
            
            with st.form("donation_form"):
                contact = st.text_input("Contact Number (Mandatory) *")
                food_items = st.text_area("What food items are you donating? (e.g., Rice, Dal, Chicken Curry) *")
                
                v_boxes = v_serves = nv_boxes = nv_serves = 0
                
                if food_category in ["Veg", "Both (Veg & Non-Veg)"]:
                    st.markdown("🟢 **Veg Details**")
                    v_boxes = st.number_input("Veg - No. of Boxes", min_value=0, step=1)
                    v_serves = st.number_input("Veg - Serves (Persons)", min_value=0, step=1)
                
                if food_category in ["Non-Veg", "Both (Veg & Non-Veg)"]:
                    st.markdown("🔴 **Non-Veg Details**")
                    nv_boxes = st.number_input("Non-Veg - No. of Boxes", min_value=0, step=1)
                    nv_serves = st.number_input("Non-Veg - Serves (Persons)", min_value=0, step=1)
                
                location = st.text_input("Pickup Address *")
                
                if st.form_submit_button("Submit Food Details"):
                    if not contact or not location or not food_items:
                        st.error("⚠️ Please fill Contact Number, Food Items, and Location!")
                    else:
                        st.session_state.db["donations"].append({
                            "id": len(st.session_state.db["donations"]) + 1,
                            "donor": st.session_state.current_user,
                            "contact": contact,
                            "items": food_items,
                            "category": food_category,
                            "veg_boxes": v_boxes, "veg_serves": v_serves,
                            "nv_boxes": nv_boxes, "nv_serves": nv_serves,
                            "location": location,
                            "time": datetime.datetime.now().strftime("%I:%M %p"),
                            "status": "Available"
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Food Details Posted Successfully!")
        
        with tab2:
            st.subheader("NGO Fund Requests")
            for req in st.session_state.db["fund_requests"]:
                if req.get("status") == "Active":
                    with st.expander(f"🏢 {req.get('ngo', 'NGO')} - Need: {req.get('reason', 'Help')}", expanded=True):
                        st.write(f"**Goal:** ₹{req.get('goal', 0)} | **Raised:** ₹{req.get('raised', 0)}")
                        
                        goal = req.get('goal', 1)
                        raised = req.get('raised', 0)
                        st.progress(min(raised / goal if goal > 0 else 0, 1.0))
                        
                        st.info(f"**Payment Details:** UPI ID: `{req.get('upi', 'N/A')}`")
                        if req.get("qr_url"):
                            st.image(req.get("qr_url"), width=150, caption="Scan to Pay")
                        
                        remaining = goal - raised
                        if remaining > 0:
                            st.write(f"*Only ₹{remaining} left to reach the goal!*")
                            min_donate = min(100, remaining)
                            amt = st.number_input("Donate (₹)", min_value=min_donate, max_value=remaining, step=min_donate, key=f"amt_{req.get('id', 0)}")
                            if st.button(f"Donate ₹{amt}", key=f"btn_{req.get('id', 0)}"):
                                req['raised'] = raised + amt
                                if req['raised'] >= goal:
                                    req['status'] = "Completed"
                                save_data(st.session_state.db)
                                st.success(f"💖 Thank you for your donation of ₹{amt}!")
                                st.rerun()
                
                elif req.get("status") == "Completed":
                    with st.expander(f"✅ FULFILLED: {req.get('ngo', 'NGO')} - {req.get('reason', 'Need')}", expanded=False):
                        st.success(f"Goal of ₹{req.get('goal', 0)} was successfully raised! Thank you.")
        
        with tab3:
            st.subheader("My Past Food Donations")
            my_donations = [d for d in st.session_state.db["donations"] if d.get("donor") == st.session_state.current_user]
            
            if not my_donations:
                st.info("You haven't made any food donations yet.")
            else:
                for d in reversed(my_donations):
                    with st.container(border=True):
                        st.write(f"📅 **{d.get('time', 'Unknown Time')}** | Status: **{d.get('status', 'Unknown')}**")
                        st.write(f"**Items:** {d.get('items', 'Not specified (Legacy Data)')}")
                        
                        v_serves = d.get('veg_serves', 0)
                        if v_serves > 0:
                            st.write(f"🟢 Veg: {d.get('veg_boxes', 0)} Boxes (Serves {v_serves})")
                        
                        nv_serves = d.get('nv_serves', 0)
                        if nv_serves > 0:
                            st.write(f"🔴 Non-Veg: {d.get('nv_boxes', 0)} Boxes (Serves {nv_serves})")

    # --- NGO DASHBOARD ---
    elif st.session_state.current_role == "NGO / Orphanage":
        st.title(f"🏢 {st.session_state.current_user}")
        tab1, tab2, tab3 = st.tabs(["🔔 Available Food", "📢 Request Funds", "📂 My Requests"])
        
        with tab1:
            st.subheader("Live Food Alerts")
            available = [d for d in st.session_state.db["donations"] if d.get("status") == "Available"]
            if not available:
                st.info("No active food donations right now.")
            else:
                for idx, d in enumerate(available):
                    with st.container(border=True):
                        st.write(f"🚨 **From:** {d.get('donor', 'Unknown')} | 📞 **Contact:** {d.get('contact', 'N/A')}")
                        st.write(f"📍 **Address:** {d.get('location', 'N/A')}")
                        st.write(f"🍲 **Items:** {d.get('items', 'Not specified (Legacy Data)')}")
                        st.write(f"**Category:** {d.get('category', 'N/A')} | Veg Serves: {d.get('veg_serves', 0)} | Non-Veg Serves: {d.get('nv_serves', 0)}")
                        
                        safe_id = d.get('id', f"legacy_{idx}")
                        
                        if st.button(f"Accept Pickup", key=f"acc_{safe_id}", use_container_width=True):
                            d['status'] = f"Accepted by {st.session_state.current_user}"
                            save_data(st.session_state.db)
                            st.success("🎉 Accepted! Please call the donor to arrange pickup.")
                            st.rerun()

        with tab2:
            st.subheader("Post Emergency Need")
            with st.form("fund_form"):
                reason = st.text_input("Reason (e.g. Groceries)")
                goal = st.number_input("Target Amount (₹)", min_value=500, step=500)
                upi = st.text_input("Your UPI ID")
                qr = st.text_input("QR Code Image URL (Optional)")
                if st.form_submit_button("Post Request"):
                    if reason and upi:
                        st.session_state.db["fund_requests"].append({
                            "id": len(st.session_state.db["fund_requests"]) + 1,
                            "ngo": st.session_state.current_user, "reason": reason, 
                            "goal": goal, "raised": 0, "status": "Active", 
                            "upi": upi, "qr_url": qr
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Posted!")
                    else:
                        st.error("Please provide Reason and UPI ID.")

        with tab3:
            st.subheader("My Active & Completed Requests")
            my_reqs = [r for r in st.session_state.db["fund_requests"] if r.get("ngo") == st.session_state.current_user]
            for req in reversed(my_reqs):
                with st.container(border=True):
                    st.write(f"**Reason:** {req.get('reason', 'N/A')}")
                    st.write(f"Status: **{req.get('status', 'Unknown')}** | Raised: ₹{req.get('raised', 0)}/₹{req.get('goal', 0)}")
                    
                    goal = req.get('goal', 1)
                    raised = req.get('raised', 0)
                    st.progress(min(raised / goal if goal > 0 else 0, 1.0))

    # --- ADMIN DASHBOARD ---
    elif st.session_state.current_role == "Admin Portal":
        st.title("⚙️ Admin Panel")
        st.write("Complete System Overview")
        
        st.subheader("Users")
        st.dataframe(st.session_state.db["users"], use_container_width=True)
        st.subheader("Food Donations")
        st.dataframe(st.session_state.db["donations"], use_container_width=True)
        st.subheader("Fund Requests")
        st.dataframe(st.session_state.db["fund_requests"], use_container_width=True)
                        
