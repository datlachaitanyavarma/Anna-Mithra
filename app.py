import streamlit as st
import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")

# --- 2. DATABASE SIMULATION (SESSION STATE) ---
if 'donations' not in st.session_state:
    st.session_state.donations = []
# New database for NGO Fund/Emergency Requests
if 'fund_requests' not in st.session_state:
    st.session_state.fund_requests = [
        {"id": 1, "ngo": "Asha Orphanage", "reason": "Today's Lunch (Rice & Dal shortage)", "goal": 5000, "raised": 1500, "status": "Active"},
        {"id": 2, "ngo": "Helping Hands", "reason": "Monthly Groceries for 50 kids", "goal": 15000, "raised": 12000, "status": "Active"}
    ]

# --- 3. SIDEBAR: ROLE-BASED LOGIN SYSTEM ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align: center; color: #FF8C00;'>📦🤝🍲 Annamithra</h2>", unsafe_allow_html=True)
        
    st.markdown("### 🔐 Login Portal")
    # This acts as our login system
    role = st.selectbox("Select your Role to Login:", ["Donor (Individual/Hotel)", "NGO / Orphanage", "Admin Portal"])
    
    st.divider()
    st.write("📍 **Operating in:** Vepagunta, AP")
    st.write("📧 contact@annamithra.org")

# --- MAIN VISUAL BANNER ---
st.markdown('''
    <img src="https://images.pexels.com/photos/6995201/pexels-photo-6995201.jpeg" 
         alt="Donor giving food to NGO" 
         style="width: 100%; border-radius: 12px; margin-bottom: 20px; object-fit: cover; max-height: 250px;">
''', unsafe_allow_html=True)


# ==========================================
# ROLE 1: DONOR (INDIVIDUAL / HOTEL)
# ==========================================
if role == "Donor (Individual/Hotel)":
    st.title("🤝 Welcome, Donor!")
    st.write("Thank you for stepping up to end hunger. Choose how you want to help today.")
    
    tab1, tab2 = st.tabs(["🍽️ Donate Surplus Food", "💰 Help with Funds (NGO Needs)"])
    
    # Food Donation Tab
    with tab1:
        st.subheader("Donate Surplus Food from Functions/Hotels")
        with st.form("donation_form"):
            donor_type = st.selectbox("I am donating as:", ["Individual (Party/Function)", "Hotel / Restaurant"])
            donor_name = st.text_input("Name")
            food_type = st.radio("Food Type", ["Veg", "Non-Veg"], horizontal=True)
            col_a, col_b = st.columns(2)
            with col_a:
                servings = st.number_input("Number of Persons it can serve", min_value=1, step=1)
            with col_b:
                boxes = st.number_input("Number of Items / Boxes", min_value=1, step=1)
            location = st.text_input("Pickup Location / Address")
            
            if st.form_submit_button("Submit Food Details", use_container_width=True):
                if donor_name and location:
                    st.session_state.donations.append({
                        "id": len(st.session_state.donations) + 1,
                        "donor": donor_name, "type": food_type, "servings": servings,
                        "boxes": boxes, "location": location,
                        "time": datetime.datetime.now().strftime("%I:%M %p"), "status": "Available"
                    })
                    st.success("✅ Food details submitted! Nearby NGOs have been alerted.")
                else:
                    st.error("⚠️ Please fill all details.")

    # Fund Donation Tab (Crowdfunding)
    with tab2:
        st.subheader("Live Emergency Requirements from NGOs")
        active_requests = [r for r in st.session_state.fund_requests if r["status"] == "Active"]
        
        if not active_requests:
            st.info("No active fund requests right now.")
        else:
            for req in active_requests:
                with st.container(border=True):
                    st.markdown(f"#### 🏢 {req['ngo']}")
                    st.error(f"**Emergency:** {req['reason']}")
                    
                    # Calculate progress
                    progress_val = min(req['raised'] / req['goal'], 1.0)
                    st.progress(progress_val)
                    
                    st.markdown(f"**Raised:** ₹{req['raised']} / **Goal:** ₹{req['goal']}")
                    
                    # Simulated Payment
                    amount_to_donate = st.number_input(f"Amount to donate to {req['ngo']} (₹)", min_value=100, step=100, key=f"amt_{req['id']}")
                    if st.button(f"Donate ₹{amount_to_donate} Now", key=f"btn_{req['id']}"):
                        # Update the raised amount
                        req['raised'] += amount_to_donate
                        if req['raised'] >= req['goal']:
                            req['status'] = "Completed"
                            st.success(f"🎉 Goal reached for {req['ngo']}! Thank you!")
                        else:
                            st.success(f"💖 Successfully donated ₹{amount_to_donate} to {req['ngo']}!")
                        st.rerun()

# ==========================================
# ROLE 2: NGO / ORPHANAGE
# ==========================================
elif role == "NGO / Orphanage":
    st.title("🏢 NGO / Orphanage Dashboard")
    
    tab1, tab2 = st.tabs(["🔔 Accept Food Alerts", "📢 Post Emergency Fund Request"])
    
    with tab1:
        st.subheader("Available Food for Pickup")
        available_donations = [d for d in st.session_state.donations if d["status"] == "Available"]
        if not available_donations:
            st.info("No active food alerts at the moment.")
        else:
            for donation in available_donations:
                with st.container(border=True):
                    st.write(f"🚨 **From:** {donation['donor']} | 📍 **Location:** {donation['location']}")
                    st.write(f"🍱 **Details:** {donation['type']} | Serves {donation['servings']} people")
                    if st.button(f"Accept Request #{donation['id']}", key=f"acc_{donation['id']}", use_container_width=True):
                        donation['status'] = "Accepted"
                        st.success("🎉 You accepted this food request!")
                        st.rerun()

    with tab2:
        st.subheader("Raise a Request for Funds or Groceries")
        st.write("If you are short on food for a specific meal, request funds directly from donors.")
        with st.form("fund_form"):
            ngo_name = st.text_input("Your NGO Name")
            reason = st.text_input("Reason (e.g., Today's Lunch Shortage, Grocery Bill)")
            goal_amount = st.number_input("Target Amount Needed (₹)", min_value=500, step=500)
            
            if st.form_submit_button("Post Request to Public", use_container_width=True):
                if ngo_name and reason:
                    st.session_state.fund_requests.append({
                        "id": len(st.session_state.fund_requests) + 1,
                        "ngo": ngo_name, "reason": reason, 
                        "goal": goal_amount, "raised": 0, "status": "Active"
                    })
                    st.success("✅ Emergency request posted! Donors can now see this and contribute.")
                else:
                    st.error("⚠️ Fill all fields.")

# ==========================================
# ROLE 3: ADMIN PORTAL
# ==========================================
elif role == "Admin Portal":
    st.title("⚙️ Admin Control Panel")
    st.write("Platform-wide analytics and monitoring.")
    
    # Calculate stats
    total_food_requests = len(st.session_state.donations)
    total_funds_raised = sum([req['raised'] for req in st.session_state.fund_requests])
    total_goals = sum([req['goal'] for req in st.session_state.fund_requests])
    
    st.markdown("### 📊 Live Analytics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Food Donations", f"{total_food_requests} drives")
    col2.metric("Total Funds Raised", f"₹{total_funds_raised}")
    col3.metric("Platform Fund Target", f"₹{total_goals}")
    st.divider()
    
    st.subheader("Database Overview")
    st.write("**All Food Donations:**")
    st.json(st.session_state.donations)
    st.write("**All Fund Requests:**")
    st.json(st.session_state.fund_requests)
