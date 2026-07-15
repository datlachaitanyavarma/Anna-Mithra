import streamlit as st
import smtplib
from email.message import EmailMessage

# --- Email Configuration ---
EMAIL_USER = "AnnaMithra.alert@gmail.com"
EMAIL_PASS = "uoqisnadymhiyiqy" # App Password

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- Main App Interface ---
st.title("AnnaMithra: Food Donation Portal")

menu = ["NGO Registration", "Donate Food"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "NGO Registration":
    st.subheader("NGO Registration")
    with st.form("ngo_registration_form"):
        ngo_name = st.text_input("NGO Name")
        mobile = st.text_input("Mobile Number (Mandatory)")
        email = st.text_input("Email ID (Mandatory)")
        register_btn = st.form_submit_button("Register")
    
    if register_btn:
        if not mobile or not email:
            st.warning("⚠️ Both Mobile Number and Email ID are mandatory!")
        else:
            st.success(f"✅ Registration Successful for {ngo_name}!")

elif choice == "Donate Food":
    st.subheader("Food Donation Form")
    with st.form("food_donation_form"):
        donor_name = st.text_input("Your Name")
        donor_email = st.text_input("Your Email (Mandatory)")
        food_item = st.text_input("Food Item Name")
        quantity = st.text_input("Quantity (e.g., 5kg)")
        ngo_email = st.text_input("NGO Contact Email (Mandatory)")
        submit = st.form_submit_button("Submit & Notify")

    if submit:
        if not donor_email or not ngo_email or not food_item or not quantity:
            st.warning("⚠️ All fields are mandatory!")
        else:
            with st.spinner("Processing your donation..."):
                # 1. Alert to NGO
                msg_ngo = f"Hello NGO,\n\nNew donation received from {donor_name}.\n\nDetails:\nItem: {food_item}\nQuantity: {quantity}\n\nPlease check the dashboard to coordinate the pickup."
                ngo_sent = send_email(ngo_email, "🚨 New Donation Alert!", msg_ngo)
                
                # 2. Thank you mail to Donor
                msg_donor = f"Dear {donor_name},\n\nThank you for your generous donation of {food_item} ({quantity}).\nYour contribution will significantly help those in need.\n\nRegards,\nTeam AnnaMithra"
                donor_sent = send_email(donor_email, "🙏 Thank You for your Donation!", msg_donor)
                
                if ngo_sent and donor_sent:
                    st.success("✅ Donation submitted successfully! Emails sent to both NGO and Donor.")
                else:
                    st.error("❌ Email process failed. Please check the email addresses.")
                    
