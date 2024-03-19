import streamlit as st
from datetime import datetime
import numpy as np
from google.cloud import firestore # see: https://blog.streamlit.io/streamlit-firestore/
import json
from streamlit_star_rating import st_star_rating

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
logins_list = list(map(lambda x: x.to_dict(), users))
user_password_dict = {user_dict["user"]: user_dict["password"] for user_dict in logins_list}

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
    # List users
    userlist = list(user_password_dict.keys())
    userlist.remove(username)
    users = userlist
    
    st.title('TRP System🔥')
    
    tab1, tab2, tab3 = st.tabs(["Vota", "Il tuo pool", "Admin"])
    
    with tab1:
        with st.form(key='rating_form'):
            st.header("Vota")
            st.write("Poche brevi informazioni sul ranking vanno qui")
            user_to_rate = st.selectbox("Scegli la persona:", options=users, key="user_to_rate")
            rating_p = st_star_rating("Attrattività", maxValue=5, defaultValue=3, key="rating_p")
            st.write('L\'attrazione fisica ed estetica')
            rating_i = st_star_rating("Interazione", maxValue=5, defaultValue=3, key="rating_i")
            st.write('La qualità dell\'interazione nel gioco di conoscenza')
            rating_v = st_star_rating("Interessi comuni", maxValue=5, defaultValue=3, key="rating_v")
            st.write('Il potenziale di proseguire con il reciproco interesse')
            st.write('Hai appena parlato con qualcuno che ti dà brutte vibes, oppure con qualcuno che gia conosci? Se vuoi, puoi escluderlo dal tuo pool')
            exclude = st.checkbox('Non voglio più interagire con questa persona', key="exclude")
            submit_button = st.form_submit_button("Vota!")

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
                    "rating_user": username,
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
                
                # Save rating to dataframe
                try:
                    doc_ref = db.collection('ratings').document()
                    doc_ref.set(rating_details)
                    st.success("Il tuo voto è stato registrato correttamente.")
                except Exception as e:
                    st.error(f"Mmmh, qualcosa è andato storto: {e}")
#### Tab 2, pool
    with tab2:
        pools = list(db.collection('pools').stream())
        pools_list = list(map(lambda x: x.to_dict(), pools))
        pools_dict = {item.pop("user"): item for item in pools_list}
        try:
            user_pool = pools_dict[username]
            st.write('Le persone che abbiamo selezionato per te sulla base del nostro bula bula algoritmico sono:')
            st.write(user_pool['recommended_1'])
            st.write(user_pool['recommended_2'])
            st.write(user_pool['recommended_3'])
            st.write(user_pool['recommended_4'])
            st.write(user_pool['recommended_5'])
            st.write('\n Ora è il momento di conoscere meglio queste persone, auguri!')
        except: 
            st.write("Non abbiamo ancora calcolato un pool per te, abbi un attimino di pazienza :)")

#### Tab 3, admin
    with tab3:
        if username != 'admin':
            st.write('Non sei l\'admin, quindi qui non c\'è niente di interessante per te.')
        else:
            import pandas as pd
            ratings = list(db.collection('ratings').stream())
            ratings_l = list(map(lambda x: x.to_dict(), ratings))
            ratings_df = pd.DataFrame(ratings_l)
            st.write(ratings_df)

            # Group by 'rated_user' and calculate the mean of 'mean_score' for each user
            average_scores_df = ratings_df.groupby('rated_user')['mean_score'].mean().reset_index()
            # Sort the DataFrame by 'average score' from lowest to highest
            average_scores_df = average_scores_df.sort_values(axis=0, by='mean_score', ascending=True).reset_index()
            st.write(average_scores_df)
            for user in average_scores_df['rated_user'].tolist():
                st.write(user)
                df_user = ratings_df[ratings_df['rated_user'] == user]
                df_user = df_user[df_user['exclude'] == False]
                # Initialize the 'reciprocal' column
                df_user['reciprocal'] = None
                for index, row in df_user.iterrows():
                    # Find the reciprocal rating
                    reciprocal_rating = ratings_df[(ratings_df['rating_user'] == row['rated_user']) & (ratings_df['rated_user'] == user)]['mean_score'].values
                    # There could be multiple ratings; choose how to handle them. Here, we'll just take the first one if it exists.
                    if len(reciprocal_rating) > 0:
                        df_user.at[index, 'reciprocal'] = reciprocal_rating[0]
                # fill Nas with 0
                df_user['reciprocal'] = df_user['reciprocal'].fillna(0)  # Replace None with 0
                # calculate mean and append as new column
                df_user['match_mean'] = df_user[['mean_score', 'reciprocal']].mean(axis=1)
                # calculate delta (module) and append as new column
                df_user['delta_module'] = (df_user['mean_score'] - df_user['reciprocal']).abs()
                # add the 'special match' column
                df_user['special_match'] = df_user['mean_score'] >= 4
                # order by mean (largest to smallest) and by delta (smallest to largest)
                df_user = df_user.sort_values(by=['match_mean', 'delta_module'], ascending=[False, True])
                # Get top 5
                # write to firebase
                st.write(df_user)

        
else:
    st.info("Please login to access the application.")

