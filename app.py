import streamlit as st
from datetime import date, datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import pandas as pd

# -----------------------------
# Email sending and scheduling functions
# -----------------------------
def send_email(to_email, subject, message, smtp_username, smtp_password, smtp_server, smtp_port):
    """Send an email using SMTP."""
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

def schedule_email(send_datetime, to_email, subject, message, smtp_username, smtp_password, smtp_server, smtp_port):
    """Wait until the scheduled datetime and then send the email."""
    now = datetime.now()
    delay = (send_datetime - now).total_seconds()
    if delay > 0:
        print(f"Email scheduled to be sent in {delay:.0f} seconds.")
        time.sleep(delay)
    else:
        print("The scheduled time is in the past. Sending email immediately.")
    send_email(to_email, subject, message, smtp_username, smtp_password, smtp_server, smtp_port)

# -----------------------------
# Email account configurations with placeholder credentials
# -----------------------------
email_accounts = {
    "Gmail Account": {
        "username": "soccerislife.love03@gmail.com",      # Replace with your Gmail address
        "password": "your_gmail_password",           # Replace with your Gmail password or app password
        "server": "smtp.gmail.com",
        "port": 587,
    },
    "BYU-I Account": {
        "username": "your_byui@example.com",         # Replace with your BYU-I email address
        "password": "your_byui_password",            # Replace with your BYU-I password or app password
        "server": "smtp.mail.byui.com",
        "port": 587,
    }
}

# -----------------------------
# Initialize session state for data entries, names, and emails if they don't exist
# -----------------------------
if "data_entries" not in st.session_state:
    st.session_state["data_entries"] = []  # Each entry is a dict with keys: name, email, class
if "names" not in st.session_state:
    st.session_state["names"] = []
if "emails" not in st.session_state:
    st.session_state["emails"] = []

# -----------------------------
# Create two tabs: one for Email Fill-out and one for Data Input
# -----------------------------
tab1, tab2 = st.tabs(["Email Fill-out", "Data Input"])

# -----------------------------
# Tab 2: Data Input - add new data entries (Name, Email, Class) with a table output and delete option
# -----------------------------
with tab2:
    st.header("Data Input")
    st.write("Enter a new data entry (Name, Email, Class):")
    
    new_name = st.text_input("Name", key="new_name")
    new_email = st.text_input("Email", key="new_email")
    new_class = st.text_input("Class", key="new_class")
    
    if st.button("Add Entry"):
        if new_name and new_email and new_class:
            new_entry = {"name": new_name, "email": new_email, "class": new_class}
            st.session_state.data_entries.append(new_entry)
            st.success("Entry added!")
        else:
            st.error("Please fill in all fields.")
    
    if st.session_state.data_entries:
        st.write("### Current Data Entries:")
        # Create a DataFrame for a tabular display
        df = pd.DataFrame(st.session_state.data_entries)
        st.dataframe(df)

        st.write("### Delete an Entry:")
        # Display each entry with a Delete button in a table-like format
        for idx, entry in enumerate(st.session_state.data_entries):
            col1, col2, col3, col4 = st.columns([3, 4, 3, 2])
            with col1:
                st.write(entry["name"])
            with col2:
                st.write(entry["email"])
            with col3:
                st.write(entry["class"])
            with col4:
                if st.button("Delete", key=f"delete_{idx}"):
                    st.session_state.data_entries.pop(idx)
                    st.experimental_rerun()

# -----------------------------
# Tab 1: Email Fill-out - form to send an email
# -----------------------------
with tab1:
    st.header("Email Fill-out Form")
    st.write("Fill out the email details below:")

    # Sender email account selection
    selected_account = st.selectbox("Select Sender Email Account", list(email_accounts.keys()))
    smtp_config = email_accounts[selected_account]
    st.write("Default sender email:", smtp_config["username"])

    # Data Entry selection dropdown (optional)
    data_entries = st.session_state.get("data_entries", [])
    entry_options = ["None"] + [f"{entry['name']} - {entry['email']} - {entry['class']}" for entry in data_entries]
    selected_data = st.selectbox("Select Data Entry (Optional)", entry_options, key="selected_data")
    
    # Determine default values for Name and Recipient Email from the selected data entry, if any.
    if selected_data != "None":
        idx = entry_options.index(selected_data) - 1  # adjust for "None" option
        selected_entry = data_entries[idx]
        name_default = selected_entry["name"]
        recipient_email_default = selected_entry["email"]
    else:
        name_default = ""
        recipient_email_default = ""
    
    # Email form fields with defaults from selected data entry if available.
    name = st.text_input("Name", value=name_default, key="name_input")
    # last_name_input = st.text_input("Last Name", value="", key="last_name_input")
    # If last name is blank, take everything after the first space in the full name.
    if name.strip() != "":
        if name.strip():
            parts = name.split(" ", 1)
            last_name = parts[1] if len(parts) > 1 else ""
        else:
            last_name = ""
    else:
        last_name = name
    st.write("Last Name:", last_name)
    
    recipient_email = st.text_input("Recipient Email", value=recipient_email_default, key="recipient_email_input")
    subject_input = st.text_input("Subject", value="Disability Accomodation Update/Extension", key="subject_input")
    message_input = st.text_area(
        "Message", 
        value=f"Hi Professor {last_name}, \n\nI wanted to reach out regarding some of my assignments in this class. Due to my health issues, I am currently in pain and cannot complete the assignments on time. Because of this, I may need to use my disability accommodations to request an extension for the project. I’ll do my best to turn it in on time, but today's pain is a lot higher than I expected so I just wanted to reach out early to keep you updated.\n\nThanks so much for your patience,\nFalone Mabila", 
        key="message_input"
    )
    send_date = st.date_input("Send On (Date)", date.today(), key="send_date")
    send_time = st.time_input("Send On (Army Time)", datetime.now().time(), key="send_time")
    
    if st.button("Submit Email"):
        # Save submitted name and recipient email to session state lists
        if name and recipient_email:
            st.session_state.names.append(name)
            st.session_state.emails.append(recipient_email)
        
        st.success("Thank you for your submission!")
        st.write("**Name:**", name)
        st.write("**Recipient Email:**", recipient_email)
        st.write("**Subject:**", subject_input)
        st.write("**Message:**", message_input)
        st.write("**Scheduled Send:**", f"{send_date} {send_time}")
        st.write("**Using Sender Account:**", selected_account)
        
        # Combine date and time into a single datetime object
        send_datetime = datetime.combine(send_date, send_time)
        
        # Start a background thread to schedule the email so that the UI remains responsive
        threading.Thread(
            target=schedule_email,
            args=(
                send_datetime,
                recipient_email,
                subject_input,
                message_input,
                smtp_config["username"],
                smtp_config["password"],
                smtp_config["server"],
                smtp_config["port"],
            ),
            daemon=True,
        ).start()
        
        st.write("Your email is scheduled to be sent at:", send_datetime)
    
    # Optionally, display dropdowns for previously submitted names and emails
    # if st.session_state.names:
    #     selected_saved_name = st.selectbox("Select a previously submitted name", st.session_state.names, key="saved_name")
    #     st.write("You selected:", selected_saved_name)
    # if st.session_state.emails:
    #     selected_saved_email = st.selectbox("Select a previously submitted email", st.session_state.emails, key="saved_email")
    #     st.write("You selected:", selected_saved_email)
