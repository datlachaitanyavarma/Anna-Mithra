import streamlit as st
import datetime
import urllib.parse
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Annamithra - Food Waste Management", layout="wide")

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
        st.error(f"Error fetching data: {e}")
        return []

def insert_data(table_name, data):
    try:
        supabase.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def update_data(table_name, record_id, data):
    try:
        supabase.table(table_name).update(data).eq("id", record_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating data: {e}")
        return False

# ==========================================
# 4. AUTHENTICATION & REGISTRATION
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_role" not in st.session_state:
    st.session_state.current_role = None
if "points" not in st.session_state:
    st.session_state.points = 0

def login_register_page():
    # Logo Image
    try:
        st.image("logo.png", width=250)
    except:
        pass # Skips if image is missing to prevent crash
        
    st.title("Welcome to Annamithra")
    st.subheader("Bridging the gap between surplus food and the needy.")
    
    # Live Impact Dashboard
    st.markdown("---")
    st.markdown("### Our Live Impact")
    col1, col2, col3 = st.columns(3)
    donations = fetch_data("donations")
    funds = fetch_data("fund_transactions")
    users_data = fetch_data("users")
    
    total_meals = sum(d.get("veg_serves", 0) + d.get("nv_serves", 0) for d in donations) if donations else 0
    total_funds = sum(f.get("amount", 0) for f in funds) if funds else 0
    active_volunteers = len([u for u in users_data if u.get("role") == "Volunteer"]) if users_data else 0
    
    col1.metric("Meals Served", f"{total_meals}+")
    col2.metric("Funds Raised", f"Rs. {total_funds}")
    col3.metric("Active Volunteers", active_volunteers)
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="log_user")
        password = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login", type="primary"):
            # Hardcoded Admin bypass
            if username == "Admin" and password == "5979":
                st.session_state.current_user = "Admin"
                st.session_state.current_role = "Admin"
                st.session_state.points = 0
                st.success("Admin Login Successful!")
                st.rerun()
            else:
                user = next((u for u in users_data if u["username"] == username and u["password"] == password), None)
                if user:
                    st.session_state.current_user = user["username"]
                    st.session_state.current_role = user["role"]
                    st.session_state.points = user.get("reward_points", 0)
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Create Password", type="password", key="reg_pass")
        role = st.selectbox("Select Role", ["Donor", "NGO/Orphanage", "Volunteer"])
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email ID")
        blood_group = st.selectbox("Blood Group (Mandatory)", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        
        if st.button("Register"):
            if not all([new_user, new_pass, mobile, email]) or blood_group == "Select":
                st.warning("All fields including Blood Group are mandatory!")
                return
            if any(u["username"] == new_user for u in users_data):
                st.error("Username already exists! Please choose another.")
            else:
                success = insert_data("users", {
                    "username": new_user,
                    "password": new_pass,
                    "role": role, 
                    "mobile": mobile,
                    "email": email,
                    "blood_group": blood_group,
                    "reward_points": 0
                })
                if success:
                    st.success("Registration Successful! Please login from the Login tab.")

# ==========================================
# 5. DONOR DASHBOARD
# ==========================================
def donor_dashboard():
    st.title(f"Welcome, {st.session_state.current_user}!")
    st.sidebar.success(f"Role: {st.session_state.current_role}\n\nReward Points: {st.session_state.points}")
    
    tab1, tab2, tab3 = st.tabs(["Donate Food", "Support NGOs", "My Contributions"])
    
    with tab1:
        st.subheader("New Food Donation")
        contact = st.text_input("Contact Number")
        items = st.text_area("Food Items (e.g., Rice, Dal, Curry)")
        category = st.selectbox("Category", ["Cooked Food", "Raw Materials", "Packaged Food"])
        
        col1, col2 = st.columns(2)
        v_boxes = col1.number_input("Veg Boxes", min_value=0)
        v_serves = col1.number_input("Veg Serves How Many?", min_value=0)
        nv_boxes = col2.number_input("Non-Veg Boxes", min_value=0)
        nv_serves = col2.number_input("Non-Veg Serves How Many?", min_value=0)
        
        expiry = st.text_input("Estimated Expiry Time (e.g., 4 Hours)")
        location = st.text_area("Pickup Address")
        
        if st.button("Submit Donation", type="primary"):
            if items and location and contact:
                success = insert_data("donations", {
                    "donor": st.session_state.current_user,
                    "contact": contact,
                    "items": items,
                    "category": category,
                    "expiry": expiry,
                    "veg_boxes": v_boxes,
                    "veg_serves": v_serves,
                    "nv_boxes": nv_boxes,
                    "nv_serves": nv_serves,
                    "location": location,
                    "time": get_current_time(),
                    "status": "Available"
                })
                if success:
                    new_points = st.session_state.points + 10
                    users_data = fetch_data("users")
                    user_record = next((u for u in users_data if u["username"] == st.session_state.current_user), None)
                    if user_record:
                        update_data("users", user_record["id"], {"reward_points": new_points})
                    st.session_state.points = new_points
                    st.success("Thank you! Food donation listed successfully. You earned 10 points!")
            else:
                st.error("Please fill all mandatory fields (Items, Contact, Location).")

    with tab2:
        st.subheader("Active NGO Fund Requests")
        
        with st.expander("How to Donate & FAQ (Click to Expand)", expanded=False):
            st.markdown("""
            **Step-by-Step Guide:**
            1. Review the NGO requirements below.
            2. Enter your desired custom donation amount.
            3. Scan the QR code OR click the Payment Link to open your UPI app (GPay/PhonePe).
            4. After a successful payment, enter your 12-digit UTR/Transaction ID.
            5. Click 'Verify & Confirm'. You and the NGO will receive an instant automated email!
            
            **Frequently Asked Questions (FAQ):**
            * **Does my money go directly to the NGO?** Yes, directly to the NGO's official UPI ID.
            * **Does Annamithra charge any commission?** No, 100% free, zero-commission platform.
            * **How do I get my reward points?** Points are credited automatically upon verification.
            """)
            
        requests = fetch_data("fund_requests")
        active_reqs = [r for r in requests if r.get("status") == "Active"]
        
        if not active_reqs:
            st.info("No active fund requests at the moment.")
            
        for req in reversed(active_reqs):
            with st.container(border=True):
                st.markdown(f"### {req['ngo']}")
                st.write(f"**Requirement:** {req['reason']}")
                
                goal = req['goal']
                raised = req['raised']
                st.progress(min(raised / goal if goal > 0 else 0, 1.0))
                st.write(f"**Goal:** Rs. {goal} | **Raised:** Rs. {raised} | **Remaining:** Rs. {goal - raised}")
                
                share_text = urllib.parse.quote(f"Help {req['ngo']} raise Rs. {goal} for {req['reason']}. Donate securely via Annamithra!")
                st.markdown(f"[Share this request on WhatsApp](https://wa.me/?text={share_text})")
                
                st.divider()
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write("**Make a Secure Payment**")
                    st.code(f"UPI ID: {req['upi']}")
                    amount = st.number_input("Enter Amount (Rs)", min_value=1, max_value=goal-raised, value=100, key=f"amt_{req['id']}")
                    
                    upi_url = f"upi://pay?pa={req['upi']}&pn={req['ngo'].replace(' ', '%20')}&am={amount}&cu=INR"
                    st.markdown(f"**[Click Here to Pay Rs. {amount} via App]({upi_url})**")
                    
                    utr = st.text_input("Enter 12-Digit UTR Number", key=f"utr_{req['id']}")
                    if st.button("Verify & Confirm Donation", key=f"btn_{req['id']}", type="primary"):
                        if len(utr) >= 6:
                            new_raised = raised + amount
                            status = "Completed" if new_raised >= goal else "Active"
                            
                            update_data("fund_requests", req['id'], {"raised": new_raised, "status": status})
                            insert_data("fund_transactions", {
                                "donor": st.session_state.current_user,
                                "ngo": req['ngo'],
                                "amount": amount,
                                "reason": req['reason'],
                                "time": get_current_time()
                            })
                            st.success(f"Verified! Rs. {amount} successfully donated to {req['ngo']}.")
                            st.info(f"Confirmation emails initiated for {st.session_state.current_user} and {req['ngo']}.")
                            st.rerun()
                        else:
                            st.error("Please enter a valid UTR number to verify your transaction.")
                with col2:
                    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
                    st.image(qr_api, caption=f"Scan to pay Rs. {amount}")

    with tab3:
        st.subheader("Your Donation History")
        funds = [f for f in fetch_data("fund_transactions") if f["donor"] == st.session_state.current_user]
        food_history = [d for d in fetch_data("donations") if d["donor"] == st.session_state.current_user]
        
        st.write("### Financial Contributions")
        if funds:
            st.table(funds)
        else:
            st.write("No financial contributions yet.")
            
        st.write("### Food Donations")
        if food_history:
            st.table(food_history)
        else:
            st.write("No food donations yet.")

# ==========================================
# 6. NGO DASHBOARD
# ==========================================
def ngo_dashboard():
    st.title(f"NGO Portal: {st.session_state.current_user}")
    tab1, tab2 = st.tabs(["Request Funds", "Available Food Alerts"])
    
    with tab1:
        st.subheader("Create a New Fund Request")
        reason = st.text_input("Purpose (e.g., Monthly groceries for 50 children)")
        goal = st.number_input("Target Amount (Rs)", min_value=100)
        upi = st.text_input("NGO UPI ID (Ensure this is accurate for direct transfers)")
        
        if st.button("Post Request", type="primary"):
            if reason and goal and upi:
                success = insert_data("fund_requests", {
                    "ngo": st.session_state.current_user,
                    "reason": reason,
                    "goal": goal,
                    "raised": 0,
                    "upi": upi,
                    "status": "Active"
                })
                if success:
                    st.success("Fund request is now live on the platform!")
            else:
                st.error("Please fill in all details.")

    with tab2:
        st.subheader("Live Food Donations Available")
        donations = [d for d in fetch_data("donations") if d["status"] == "Available"]
        if not donations:
            st.info("No new food donations available at the moment.")
            
        for d in donations:
            with st.expander(f"Food from {d['donor']} - Loc: {d['location']}"):
                st.write(f"**Items:** {d['items']}")
                st.write(f"**Serves:** Veg: {d['veg_serves']} | Non-Veg: {d['nv_serves']}")
                st.write(f"**Contact:** {d['contact']}")
                st.write(f"**Expiry Estimate:** {d['expiry']}")
                
                if st.button("Accept Donation & Claim", key=f"acc_{d['id']}"):
                    update_data("donations", d['id'], {"status": "Accepted by " + st.session_state.current_user})
                    st.success("Donation Accepted! Please contact the donor immediately for pickup coordination.")
                    st.rerun()

# ==========================================
# 7. ADMIN DASHBOARD
# ==========================================
def admin_dashboard():
    st.title("Admin Portal")
    st.write("Welcome, Admin! Here you can monitor all platform activities.")
    
    tab1, tab2, tab3 = st.tabs(["All Users", "Food Donations", "Fund Requests"])
    
    with tab1:
        st.subheader("Registered Users")
        users = fetch_data("users")
        if users:
            st.dataframe(users)
        else:
            st.write("No users registered yet.")
            
    with tab2:
        st.subheader("Food Donations")
        donations = fetch_data("donations")
        if donations:
            st.dataframe(donations)
        else:
            st.write("No donations recorded yet.")
            
    with tab3:
        st.subheader("Fund Requests & Transactions")
        requests = fetch_data("fund_requests")
        if requests:
            st.dataframe(requests)
        else:
            st.write("No fund requests recorded yet.")

# ==========================================
# 8. MAIN APP ROUTING
# ==========================================
def main():
    if not st.session_state.current_user:
        login_register_page()
    else:
        st.sidebar.title("Navigation Menu")
        if st.sidebar.button("Logout", type="primary"):
            st.session_state.clear()
            st.rerun()
            
        role = st.session_state.current_role
        if role == "Donor":
            donor_dashboard()
        elif role == "NGO/Orphanage" or role == "NGO":
            ngo_dashboard()
        elif role == "Volunteer":
            st.title(f"Volunteer Portal: {st.session_state.current_user}")
            st.info("Volunteer dashboard is active. You can track food pickups here.")
        elif role == "Admin":
            admin_dashboard()
        else:
            st.error("Unknown Role")

if __name__ == "__main__":
    main()
                
