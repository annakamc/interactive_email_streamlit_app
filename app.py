import streamlit as st
from datetime import date

# Initialize session state lists for names and emails if they don't exist
if 'names' not in st.session_state:
    st.session_state['names'] = []
if 'emails' not in st.session_state:
    st.session_state['emails'] = []

# Set up the page title and description
st.title("Contact Form")
st.write("Fill out the details below:")

# Create input fields for the form
name = st.text_input("Name")
email = st.text_input("Email")
subject = st.text_input("Subject")
message = st.text_area("Message")
selected_date = st.date_input("Date", date.today())

# When the submit button is pressed, save name and email, then display submission details
if st.button("Submit"):
    if name and email:
        st.session_state.names.append(name)
        st.session_state.emails.append(email)
    st.success("Thank you for your submission!")
    st.write("**Name:**", name)
    st.write("**Email:**", email)
    st.write("**Subject:**", subject)
    st.write("**Message:**", message)
    st.write("**Date:**", selected_date)

# Display dropdowns for selecting previously submitted names and emails, if any exist
if st.session_state.names:
    selected_saved_name = st.selectbox("Select a previously submitted name", st.session_state.names)
    st.write("You selected:", selected_saved_name)
    
if st.session_state.emails:
    selected_saved_email = st.selectbox("Select a previously submitted email", st.session_state.emails)
    st.write("You selected:", selected_saved_email)
