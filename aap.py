import streamlit as st
import datetime

# --- 1. PAGE CONFIGURATION ---
# App icon and title update
st.set_page_config(page_title="Annamithra - Food Distribution", page_icon="🤝", layout="centered")

# Initialize session state for database simulation
if 'donations' not in st.session_state:
    st.session_state.donations = []

# --- 2. SIDEBAR (ABOUT US) ---
with st.sidebar:
    # Burger theesesi Charity/Donation Box icon pettam
    st.image("https://cdn-icons-png.flaticon.com/512/3349/3349286.png", width=80)
    st.title("Annamithra")
    st.info("Our mission is to achieve zero food waste by bridging the gap between donors and NGOs.")
    st.divider()
    st.write("📍 **Operating in:** Vepagunta, AP")
    st.write("📧 contact@annamithra.org")
    st.write("© 2026 Annamithra Platform")

# --- 3. MAIN VISUAL BANNER (DONOR TO NGO CONCEPT) ---
# Ide meeru adigina theme. Okaru inkokariki food isthunna high-quality visual banner.
st.image("https://images.unsplash.com/photo-1593113565694-c700fae626d2?q=80&w=1920&auto=format&fit=crop", use_container_width=True)

# --- 4. MAIN HEADER & ANALYTICS DASHBOARD ---
st.title("🤝 Annamithra: Food Waste Management")
st.write("Connecting surplus food from individuals and restaurants directly to orphanages and NGOs.")

st.markdown("### 📊 Platform Impact")
col1, col2, col3 = st.columns(3)
col1.metric("Meals Distributed", "1,250", "+12 today")
col2.metric("Active NGOs", "45", "+2 this week")
col3.metric("Food Saved (KG)", "840", "+15 kg")
st.divider()

# --- 5. MAIN FUNCTIONALITY TABS ---
tab1, tab2 = st.tabs(["🍽️ Donate Food (Hotels/Individuals)", "🔔 NGO Dashboard"])

# TAB 1: DONOR SECTION
with tab1:
    st.header("Donate Surplus Food")
    st.write("Fill out the details below to notify nearby NGOs through the Annamithra network.")
    
    with st.form("donation_form"):
        donor_name = st.text_input("Donor / Restaurant Name")
        food_type = st.radio("Food Type", ["Veg", "Non-Veg"], horizontal=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            servings = st.number_input("Number of Persons it can serve", min_value=1, step=1)
        with col_b:
            boxes = st.number_input("Number of Items / Boxes", min_value=1, step=1)
            
        location = st.text_input("Pickup Location / Address")
        
        # Submit button with custom styling directly from Streamlit configuration
        submit_btn = st.form_submit_button("Submit Food Details", use_container_width=True)
        
        if submit_btn:
            if donor_name and location:
                donation_data = {
                    "id": len(st.session_state.donations) + 1,
                    "donor": donor_name,
                    "type": food_type,
                    "servings": servings,
                    "boxes": boxes,
                    "location": location,
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "status": "Available"
                }
                st.session_state.donations.append(donation_data)
                st.success("✅ Food details submitted! Nearby NGOs have been instantly alerted.")
            else:
                st.error("⚠️ Please fill in all required fields (Name and Location).")

# TAB 2: NGO SECTION
with tab2:
    st.header("Active Alerts for NGOs")
    st.write("View and accept nearby food pickup requests.")
    
    available_donations = [d for d in st.session_state.donations if d["status"] == "Available"]
    
    if not available_donations:
        st.info("No active food alerts at the moment.")
    else:
        for donation in available_donations:
            with st.container(border=True):
                st.markdown(f"#### 🚨 Alert from: {donation['donor']}")
                st.write(f"📍 **Location:** {donation['location']}")
                st.write(f"🍱 **Details:** {donation['type']} | Serves {donation['servings']} people | {donation['boxes']} boxes")
                st.write(f"⏰ **Time Posted:** {donation['time']}")
                
                if st.button(f"Accept Request #{donation['id']}", key=donation['id'], use_container_width=True):
                    for d in st.session_state.donations:
                        if d['id'] == donation['id']:
                            d['status'] = "Accepted"
                    st.success(f"🎉 You accepted the request from {donation['donor']}! Please arrange pickup.")
                    st.rerun()

    st.divider()
    st.subheader("✅ Completed Pickups")
    completed_donations = [d for d in st.session_state.donations if d["status"] == "Accepted"]
    if completed_donations:
        for d in completed_donations:
            st.write(f"- **{d['donor']}** (Claimed)")
    else:
        st.write("No completed pickups yet.")
        
