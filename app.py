import streamlit as st
import datetime
import urllib.parse
import pandas as pd
import streamlit.components.v1 as components
import smtplib
from email.message import EmailMessage
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
# 3. HELPER FUNCTIONS & EMAILS
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

# Email Helpers
def get_user_email(username, users_data):
    user = next((u for u in users_data if u["username"] == username), None)
    return user["email"] if user and "email" in user else "annamithra.official@gmail.com"

def get_emails_by_role(role, users_data):
    return [u["email"] for u in users_data if u.get("role") == role and "email" in u]

# Advanced Email Sender (TLS - Port 587 with Error Handling)
def send_email_notification(to_email, subject, body, bcc_list=None):
    st.toast(f"📧 Triggering automated emails...")
    try:
        sender_email = "annamithra.alert@gmail.com" 
        password = "hdbbkvxqmstitoyu" 
        
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        if bcc_list:
            msg['Bcc'] = ", ".join(bcc_list)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(sender_email, password)
            smtp.send_message(msg)
            
        st.toast("✅ Email Delivered Successfully!")
    except Exception as e:
        st.error(f"❌ Email Failed! Error: {e}")

# Admin Dashboard Table Formatter
def display_formatted_table(data, prefix="AM"):
    if not data:
        st.info("No records found in this category.")
        return
    df = pd.DataFrame(data)
    df.insert(0, 'Annamithra_ID', [f"{prefix}{str(i+1).zfill(4)}" for i in range(len(df))])
    if 'id' in df.columns: df = df.drop(columns=['id'])
    if 'password' in df.columns and prefix == "AM-USR": df['password'] = "••••••••"
    st.dataframe(df, hide_index=True, use_container_width=True)

# --- LIVE LOCATION COMPONENT ---
def render_location_widget():
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        .btn { background-color: #FF4B4B; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-family: sans-serif; font-size: 14px; }
        .btn-copy { background-color: #4CAF50; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-family: sans-serif; font-size: 14px; margin-left: 5px; }
        input { width: 100%; padding: 10px; margin-top: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-family: sans-serif; color: #333; }
        </style>
        </head>
        <body style="margin:0; padding:15px; font-family:sans-serif; background-color:#f4f6f9; border-radius:8px; border:1px solid #e0e0e0;">
        <p style="margin-top:0; font-size:15px; color:#333; font-weight:bold;">📍 Get Your Live Location Link</p>
        <button class="btn" onclick="getLocation()">1. Get My Current Location</button>
        <input type="text" id="loc_link" placeholder="Your Google Maps link will appear here..." readonly>
        <button class="btn-copy" onclick="copyLink()">2. 📋 Copy Link</button>
        <script>
        function getLocation() {
            var inputField = document.getElementById("loc_link");
            inputField.value = "Fetching location... Please wait and click 'Allow'.";
            if (navigator.geolocation) { navigator.geolocation.getCurrentPosition(showPosition, showError); } 
            else { inputField.value = "Geolocation is not supported by this browser."; }
        }
        function showPosition(position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            document.getElementById("loc_link").value = "https://www.google.com/maps?q=" + lat + "," + lon;
        }
        function showError(error) { document.getElementById("loc_link").value = "Error fetching location."; }
        function copyLink() {
            var copyText = document.getElementById("loc_link");
            if (!copyText.value || copyText.value.includes("Error") || copyText.value.includes("Fetching")) { alert("Get location first!"); return; }
            copyText.select(); document.execCommand("copy");
            alert("✅ Link Copied! Paste it in the box below.");
        }
        </script>
        </body>
        </html>
        """,
        height=180
    )

# ==========================================
# 4. SIDEBAR & AUTHENTICATION
# ==========================================
if "current_user" not in st.session_state: st.session_state.current_user = None
if "current_role" not in st.session_state: st.session_state.current_role = None

def render_sidebar():
    try: st.sidebar.image("logo.png", use_container_width=True)
    except: st.sidebar.write("*(Logo.png missing)*")
    st.sidebar.markdown("---")
    
    if not st.session_state.current_user:
        st.sidebar.write("🔒 Please login.")
    else:
        st.sidebar.success(f"👤 {st.session_state.current_user}")
        st.sidebar.info(f"Role: {st.session_state.current_role}")
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True): st.rerun()
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    st.sidebar.markdown("---")
    st.sidebar.markdown("📍 Vepagunta, AP | 📧 contact@annamithra.org")

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
                        
                        user_email = user.get("email", "annamithra.official@gmail.com")
                        body = f"Hello {user['username']},\n\nA successful login was detected on your Annamithra account at {get_current_time()}.\n\nIf this was you, no action is needed."
                        send_email_notification(user_email, "Security Alert: Login Detected", body)
                        
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
            blood_group = st.selectbox("Blood Group", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            
            if st.button("Register", use_container_width=True):
                if not all([new_user, new_pass, mobile, email]) or blood_group == "Select":
                    st.warning("All fields are mandatory!")
                elif any(u["username"] == new_user for u in users_data):
                    st.error("Username already exists!")
                else:
                    insert_data("users", {"username": new_user, "password": new_pass, "role": role, "mobile": mobile, "email": email, "blood_group": blood_group})
                    st.success("Registration Successful! Please login.")
                    send_email_notification(email, "Welcome to Annamithra", f"Hello {new_user},\n\nThank you for registering on Annamithra as a {role}.\nTogether we can fight food waste!\n\nRegards,\nTeam Annamithra")

# ==========================================
# 5. DONOR DASHBOARD
# ==========================================
def donor_dashboard():
    st.title(f"👋 Welcome, {st.session_state.current_user}!")
    tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📜 My History"])
    
    with tab1:
        st.subheader("Submit Surplus Food")
        food_type = st.radio("Category of Food", ["Veg", "Non-Veg", "Both (Veg & Non-Veg)"], horizontal=True)
        
        with st.container(border=True):
            contact = st.text_input("Contact Number *")
            items = st.text_area("Food Items (e.g., Rice, Dal) *")
            v_boxes = st.number_input("Veg Boxes", min_value=0) if "Veg" in food_type else 0
            v_serves = st.number_input("Veg Serves", min_value=0) if "Veg" in food_type else 0
            nv_boxes = st.number_input("Non-Veg Boxes", min_value=0) if "Non" in food_type else 0
            nv_serves = st.number_input("Non-Veg Serves", min_value=0) if "Non" in food_type else 0
            address = st.text_area("Pickup Address *")
            
            render_location_widget()
            gmaps_link = st.text_input("Paste the Copied Location Link Here 🔗 *")
            
            if st.button("Submit Food Details", type="primary"):
                if contact and items and address and gmaps_link:
                    final_loc = f"{address} | MapsLink: {gmaps_link}"
                    insert_data("donations", {
                        "donor": st.session_state.current_user, "contact": contact, "items": items,
                        "category": food_type, "veg_boxes": v_boxes, "veg_serves": v_serves,
                        "nv_boxes": nv_boxes, "nv_serves": nv_serves, "location": final_loc,
                        "expiry": "N/A", "time": get_current_time(), "status": "Available"
                    })
                    st.success("Food Details Submitted!")
                    
                    users_data = fetch_data("users")
                    donor_email = get_user_email(st.session_state.current_user, users_data)
                    volunteers = get_emails_by_role("Volunteer", users_data)
                    ngos = get_emails_by_role("NGO / Orphanage", users_data)
                    
                    alert_recipients = volunteers + ngos
                    
                    send_email_notification(donor_email, "Food Donation Listed", f"Dear {st.session_state.current_user},\n\nYour food donation has been successfully listed. An NGO or Volunteer will accept it soon.\n\nThank you!")
                    if alert_recipients:
                        send_email_notification("annamithra.official@gmail.com", "New Food Available for Pickup", f"Hello,\n\nNew food has been listed by {st.session_state.current_user}.\n\nItems: {items}\nAddress: {address}\n\nPlease check your Annamithra dashboard to accept the pickup.", bcc_list=alert_recipients)
                else:
                    st.error("Fill all mandatory (*) fields including Map Link.")

    with tab2:
        st.subheader("NGO Fund Requests")
        requests = fetch_data("fund_requests")
        active_reqs = [r for r in requests if r.get("status") == "Active"]
        if not active_reqs: st.info("No active fund requests.")
            
        for req in reversed(active_reqs):
            with st.expander(f"🏢 {req['ngo']} - Need: {req['reason']}", expanded=True):
                goal, raised = req['goal'], req['raised']
                st.write(f"**Goal:** ₹{goal} | **Raised:** ₹{raised}")
                st.progress(min(raised / goal if goal > 0 else 0, 1.0))
                st.info(f"**UPI ID:** {req['upi']}")
                
                amount = st.number_input("Donate (₹)", min_value=1, max_value=goal-raised, value=100, key=f"amt_{req['id']}")
                utr = st.text_input("Enter 12-Digit UTR:", key=f"utr_{req['id']}")
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
                        st.success("Donation Verified!")
                        
                        users_data = fetch_data("users")
                        donor_email = get_user_email(st.session_state.current_user, users_data)
                        ngo_email = get_user_email(req['ngo'], users_data)
                        
                        send_email_notification(donor_email, "Donation Successful", f"Dear {st.session_state.current_user},\n\nYour donation of ₹{amount} to {req['ngo']} is verified.\n\nThank you for your generosity!")
                        send_email_notification(ngo_email, "New Fund Donation Received", f"Dear {req['ngo']},\n\nYou received a donation of ₹{amount} from {st.session_state.current_user} for '{req['reason']}'.\n\nPlease check your account.")
                        st.rerun()
                    else:
                        st.error("Enter valid UTR.")

    with tab3:
        st.subheader("My Contributions (History)")
        funds = [f for f in fetch_data("fund_transactions") if f["donor"] == st.session_state.current_user]
        food = [d for d in fetch_data("donations") if d["donor"] == st.session_state.current_user]
        
        st.write("### 💰 Financial Contributions")
        if not funds: st.info("No funds donated yet.")
        for f in reversed(funds):
            with st.container(border=True):
                st.write(f"**To:** {f['ngo']} | **Amount:** ₹{f['amount']} | **Reason:** {f['reason']}")
                st.caption(f"📅 Date: {f['time']}")
                
        st.write("### 🍽️ Food Contributions")
        if not food: st.info("No food donated yet.")
        for d in reversed(food):
            with st.container(border=True):
                st.write(f"**Items:** {d['items']} | **Category:** {d['category']}")
                st.write(f"**Status:** `{d['status']}`")
                st.caption(f"📅 Listed On: {d['time']}")

# ==========================================
# 6. NGO DASHBOARD
# ==========================================
def ngo_dashboard():
    st.title(f"🏢 {st.session_state.current_user}")
    tab1, tab2, tab3, tab4 = st.tabs(["🔔 Live Food", "✅ Accepted Pickups", "📢 Fund Requests", "📁 History & Donors"])
    
    with tab1:
        st.subheader("Live Food Alerts")
        donations = [d for d in fetch_data("donations") if d["status"] == "Available"]
        if not donations: st.info("No active food donations right now.")
            
        for d in donations:
            with st.container(border=True):
                st.write(f"**From:** {d['donor']} | **Items:** {d['items']}")
                if " | MapsLink: " in d['location']:
                    address_part, link_part = d['location'].split(" | MapsLink: ")
                    st.write(f"**Loc:** {address_part}")
                    st.markdown(f"**[📍 Open in Google Maps]({link_part})**")
                else:
                    st.write(f"**Loc:** {d['location']}")
                st.write(f"**Contact:** {d['contact']}")
                
                if st.button("Accept Pickup", key=f"acc_{d['id']}"):
                    update_data("donations", d['id'], {"status": f"Accepted by {st.session_state.current_user}"})
                    st.success("Accepted! Check 'Accepted Pickups' tab.")
                    
                    users_data = fetch_data("users")
                    ngo_email = get_user_email(st.session_state.current_user, users_data)
                    donor_email = get_user_email(d['donor'], users_data)
                    volunteers = get_emails_by_role("Volunteer", users_data)
                    
                    send_email_notification(ngo_email, "Pickup Accepted", f"Dear {st.session_state.current_user},\n\nYou have accepted the food pickup from {d['donor']}. Please collect it soon.")
                    send_email_notification(donor_email, "Food Accepted by NGO", f"Dear {d['donor']},\n\nGood news! {st.session_state.current_user} has accepted your food donation and will pick it up soon.")
                    if volunteers:
                        send_email_notification("annamithra.official@gmail.com", "Update: Food Accepted", f"Hello Volunteers,\n\nThe food listed by {d['donor']} has been accepted by {st.session_state.current_user} and is no longer available.", bcc_list=volunteers)
                    
                    st.rerun()

    with tab2:
        st.subheader("Your Active Pickups")
        my_pickups = [d for d in fetch_data("donations") if d["status"] == f"Accepted by {st.session_state.current_user}"]
        
        if not my_pickups: st.info("No pending pickups.")
        
        for p in my_pickups:
            with st.container(border=True):
                st.write(f"**Donor:** {p['donor']} | **Contact:** {p['contact']}")
                st.write(f"**Items:** {p['items']}")
                if " | MapsLink: " in p['location']:
                    st.markdown(f"**[📍 Navigate Location]({p['location'].split(' | MapsLink: ')[1]})**")
                
                st.warning("Make sure you reach the location before clicking this button.")
                if st.button("Mark as 'Reached Location' (Completed)", key=f"reach_{p['id']}"):
                    update_data("donations", p['id'], {"status": f"Completed by {st.session_state.current_user}"})
                    st.success("Status Updated: Pickup Completed!")
                    
                    users_data = fetch_data("users")
                    ngo_email = get_user_email(st.session_state.current_user, users_data)
                    donor_email = get_user_email(p['donor'], users_data)
                    
                    send_email_notification(ngo_email, "Pickup Completed", f"Dear {st.session_state.current_user},\n\nYou have successfully completed the pickup from {p['donor']}.")
                    send_email_notification(donor_email, "Food Pickup Completed", f"Dear {p['donor']},\n\n{st.session_state.current_user} has successfully reached the location and picked up your food.\n\nThank you for preventing food waste!")
                    st.rerun()

    with tab3:
        st.subheader("Request Funds")
        reason = st.text_input("Need (e.g., Groceries, Lunch)")
        goal = st.number_input("Target Amount (₹)", min_value=100)
        upi = st.text_input("UPI ID")
        if st.button("Submit Fund Request"):
            if reason and goal and upi:
                insert_data("fund_requests", {"ngo": st.session_state.current_user, "reason": reason, "goal": goal, "raised": 0, "upi": upi, "status": "Active"})
                st.success("Fund Request Created!")
                
                users_data = fetch_data("users")
                ngo_email = get_user_email(st.session_state.current_user, users_data)
                send_email_notification(ngo_email, "Fund Request Live", f"Dear {st.session_state.current_user},\n\nYour fund request for ₹{goal} ({reason}) is now live on Annamithra.")
            else:
                st.error("Fill all details.")

    with tab4:
        st.subheader("My Fund Requests & Donors")
        st.write("#### 📢 My Requests")
        my_reqs = [r for r in fetch_data("fund_requests") if r["ngo"] == st.session_state.current_user]
        if not my_reqs: st.write("No requests made.")
        for r in reversed(my_reqs):
            with st.container(border=True):
                st.write(f"**Need:** {r['reason']} | **Goal:** ₹{r['goal']} | **Raised:** ₹{r['raised']}")
                st.caption(f"Status: {r['status']}")
                
        st.write("#### 💖 People who donated to you")
        my_donors = [f for f in fetch_data("fund_transactions") if f["ngo"] == st.session_state.current_user]
        if not my_donors: st.write("No donations received yet.")
        for f in reversed(my_donors):
            with st.container(border=True):
                st.write(f"**Donor:** {f['donor']} sent **₹{f['amount']}**")
                st.caption(f"📅 Date: {f['time']}")

# ==========================================
# 7. PROFESSIONAL ADMIN DASHBOARD
# ==========================================
def admin_dashboard():
    st.title("⚙️ Admin Dashboard")
    users, donations, reqs, trans = fetch_data("users"), fetch_data("donations"), fetch_data("fund_requests"), fetch_data("fund_transactions")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Users", len(users) if users else 0)
    col2.metric("🍽️ Meals", sum(d.get("veg_serves", 0) + d.get("nv_serves", 0) for d in donations) if donations else 0)
    col3.metric("💰 Funds", f"₹{sum(t.get('amount', 0) for t in trans) if trans else 0}")
    
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "🍽️ Food", "📢 Requests", "💸 Transactions"])
    with tab1: display_formatted_table(users, "AM-USR")
    with tab2: display_formatted_table(donations, "AM-FD")
    with tab3: display_formatted_table(reqs, "AM-REQ")
    with tab4: display_formatted_table(trans, "AM-TXN")

# ==========================================
# 8. MAIN ROUTING
# ==========================================
def main():
    render_sidebar()
    if not st.session_state.current_user: login_register_page()
    else:
        role = st.session_state.current_role
        if "Donor" in role: donor_dashboard()
        elif "NGO" in role: ngo_dashboard()
        elif "Admin" in role: admin_dashboard()
        else: st.info("Dashboard under construction.")

if __name__ == "__main__": 
    main()
