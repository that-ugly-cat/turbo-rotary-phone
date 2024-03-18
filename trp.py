import streamlit as st
from datetime import datetime
import numpy as np

# Define users and passwords (for demonstration purposes only)
# WARNING: This is not secure and is for demonstration only. Consider using a secure password handling and verification system.
USER_PASSWORD_PAIRS = {
    "user1": "password1",
    "user2": "password2"
}

# Function to verify login credentials
def check_login(username, password):
    return USER_PASSWORD_PAIRS.get(username) == password

# Login state check
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

# Login form in the sidebar
with st.sidebar:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.success("You are successfully logged in.")
            st.session_state['login_status'] = True
        else:
            st.error("Username/password is incorrect.")

# Main app content
if st.session_state['login_status']:
    st.title('TRP System🔥')
    
    tab1, tab2 = st.tabs(["Rate Users", "Your Matches"])
    
    with tab1:
        with st.form(key='rating_form'):
            st.header("La mia opinione su...")
            st.write("Poche brevi informazioni sul ranking")
            user_to_rate = st.selectbox("Scegli la persona:", options=users, key="user_to_rate")
            rating_p = st.slider("Voto alla persona (1 = 😠, 5 = 🤩):", 1, 5, value=3, key="rating_p")
            rating_i = st.slider("Voto all'interazione (1 = 😠, 5 = 🤩):", 1, 5, value=3, key="rating_i")
            rating_v = st.slider("Voto alle vibes (1 = 😠, 5 = 🤩):", 1, 5, value=3, key="rating_v")
            st.write("Poche brevi informazioni sull'esclusione")
            exclude = st.checkbox('Non voglio più interagire con questa persona', key="exclude")
            submit_button = st.form_submit_button("Submit Rating")
    
        # Your existing logic for handling form submission
        # ...

    with tab2:
        st.write("Your matches will be displayed here.")
else:
    st.info("Please login to access the application.")
