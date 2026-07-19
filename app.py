import streamlit as st
import streamlit.components.v1 as components
import datetime
import os
import json
import smtplib
from email.message import EmailMessage
from PIL import Image

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")

DB_FILE = "database.json"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- EMAIL CONFIGURATION ---
EMAIL_USER = "AnnaMithra.alert@gmail.com"
EMAIL_PASS = "dqfnqinpxrzvufrh" 

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# --- INDIAN STANDARD TIME (IST) SETUP ---
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# --- 2. DATABASE SYSTEM (JSON BASED) ---
def load_data():
    default_data = {
        "users": [{"username": "Admin", "password": "5979", "role": "Admin Portal", "mobile": "Admin", "email": "", "reward_points": 0}],
        "donations": [],
        "fund_requests": [],
        "fund_transactions": []
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                for user in data["users"]:
                    if "reward_points" not in user:
                        user["reward_points"] = 0
                return data
        except json.JSONDecodeError:
            return default_data
    return default_data

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

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
        
        if st.session_state.current_role == "Donor (Individual/Hotel)":
            current_user_data = next((u for u in st.session_state.db["users"] if u["username"] == st.session_state.current_user), None)
            points = current_user_data.get("reward_points", 0) if current_user_data else 0
            st.warning(f"🏆 Reward Points: **{points}**")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
            
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.current_role = ""
            st.rerun()
    else:
        st.write("🔒 Please login.")
    st.divider()
    st.write("📍 Vepagunta, AP | 📧 contact@annamithra.org")

# --- 4. MAIN PAGE (LOGIN/REGISTER) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Welcome to Annamithra 🤝</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with auth_tab1:
            with st.container(border=True):
                log_user = st.text_input("Username", key="login_user")
                log_pass = st.text_input("Password", type="password", key="login_pass")
                if st.button("Login", type="primary", use_container_width=True, key="login_btn"):
                    matched_user = next((u for u in st.session_state.db["users"] if u["username"].lower() == log_user.lower() and u["password"] == log_pass), None)
                    if matched_user:
                        st.session_state.logged_in = True
                        st.session_state.current_user = matched_user["username"]
                        st.session_state.current_role = matched_user["role"]
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password!")
        
        with auth_tab2:
            with st.container(border=True):
                new_user = st.text_input("Choose Username *", key="reg_user")
                new_pass = st.text_input("Create Password *", type="password", key="reg_pass")
                new_mobile = st.text_input("Mobile Number (Mandatory) *", key="reg_mob")
                new_email = st.text_input("Email Address (Mandatory) *", key="reg_email") 
                new_role = st.selectbox("I am a:", ["Donor (Individual/Hotel)", "NGO / Orphanage", "Volunteer"], key="reg_role")
                
                if st.button("Create Account", type="primary", use_container_width=True, key="reg_btn"):
                    if any(u["username"].lower() == new_user.lower() for u in st.session_state.db["users"]):
                        st.error("Username already exists!")
                    elif new_user and new_pass and new_mobile and new_email:
                        st.session_state.db["users"].append({
                            "username": new_user, "password": new_pass, "role": new_role,
                            "mobile": new_mobile, "email": new_email, "reward_points": 0
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Account created! You can now Login.")
                    else:
                        st.error("⚠️ Please fill all mandatory (*) fields.")

else:
    # ==========================================
    # --- ADMIN DASHBOARD ---
    # ==========================================
    if st.session_state.current_role == "Admin Portal":
        st.title("👑 Admin Portal - Master Data")
        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["👥 All Users", "🍲 All Food Donations", "💰 All Fund Requests"])
        
        with adm_tab1:
            st.subheader("Registered Users")
            st.table(st.session_state.db["users"])
            
        with adm_tab2:
            st.subheader("Food Donation Records")
            st.table(st.session_state.db["donations"])
            
        with adm_tab3:
            st.subheader("Fund Requests & Transactions")
            st.write("Requests:")
            st.table(st.session_state.db["fund_requests"])
            st.write("Transactions:")
            st.table(st.session_state.db["fund_transactions"])

    # ==========================================
    # --- DONOR DASHBOARD ---
    # ==========================================
    elif st.session_state.current_role == "Donor (Individual/Hotel)":
        st.title(f"👋 Welcome, {st.session_state.current_user}!")
        tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📜 My History"])
        
        with tab1:
            st.subheader("Submit Surplus Food")
            food_category = st.radio("Category of Food", ["Veg", "Non-Veg", "Both (Veg & Non-Veg)"], horizontal=True)
            
            with st.form("donation_form", clear_on_submit=True):
                contact = st.text_input("Contact Number (For this pickup) *")
                food_items = st.text_area("What food items are you donating? *")
                approx_expiry = st.selectbox("Approximate Expiry Time", ["2 Hours", "4 Hours", "6 Hours", "8+ Hours"])
                food_image = st.file_uploader("Upload Food Photo (Optional)", type=["jpg", "png", "jpeg"])
                
                v_boxes = v_serves = nv_boxes = nv_serves = 0
                
                if food_category in ["Veg", "Both (Veg & Non-Veg)"]:
                    st.markdown("🟢 **Veg Details**")
                    v_boxes = st.number_input("Veg - No. of Boxes", min_value=0, step=1)
                    v_serves = st.number_input("Veg - Serves (Persons)", min_value=0, step=1)
                
                if food_category in ["Non-Veg", "Both (Veg & Non-Veg)"]:
                    st.markdown("🔴 **Non-Veg Details**")
                    nv_boxes = st.number_input("Non-Veg - No. of Boxes", min_value=0, step=1)
                    nv_serves = st.number_input("Non-Veg - Serves (Persons)", min_value=0, step=1)
                
                # 🔥 GOOGLE MAPS LOCATION BUTTON WITH COPY FEATURE
                st.markdown("📍 **Get exact location for easy pickup:**")
                components.html("""
                    <script>
                    var mapLink = "";
                    function getLocation() {
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(showPosition, showError);
                        } else {
                            document.getElementById("loc").innerHTML = "Geolocation is not supported.";
                        }
                    }
                    function showPosition(position) {
                        mapLink = "https://maps.google.com/?q=" + position.coords.latitude + "," + position.coords.longitude;
                        document.getElementById("loc").innerHTML = 
                            "<b>Link:</b> <a href='" + mapLink + "' target='_blank'>" + mapLink + "</a>" + 
                            "<br><br><button onclick='copyToClipboard()' style='padding:8px; background-color:#008CBA; color:white; border:none; border-radius:5px; cursor:pointer;'>📋 Copy Link</button>";
                    }
                    function showError(error) {
                        document.getElementById("loc").innerHTML = "Please allow location access.";
                    }
                    function copyToClipboard() {
                        navigator.clipboard.writeText(mapLink).then(function() {
                            alert("Link Copied! Paste it in the box below.");
                        }).catch(function(err) {
                            alert("Copy failed. Please copy manually.");
                        });
                    }
                    </script>
                    <button onclick="getLocation()" style="padding:10px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">🧭 1. Get My Location</button>
                    <p id="loc" style="font-family:sans-serif; font-size:14px; margin-top:10px;"></p>
                """, height=120)
                
                location = st.text_input("Paste the copied Google Maps Link or Type Address here *")
                
                if st.form_submit_button("Submit Food Details"):
                    if not contact or not location or not food_items:
                        st.error("⚠️ Please fill Contact Number, Food Items, and Location!")
                    else:
                        img_path = ""
                        if food_image is not None:
                            img_path = os.path.join(UPLOAD_DIR, food_image.name)
                            with open(img_path, "wb") as f:
                                f.write(food_image.getbuffer())

                        current_time = datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p")
                        
                        st.session_state.db["donations"].append({
                            "id": len(st.session_state.db["donations"]) + 1,
                            "donor": st.session_state.current_user,
                            "contact": contact,
                            "items": food_items,
                            "category": food_category,
                            "expiry": approx_expiry,
                            "image": img_path,
                            "veg_boxes": v_boxes, "veg_serves": v_serves,
                            "nv_boxes": nv_boxes, "nv_serves": nv_serves,
                            "location": location,
                            "time": current_time,
                            "status": "Available"
                        })
                        
                        for u in st.session_state.db["users"]:
                            if u["username"] == st.session_state.current_user:
                                u["reward_points"] += 10
                                break
                                
                        save_data(st.session_state.db)
                        st.success("✅ Posted Successfully! You earned 10 Reward Points! 🏆 NGOs & Volunteers have been notified.")

        with tab2:
            st.subheader("NGO Fund Requests")
            for req in reversed(st.session_state.db["fund_requests"]):
                if req.get("status") == "Active":
                    with st.expander(f"🏢 {req.get('ngo', 'NGO')} - Need: {req.get('reason', 'Help')}", expanded=True):
                        st.write(f"**Goal:** ₹{req.get('goal', 0)} | **Raised:** ₹{req.get('raised', 0)}")
                        goal = req.get('goal', 1)
                        raised = req.get('raised', 0)
                        st.progress(min(raised / goal if goal > 0 else 0, 1.0))
        
        with tab3:
            st.subheader("🍱 My Past Food Donations")
            my_donations = [d for d in st.session_state.db["donations"] if d.get("donor") == st.session_state.current_user]
            if not my_donations:
                st.info("You haven't made any food donations yet.")
            else:
                for d in reversed(my_donations):
                    with st.container(border=True):
                        st.write(f"📅 **{d.get('time', 'Unknown Time')}** | Status: **{d.get('status', 'Unknown')}**")
                        st.write(f"**Items:** {d.get('items', 'Not specified')} (Expires in {d.get('expiry', 'Unknown')})")

    # ==========================================
    # --- NGO DASHBOARD ---
    # ==========================================
    elif st.session_state.current_role == "NGO / Orphanage":
        st.title(f"🏢 {st.session_state.current_user}")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔔 Available Food", "✅ Accepted Pickups", "📢 Request Funds", "📂 My Fund Requests", "💖 Fund Donors"])
        
        with tab1:
            st.subheader("Live Food Alerts")
            available = [d for d in st.session_state.db["donations"] if d.get("status") == "Available"]
            if not available:
                st.info("No active food donations right now.")
            else:
                for idx, d in enumerate(available):
                    with st.container(border=True):
                        st.write(f"🚨 **From:** {d.get('donor', 'Unknown')} | ⏳ **Expires in:** {d.get('expiry', 'N/A')}")
                        st.write(f"📍 **Address/Map:** {d.get('location', 'N/A')}")
                        st.write(f"🍲 **Items:** {d.get('items', 'Not specified')}")
                        if d.get("image") and os.path.exists(d.get("image")):
                            st.image(Image.open(d.get("image")), width=200)

                        safe_id = d.get('id', f"ngo_avail_{idx}")
                        if st.button(f"Accept Pickup", key=f"acc_{safe_id}", use_container_width=True):
                            d['status'] = f"Accepted by {st.session_state.current_user} (NGO)"
                            save_data(st.session_state.db)
                            st.success("Accepted!")
                            st.rerun()

        with tab2:
            st.subheader("Food You Have Accepted")
            my_pickups = [d for d in st.session_state.db["donations"] if d.get("status") == f"Accepted by {st.session_state.current_user} (NGO)"]
            if not my_pickups:
                st.info("You haven't accepted any food pickups yet.")
            else:
                for idx, d in enumerate(reversed(my_pickups)):
                    with st.container(border=True):
                        st.write(f"🚨 **From:** {d.get('donor', 'Unknown')} | 📞 **Contact:** {d.get('contact', 'N/A')}")
                        st.write(f"📍 **Address:** {d.get('location', 'N/A')}")
                        
                        safe_id = d.get('id', f"ngo_recv_{idx}")
                        if st.button("🍽️ Mark as Food Received", key=f"recv_{safe_id}", type="primary"):
                            d['status'] = f"Received by {st.session_state.current_user} (NGO)"
                            save_data(st.session_state.db)
                            st.success("✅ Marked as Received!")
                            st.rerun()

        with tab3:
            st.subheader("Post Emergency Need")
            with st.form("fund_form", clear_on_submit=True):
                reason = st.text_input("Reason (e.g. Groceries for 50 kids)")
                goal = st.number_input("Target Amount (₹)", min_value=500, step=500)
                upi = st.text_input("Your UPI ID")
                qr = st.text_input("QR Code Image URL (Optional)")
                if st.form_submit_button("Post Request"):
                    if reason and upi:
                        st.session_state.db["fund_requests"].append({
                            "id": len(st.session_state.db["fund_requests"]) + 1,
                            "ngo": st.session_state.current_user,
                            "reason": reason, "goal": goal, "raised": 0,
                            "upi": upi, "qr_url": qr, "status": "Active"
                        })
                        save_data(st.session_state.db)
                        st.success("✅ Fund request posted successfully!")
                    else:
                        st.error("Please fill reason and UPI id.")
                        
        with tab4:
            st.subheader("My Fund Requests")
            my_reqs = [r for r in st.session_state.db["fund_requests"] if r.get("ngo") == st.session_state.current_user]
            if not my_reqs:
                st.info("You haven't posted any requests.")
            else:
                for r in reversed(my_reqs):
                    st.write(f"**Need:** {r.get('reason')} | **Raised:** ₹{r.get('raised')} / ₹{r.get('goal')} | **Status:** {r.get('status')}")
                    st.divider()
                    
        with tab5:
            st.subheader("Donors Who Supported You")
            my_funds = [f for f in st.session_state.db["fund_transactions"] if f.get("ngo") == st.session_state.current_user]
            if not my_funds:
                st.info("No donations received yet.")
            else:
                for f in reversed(my_funds):
                    st.write(f"💖 **{f.get('donor')}** donated **₹{f.get('amount')}** for {f.get('reason')} on {f.get('time')}")

    # ==========================================
    # --- VOLUNTEER DASHBOARD ---
    # ==========================================
    elif st.session_state.current_role == "Volunteer":
        st.title(f"🙋‍♂️ Welcome Volunteer, {st.session_state.current_user}!")
        tab1, tab2 = st.tabs(["🔔 Available Food for Pickup", "✅ My Deliveries"])
        
        with tab1:
            st.subheader("Rescue Food & Distribute to Needy")
            available = [d for d in st.session_state.db["donations"] if d.get("status") == "Available"]
            if not available:
                st.info("No active food donations right now.")
            else:
                for idx, d in enumerate(available):
                    with st.container(border=True):
                        st.write(f"🚨 **From:** {d.get('donor', 'Unknown')} | ⏳ **Expires in:** {d.get('expiry', 'N/A')}")
                        st.write(f"📍 **Address/Map:** {d.get('location', 'N/A')}")
                        st.write(f"🍲 **Items:** {d.get('items', 'Not specified')}")
                        if d.get("image") and os.path.exists(d.get("image")):
                            st.image(Image.open(d.get("image")), width=200)
                            
                        safe_id = d.get('id', f"vol_avail_{idx}")
                        if st.button("I will Pickup & Distribute", key=f"vol_acc_{safe_id}", type="primary"):
                            d['status'] = f"Accepted by Volunteer {st.session_state.current_user}"
                            save_data(st.session_state.db)
                            st.success("Accepted! Please coordinate with the donor.")
                            st.rerun()

        with tab2:
            st.subheader("Food You Have Accepted")
            my_pickups = [d for d in st.session_state.db["donations"] if d.get("status") == f"Accepted by Volunteer {st.session_state.current_user}"]
            if not my_pickups:
                st.info("You haven't accepted any pickups yet.")
            else:
                for idx, d in enumerate(reversed(my_pickups)):
                    with st.container(border=True):
                        st.write(f"🚨 **Donor:** {d.get('donor', 'Unknown')} | 📞 **Contact:** {d.get('contact', 'N/A')}")
                        st.write(f"📍 **Pickup Address:** {d.get('location', 'N/A')}")
                        
                        safe_id = d.get('id', f"vol_recv_{idx}")
                        if st.button("✅ Mark as Distributed to Needy", key=f"vol_recv_{safe_id}", type="primary"):
                            d['status'] = f"Distributed by Volunteer {st.session_state.current_user}"
                            save_data(st.session_state.db)
                            st.success("Great job! Food distributed successfully.")
                            st.rerun()
