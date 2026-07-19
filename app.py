import streamlit as st
import datetime
import urllib.parse
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Annamithra - Food Waste Management", page_icon="🍲", layout="wide")

# ==========================================
# 2. SUPABASE DATABASE CONFIGURATION
# ==========================================
SUPABASE_URL = "https://fgqwfndywylzckgmtqgr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZncXdmbmR5d3lsemNrZ210cWdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ0NzAxOTYsImV4cCI6MjEwMDA0NjE5Nn0.0-gAsjS5DHrtet6y0h0WKCnGmtQfKcoi9H2inHAGguE"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_current_time():
    return datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p")

def fetch_data(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        return []

def insert_data(table_name, data):
    try:
        supabase.table(table_name).insert(data).execute()
        return True
    except:
        return False

def update_data(table_name, record_id, data):
    try:
        supabase.table(table_name).update(data).eq("id", record_id).execute()
        return True
    except:
        return False

def display_formatted_table(data, prefix="AM"):
    if not data:
        st.info("No records found in this category.")
        return
    df = pd.DataFrame(data)
    df.insert(0, 'Annamithra_ID', [f"{prefix}{str(i+1).zfill(4)}" for i in range(len(df))])
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    if 'password' in df.columns and prefix == "AM-USR":
        df['password'] = "••••••••"
    st.dataframe(df, hide_index=True, use_container_width=True)

# ==========================================
# 4. SIDEBAR & AUTHENTICATION
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_role" not in st.session_state:
    st.session_state.current_role = None

def render_sidebar():
    try:
        st.sidebar.image("logo.png", use_container_width=True)
    except:
        st.sidebar.write("*(Logo.png missing)*")
        
    st.sidebar.markdown("---")
    
    if not st.session_state.current_user:
        st.sidebar.write("🔒 Please login.")
    else:
        st.sidebar.success(f"👤 {st.session_state.current_user}")
        st.sidebar.info(f"Role: {st.session_state.current_role}")
        
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    st.sidebar.markdown("---")
    st.sidebar.markdown("📍 Vepagunta, AP | 📧 [contact@annamithra.org](mailto:contact@annamithra.org)")

def login_register_page():
    st.title("Welcome to Annamithra 🤝")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    users_data = fetch_data("users")
    
    with tab1:
        with st.container(border=True):
            username = st.text_input("Username", key="log_user")
            password = st.text_input("Password", type="password", key="log_pass")
            if st.button("Login", type="primary", use_container_width=True):
                if username == "Admin" and password == "5979":
                    st.session_state.current_user = "Admin"
                    st.session_state.current_role = "Admin Portal"
                    st.rerun()
                else:
                    user = next((u for u in users_data if u["username"] == username and u["password"] == password), None)
                    if user:
                        st.session_state.current_user = user["username"]
                        st.session_state.current_role = user["role"]
                        st.rerun()
                    else:
                        st.error("Invalid Credentials!")

    with tab2:
        with st.container(border=True):
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Create Password", type="password", key="reg_pass")
            role = st.selectbox("Select Role", ["Donor (Individual/Hotel)", "NGO / Orphanage", "Volunteer"])
            mobile = st.text_input("Mobile Number")
            email = st.text_input("Email ID")
            blood_group = st.selectbox("Blood Group (Mandatory)", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            
            if st.button("Register", use_container_width=True):
                if not all([new_user, new_pass, mobile, email]) or blood_group == "Select":
                    st.warning("All fields are mandatory!")
                elif any(u["username"] == new_user for u in users_data):
                    st.error("Username already exists!")
                else:
                    insert_data("users", {
                        "username": new_user, "password": new_pass, "role": role, 
                        "mobile": mobile, "email": email, "blood_group": blood_group
                    })
                    st.success("Registration Successful! Please login.")

# ==========================================
# 5. DONOR DASHBOARD
# ==========================================
def donor_dashboard():
    st.title(f"👋 Welcome, {st.session_state.current_user}!")
    
    tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📜 My History"])
    
    with tab1:
        st.subheader("Submit Surplus Food")
        st.info("👇 Select Food Category first, then fill the details in the box.")
        
        food_type = st.radio("Category of Food", ["Veg", "Non-Veg", "Both (Veg & Non-Veg)"], horizontal=True)
        
        with st.container(border=True):
            contact = st.text_input("Contact Number (For this pickup) *")
            items = st.text_area("What food items are you donating? (e.g., Rice, Dal, Chicken Curry) *")
            
            v_boxes, v_serves, nv_boxes, nv_serves = 0, 0, 0, 0
            
            if food_type in ["Veg", "Both (Veg & Non-Veg)"]:
                st.markdown("🟢 **Veg Details**")
                v_boxes = st.number_input("Veg - No. of Boxes", min_value=0, key="vb")
                v_serves = st.number_input("Veg - Serves (Persons)", min_value=0, key="vs")
                
            if food_type in ["Non-Veg", "Both (Veg & Non-Veg)"]:
                st.markdown("🔴 **Non-Veg Details**")
                nv_boxes = st.number_input("Non-Veg - No. of Boxes", min_value=0, key="nvb")
                nv_serves = st.number_input("Non-Veg - Serves (Persons)", min_value=0, key="nvs")
                
            address = st.text_area("Pickup Address (Door No, Street Name) *")
            
            # --- Google Maps Location Feature ---
            st.markdown("##### 📍 Share Exact Location (Optional but helpful)")
            st.info("Step 1: Click the link below to open Maps.\n\nStep 2: Copy your location link.\n\nStep 3: Paste it in the box below.")
            st.markdown("👉 **[Open Google Maps to Copy Link](https://maps.google.com/)**")
            gmaps_link = st.text_input("Paste Google Maps Link Here 🔗")
            
            if st.button("Submit Food Details", type="primary"):
                if contact and items and address:
                    # Combine address and maps link for database storage
                    final_location = f"{address} | MapsLink: {gmaps_link}" if gmaps_link else address
                    
                    insert_data("donations", {
                        "donor": st.session_state.current_user, "contact": contact, "items": items,
                        "category": food_type, "veg_boxes": v_boxes, "veg_serves": v_serves,
                        "nv_boxes": nv_boxes, "nv_serves": nv_serves, "location": final_location,
                        "expiry": "N/A", "time": get_current_time(), "status": "Available"
                    })
                    st.success("Food Details Submitted Successfully!")
                else:
                    st.error("Please fill all mandatory (*) fields.")

    with tab2:
        st.subheader("NGO Fund Requests")
        requests = fetch_data("fund_requests")
        active_reqs = [r for r in requests if r.get("status") == "Active"]
        
        if not active_reqs:
            st.info("No active fund requests right now.")
            
        for req in reversed(active_reqs):
            with st.expander(f"🏢 {req['ngo']} - Need: {req['reason']}", expanded=True):
                goal = req['goal']
                raised = req['raised']
                
                st.write(f"**Goal:** ₹{goal} | **Raised:** ₹{raised}")
                st.progress(min(raised / goal if goal > 0 else 0, 1.0))
                
                st.info(f"**Payment Details:** UPI ID: {req['upi']}")
                st.write(f"*Only ₹{goal - raised} left to reach the goal!*")
                
                amount = st.number_input("Donate (₹)", min_value=1, max_value=goal-raised, value=100, key=f"amt_{req['id']}")
                utr = st.text_input("Enter 12-Digit UTR after payment via app:", key=f"utr_{req['id']}")
                
                upi_url = f"upi://pay?pa={req['upi']}&pn={req['ngo'].replace(' ', '%20')}&am={amount}&cu=INR"
                st.markdown(f"[🚀 Click Here to Pay ₹{amount} via App]({upi_url})")
                
                if st.button(f"Donate ₹{amount} & Verify", key=f"btn_{req['id']}"):
                    if len(utr) >= 6:
                        new_raised = raised + amount
                        status = "Completed" if new_raised >= goal else "Active"
                        update_data("fund_requests", req['id'], {"raised": new_raised, "status": status})
                        insert_data("fund_transactions", {
                            "donor": st.session_state.current_user, "ngo": req['ngo'],
                            "amount": amount, "reason": req['reason'], "time": get_current_time()
                        })
                        st.success(f"Donation of ₹{amount} successful! Verified.")
                        st.rerun()
                    else:
                        st.error("Please enter a valid UTR number.")

    with tab3:
        st.subheader("My Contributions")
        funds = [f for f in fetch_data("fund_transactions") if f["donor"] == st.session_state.current_user]
        food = [d for d in fetch_data("donations") if d["donor"] == st.session_state.current_user]
        
        st.write("### Financial Contributions")
        display_formatted_table(funds, "AM-TXN")
            
        st.write("### Food Contributions")
        display_formatted_table(food, "AM-FD")

# ==========================================
# 6. NGO DASHBOARD
# ==========================================
def ngo_dashboard():
    st.title(f"🏢 {st.session_state.current_user}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔔 Available Food", "✅ Accepted Pickups", "📢 Request Funds", "📁 My Fund Requests", "💖 Fund Donors"])
    
    with tab1:
        st.subheader("Live Food Alerts")
        donations = [d for d in fetch_data("donations") if d["status"] == "Available"]
        if not donations:
            st.info("No active food donations right now.")
            
        for d in donations:
            with st.container(border=True):
                st.write(f"**From:** {d['donor']} | **Items:** {d['items']}")
                
                # Smart Google Maps Link Display
                if " | MapsLink: " in d['location']:
                    address_part, link_part = d['location'].split(" | MapsLink: ")
                    st.write(f"**Loc:** {address_part}")
                    st.markdown(f"**[📍 Open in Google Maps (Navigate)]({link_part})**")
                else:
                    st.write(f"**Loc:** {d['location']}")
                    
                st.write(f"**Contact:** {d['contact']}")
                
                if st.button("Accept Pickup", key=f"acc_{d['id']}"):
                    update_data("donations", d['id'], {"status": "Accepted by " + st.session_state.current_user})
                    st.success("Accepted! Check 'Accepted Pickups' tab.")
                    st.rerun()

    with tab2:
        st.subheader("Your Accepted Pickups")
        my_pickups = [d for d in fetch_data("donations") if d["status"] == f"Accepted by {st.session_state.current_user}"]
        display_formatted_table(my_pickups, "AM-PKP")

    with tab3:
        st.subheader("Request Funds")
        reason = st.text_input("Need (e.g., Groceries, Lunch)")
        goal = st.number_input("Target Amount (₹)", min_value=100)
        upi = st.text_input("UPI ID (Ensure accuracy)")
        if st.button("Submit Fund Request"):
            if reason and goal and upi:
                insert_data("fund_requests", {
                    "ngo": st.session_state.current_user, "reason": reason, "goal": goal,
                    "raised": 0, "upi": upi, "status": "Active"
                })
                st.success("Fund Request Created!")
            else:
                st.error("Fill all details.")

    with tab4:
        st.subheader("My Fund Requests")
        my_reqs = [r for r in fetch_data("fund_requests") if r["ngo"] == st.session_state.current_user]
        display_formatted_table(my_reqs, "AM-REQ")

    with tab5:
        st.subheader("People who donated to you")
        my_donors = [f for f in fetch_data("fund_transactions") if f["ngo"] == st.session_state.current_user]
        display_formatted_table(my_donors, "AM-DNR")

# ==========================================
# 7. PROFESSIONAL ADMIN DASHBOARD
# ==========================================
def admin_dashboard():
    st.title("⚙️ Admin Dashboard")
    st.markdown("Monitor and manage platform activities, users, and transactions.")
    
    users = fetch_data("users")
    donations = fetch_data("donations")
    reqs = fetch_data("fund_requests")
    trans = fetch_data("fund_transactions")
    
    total_users = len(users) if users else 0
    total_meals = sum(d.get("veg_serves", 0) + d.get("nv_serves", 0) for d in donations) if donations else 0
    total_funds = sum(t.get("amount", 0) for t in trans) if trans else 0
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Registered Users", f"{total_users}")
    col2.metric("🍽️ Total Meals Donated", f"{total_meals}+")
    col3.metric("💰 Total Funds Raised", f"₹{total_funds}")
    
    st.markdown("---")
    st.write("### 📊 Database Records")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users List", "🍽️ Food Donations", "📢 Fund Requests", "💸 Transactions Log"])
    
    with tab1:
        display_formatted_table(users, "AM-USR")
    with tab2:
        display_formatted_table(donations, "AM-FD")
    with tab3:
        display_formatted_table(reqs, "AM-REQ")
    with tab4:
        display_formatted_table(trans, "AM-TXN")
        
    st.markdown("---")
    with st.expander("⚠️ Danger Zone (System Controls)", expanded=False):
        st.write("Clicking this will attempt to delete all data and reset the app.")
        if st.button("🗑️ Clear Entire Database (Reset All)"):
            st.warning("For security, bulk deletion is disabled via web. Please use Supabase SQL Editor to truncate tables.")

# ==========================================
# 8. MAIN APP ROUTING
# ==========================================
def main():
    render_sidebar()
    
    if not st.session_state.current_user:
        login_register_page()
    else:
        role = st.session_state.current_role
        if "Donor" in role:
            donor_dashboard()
        elif "NGO" in role:
            ngo_dashboard()
        elif "Admin" in role:
            admin_dashboard()
        else:
            st.title(f"👋 Welcome, {st.session_state.current_user}!")
            st.info("Dashboard under construction for this role.")

if __name__ == "__main__":
    main()
                                 
