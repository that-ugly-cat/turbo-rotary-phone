import streamlit as st
from datetime import datetime
import numpy as np
from google.cloud import firestore # see: https://blog.streamlit.io/streamlit-firestore/
import json

#### Firebase connection
try:
    test_firebase_auth = st.secrets.firebase.type
    firebase_connected = 'yes'
    #st.write('firebase connected')
except:
    firebase_connected = 'no'
    #st.write('firebase NOT connected')

with open('auth.json', 'w') as f:
    json.dump(dict(st.secrets.firebase), f)
db = firestore.Client.from_service_account_json('auth.json')

#### User auth
users = list(db.collection('trp_users').stream())
users_list = list(map(lambda x: x.to_dict(), users))
user_password_dict = {user_dict["user"]: user_dict["password"] for user_dict in users_list}

USER_PASSWORD_PAIRS = user_password_dict

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
#### end login section

#### Main app content
if st.session_state['login_status']:
    # Mock data for user selection
    users = list(user_password_dict.keys()).remove(username)
    
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

            # submit logic
            if submit_button: 
                # Get the current time 
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                scores = [rating_p, rating_i, rating_v]
                mean_score = np.mean(scores)
                max_score = np.max(scores)
                min_score = np.min(scores)
                std_score = np.std(scores)
                
                rating_details = {
                    "rated_user": user_to_rate,
                    "rating_p": int(rating_p),
                    "rating_i": int(rating_i),
                    "rating_v": int(rating_v),
                    "exclude": exclude,
                    "mean_score": round(mean_score, 2),
                    "max_score": int(max_score),
                    "min_score": int(min_score),
                    "std_score": round(std_score, 2),
                    "timestamp": current_time
                }
        
                if exclude:
                    st.error(f"Hai deciso di non proseguire con {user_to_rate}.")
                else:
                    st.success(f"Hai valutato {user_to_rate} con {rating_p}/5 (alla persona), con {rating_i}/5 (all'interazione) e con {rating_v}/5 (alle vibes).")
                st.json(rating_details)

    with tab2:
        st.write("Your matches will be displayed here.")
else:
    st.info("Please login to access the application.")
