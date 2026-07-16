import streamlit as st
import datetime, os, json, smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Annamithra - Food & Fund Platform", page_icon="🤝", layout="wide")
DB_FILE = "database.json"
EMAIL_USER = "AnnaMithra.alert@gmail.com"
EMAIL_PASS = "dqfnqinpxrzvufrh" # Ne kotha app password

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'], msg['From'], msg['To'] = subject, EMAIL_USER, to_email
    msg.set_content(body)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"⚠️ Email Error for {to_email}: {e}")
        return False

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if "users" not in data: data["users"] = [{"username": "Admin", "password": "5979", "role": "Admin Portal", "mobile": "Admin", "email": ""}]
            if "fund_transactions" not in data: data["fund_transactions"] = [] 
            return data
    return {"users": [{"username": "Admin", "password": "5979", "role": "Admin Portal", "mobile": "Admin", "email": ""}], "donations": [], "fund_requests": [], "fund_transactions": []}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'logged_in' not in st.session_state: st.session_state.logged_in, st.session_state.current_user, st.session_state.current_role = False, "", ""

with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("<h2 style='text-align: center; color: #FF8C00;'>📦🤝🍲 Annamithra</h2>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.logged_in:
        st.success(f"👤 **{st.session_state.current_user}**\n\nRole: {st.session_state.current_role}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else: st.write("🔒 Please login.")
    st.divider()
    st.write("📍 Vepagunta, AP | 📧 contact@annamithra.org")

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
                    for u in st.session_state.db["users"]:
                        if u["username"].lower() == log_user.lower() and u["password"] == log_pass:
                            st.session_state.logged_in, st.session_state.current_user, st.session_state.current_role = True, u["username"], u["role"]
                            st.rerun()
        with auth_tab2:
            with st.container(border=True):
                new_user = st.text_input("Choose Username *", key="reg_user")
                new_pass = st.text_input("Create Password *", type="password", key="reg_pass")
                new_mobile = st.text_input("Mobile Number (Mandatory) *", key="reg_mob")
                new_email = st.text_input("Email Address (Mandatory) *", key="reg_email") 
                new_role = st.selectbox("I am a:", ["Donor (Individual/Hotel)", "NGO / Orphanage"], key="reg_role")
                if st.button("Create Account", type="primary", use_container_width=True, key="reg_btn"):
                    if any(u["username"].lower() == new_user.lower() for u in st.session_state.db["users"]): st.error("Username already exists!")
                    elif new_user and new_pass and new_mobile and new_email:
                        st.session_state.db["users"].append({"username": new_user, "password": new_pass, "role": new_role, "mobile": new_mobile, "email": new_email})
                        save_data(st.session_state.db)
                        st.success("✅ Account created! You can now Login.")
                    else: st.error("⚠️ Please fill all mandatory (*) fields including Email.")

else:
    # --- DONOR DASHBOARD ---
    if st.session_state.current_role == "Donor (Individual/Hotel)":
        st.title(f"👋 Welcome, {st.session_state.current_user}!")
        tab1, tab2, tab3 = st.tabs(["🍽️ Donate Food", "💰 Support NGOs", "📜 My History"])
        with tab1:
            st.subheader("Submit Surplus Food")
            food_category = st.radio("Category of Food", ["Veg", "Non-Veg", "Both (Veg & Non-Veg)"], horizontal=True)
            with st.form("donation_form"):
                contact = st.text_input("Contact Number (For this pickup) *")
                food_items = st.text_area("Food items? (e.g., Rice, Dal, Chicken) *")
                v_boxes = v_serves = nv_boxes = nv_serves = 0
                if food_category in ["Veg", "Both (Veg & Non-Veg)"]:
                    v_boxes, v_serves = st.number_input("Veg Boxes", min_value=0), st.number_input("Veg Serves", min_value=0)
                if food_category in ["Non-Veg", "Both (Veg & Non-Veg)"]:
                    nv_boxes, nv_serves = st.number_input("Non-Veg Boxes", min_value=0), st.number_input("Non-Veg Serves", min_value=0)
                location = st.text_input("Pickup Address *")
                if st.form_submit_button("Submit Food Details"):
                    if not contact or not location or not food_items: st.error("⚠️ Fill Contact, Food Items, and Location!")
                    else:
                        st.session_state.db["donations"].append({"id": len(st.session_state.db["donations"]) + 1, "donor": st.session_state.current_user, "contact": contact, "items": food_items, "category": food_category, "veg_boxes": v_boxes, "veg_serves": v_serves, "nv_boxes": nv_boxes, "nv_serves": nv_serves, "location": location, "time": datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p"), "status": "Available"})
                        save_data(st.session_state.db)
                        with st.spinner("Notifying NGOs..."):
                            ngo_list = [u['email'] for u in st.session_state.db["users"] if u.get('role') == "NGO / Orphanage" and u.get('email')]
                            ngo_msg = f"Hello NGO,\n\nEmergency: Surplus Food available!\nDonor: {st.session_state.current_user}\nItems: {food_items}\nContact: {contact}\nLocation: {location}\n\nLog in to Annamithra to accept."
                            sent_count = sum(1 for ngo in ngo_list if send_email(ngo, "🚨 Surplus Food Available!", ngo_msg))
                            donor_em = next((u['email'] for u in st.session_state.db["users"] if u['username'] == st.session_state.current_user), None)
                            if donor_em: send_email(donor_em, "🙏 Thank You!", f"Dear {st.session_state.current_user},\n\nThank you for donating {food_items}. You will be notified once an NGO accepts it.")
                        st.success(f"✅ Posted Successfully! Notified {sent_count} NGOs.")
        
        with tab2:
            st.subheader("NGO Fund Requests")
            for req in st.session_state.db["fund_requests"]:
                if req.get("status") == "Active":
                    with st.expander(f"🏢 {req.get('ngo', 'NGO')} - Need: {req.get('reason', 'Help')}", expanded=True):
                        goal, raised = req.get('goal', 1), req.get('raised', 0)
                        st.write(f"**Goal:** ₹{goal} | **Raised:** ₹{raised}")
                        st.progress(min(raised / goal if goal > 0 else 0, 1.0))
                        st.info(f"**Payment:** UPI ID: `{req.get('upi', 'N/A')}`")
                        if req.get("qr_url"): st.image(req.get("qr_url"), width=150)
                        rem = goal - raised
                        if rem > 0:
                            min_d = min(100, rem)
                            amt = st.number_input("Donate (₹)", min_value=min_d, max_value=rem, step=min_d, key=f"amt_{req.get('id', 0)}")
                            if st.button(f"Donate ₹{amt}", key=f"btn_{req.get('id', 0)}"):
                                req['raised'] += amt
                                if req['raised'] >= goal: req['status'] = "Completed"
                                st.session_state.db.setdefault("fund_transactions", []).append({"donor": st.session_state.current_user, "ngo": req.get('ngo'), "amount": amt, "reason": req.get('reason'), "time": datetime.datetime.now(IST).strftime("%d %b %Y, %I:%M %p")})
                                save_data(st.session_state.db)
                                st.success(f"💖 Thank you for ₹{amt} donation!"); st.rerun()
                elif req.get("status") == "Completed":
                    with st.expander(f"✅ FULFILLED: {req.get('ngo', 'NGO')} - {req.get('reason', 'Need')}", expanded=False): st.success("Goal successfully raised!")
        
        with tab3:
            st.subheader("📜 My Donations Log")
            my_funds = [f for f in st.session_state.db.get("fund_transactions", []) if f.get("donor") == st.session_state.current_user]
            for f in reversed(my_funds): st.write(f"📅 {f.get('time')} | 💖 ₹{f.get('amount')} to {f.get('ngo')} for {f.get('reason')}")
            st.divider()
            my_dons = [d for d in st.session_state.db["donations"] if d.get("donor") == st.session_state.current_user]
            for d in reversed(my_dons): st.write(f"📅 {d.get('time')} | **Items:** {d.get('items')} | **Status:** {d.get('status')}")

    # --- NGO DASHBOARD ---
    elif st.session_state.current_role == "NGO / Orphanage":
        st.title(f"🏢 {st.session_state.current_user}")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔔 Alerts", "✅ Accepted", "📢 Request Fund", "📂 My Funds", "💖 Donors"])
        
        with tab1:
            st.subheader("Live Food Alerts")
            available = [d for d in st.session_state.db["donations"] if d.get("status") == "Available"]
            if not available: st.info("No active donations right now.")
            for idx, d in enumerate(available):
                with st.container(border=True):
                    st.write(f"📅 **Time:** {d.get('time')} | 🚨 **From:** {d.get('donor')} | 📍 **Loc:** {d.get('location')}")
                    st.write(f"🍲 **Items:** {d.get('items')} | **Cat:** {d.get('category')}")
                    if st.button(f"Accept Pickup", key=f"acc_{d.get('id', idx)}", use_container_width=True):
                        d['status'] = f"Accepted by {st.session_state.current_user}"
                        save_data(st.session_state.db)
                        # EMAIL 1: NGO ACCEPTED
                        don_em = next((u['email'] for u in st.session_state.db["users"] if u['username'] == d['donor']), None)
                        if don_em: send_email(don_em, "🎉 Your Food Donation is Accepted!", f"Hello {d['donor']},\n\nGood news! Your donation ({d['items']}) has been ACCEPTED by {st.session_state.current_user}.\nThey will coordinate via {d['contact']} for pickup.\n\nThank you,\nTeam Annamithra")
                        st.success("🎉 Accepted! Donor has been notified via Email."); st.rerun()

        with tab2:
            st.subheader("Food You Have Accepted")
            my_pickups = [d for d in st.session_state.db["donations"] if d.get("status") == f"Accepted by {st.session_state.current_user}"]
            if not my_pickups: st.info("No pending pickups.")
            for idx, d in enumerate(reversed(my_pickups)):
                with st.container(border=True):
                    st.write(f"📅 **Time:** {d.get('time')} | 🚨 **Donor:** {d.get('donor')} | 📞 **Ph:** {d.get('contact')}")
                    st.write(f"📍 **Address:** {d.get('location')} | 🍲 **Items:** {d.get('items')}")
                    # BUTTON: MARK AS RECEIVED
                    if st.button("🍽️ Mark as Food Received", key=f"recv_{d.get('id', idx)}", type="primary", use_container_width=True):
                        d['status'] = f"Received by {st.session_state.current_user}"
                        save_data(st.session_state.db)
                        # EMAIL 2: FOOD RECEIVED
                        don_em = next((u['email'] for u in st.session_state.db["users"] if u['username'] == d['donor']), None)
                        if don_em: send_email(don_em, "❤️ Food Reached the Needy!", f"Dear {d['donor']},\n\nThank you so much! The food you donated ({d['items']}) has SUCCESSFULLY REACHED the needy through {st.session_state.current_user}.\n\nYour kindness makes a huge difference.\n\nRegards,\nTeam Annamithra")
                        st.success("✅ Marked as Received! Thank you email sent to Donor."); st.rerun()

        with tab3:
            with st.form("fund_form"):
                reason, goal = st.text_input("Reason (e.g. Groceries)"), st.number_input("Target (₹)", min_value=500, step=500)
                upi, qr = st.text_input("Your UPI ID"), st.text_input("QR Code URL (Optional)")
                if st.form_submit_button("Post Request"):
                    if reason and upi:
                        st.session_state.db["fund_requests"].append({"id": len(st.session_state.db["fund_requests"]) + 1, "ngo": st.session_state.current_user, "reason": reason, "goal": goal, "raised": 0, "status": "Active", "upi": upi, "qr_url": qr})
                        save_data(st.session_state.db); st.success("✅ Posted!")
                    else: st.error("Provide Reason and UPI ID.")

        with tab4:
            st.subheader("My Fund Requests")
            for req in reversed([r for r in st.session_state.db["fund_requests"] if r.get("ngo") == st.session_state.current_user]):
                st.write(f"**{req.get('reason')}** | Status: {req.get('status')} | ₹{req.get('raised')}/₹{req.get('goal')}")

        with tab5:
            st.subheader("💖 Donors Who Supported")
            for f in reversed([f for f in st.session_state.db.get("fund_transactions", []) if f.get("ngo") == st.session_state.current_user]):
                mob = next((u.get("mobile", "N/A") for u in st.session_state.db["users"] if u["username"].lower() == f.get("donor", "").lower()), "N/A")
                st.write(f"💖 **{f.get('donor')}** donated **₹{f.get('amount')}** (Ph: {mob}) | For: {f.get('reason')}")

    # --- ADMIN DASHBOARD ---
    elif st.session_state.current_role == "Admin Portal":
        st.title("⚙️ Admin Panel")
        st.subheader("Database Overview")
        st.dataframe(st.session_state.db["users"], use_container_width=True)
        st.dataframe(st.session_state.db["donations"], use_container_width=True)
        st.dataframe(st.session_state.db["fund_requests"], use_container_width=True)
        if st.session_state.db.get("fund_transactions"): st.dataframe(st.session_state.db["fund_transactions"], use_container_width=True)
        st.divider()
        if st.button("🗑️ Clear Entire Database (Reset All)", type="primary"):
            st.session_state.db = {"users": [{"username": "Admin", "password": "5979", "role": "Admin Portal", "mobile": "Admin", "email": ""}], "donations": [], "fund_requests": [], "fund_transactions": []}
            save_data(st.session_state.db); st.success("Database wiped! Fresh start ready. Log out and log in.")
                            
