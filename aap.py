import streamlit as st
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Annamithra - Food Distribution", layout="centered")

# Initialize session state to act as our database for food donations
if 'donations' not in st.session_state:
    st.session_state.donations = []

# --- MAIN HEADER ---
st.title("🍲 Annamithra: Food Waste Management")
st.write("Connecting surplus food with NGOs and orphanages to eliminate waste.")

# Create tabs for the Donor and the NGO/Orphanage
tab1, tab2 = st.tabs(["Donate Food (Hotels/Individuals)", "NGO Dashboard"])

# --- TAB 1: DONOR SECTION ---
with tab1:
    st.header("Donate Surplus Food")
    st.write("Fill out the details below to notify nearby NGOs through the Annamithra network.")
    
    with st.form("donation_form"):
        donor_name = st.text_input("Donor/Restaurant Name")
        food_type = st.radio("Food Type", ["Veg", "Non-Veg"])
        
        col1, col2 = st.columns(2)
        with col1:
            servings = st.number_input("Number of Persons it can serve", min_value=1, step=1)
        with col2:
            boxes = st.number_input("Number of Items/Boxes", min_value=1, step=1)
            
        location = st.text_input("Location / Address")
        
        submit_btn = st.form_submit_button("Submit Food Details")
        
        if submit_btn:
            if donor_name and location:
                # Save the data to our session state "database"
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
                st.success("✅ Food details submitted! Nearby NGOs have been alerted via Annamithra.")
            else:
                st.error("Please fill in all required fields (Name and Location).")

# --- TAB 2: NGO SECTION ---
with tab2:
    st.header("🔔 Active Alerts for NGOs")
    st.write("View and accept nearby food pickup requests.")
    
    available_donations = [d for d in st.session_state.donations if d["status"] == "Available"]
    
    if not available_donations:
        st.info("No active food alerts at the moment.")
    else:
        for donation in available_donations:
            with st.container():
                st.markdown(f"### Alert from: {donation['donor']}")
                st.write(f"📍 **Location:** {donation['location']}")
                st.write(f"🍱 **Details:** {donation['type']} | Serves {donation['servings']} people | {donation['boxes']} boxes/items")
                st.write(f"⏰ **Time Posted:** {donation['time']}")
                
                # Button to accept the request
                if st.button(f"Accept Request #{donation['id']}", key=donation['id']):
                    # Update status
                    for d in st.session_state.donations:
                        if d['id'] == donation['id']:
                            d['status'] = "Accepted"
                    st.success(f"🎉 You have successfully accepted the request from {donation['donor']}! Please arrange for pickup.")
                    st.rerun()

    # Show accepted history
    st.divider()
    st.subheader("Completed Pickups")
    completed_donations = [d for d in st.session_state.donations if d["status"] == "Accepted"]
    if completed_donations:
        for d in completed_donations:
            st.write(f"✅ {d['donor']} - Claimed")
    else:
        st.write("No completed pickups yet.")
