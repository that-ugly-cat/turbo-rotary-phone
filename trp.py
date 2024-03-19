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
    users = sorted(userlist)
    
    st.title('TRP System🔥')
    
    tab1, tab2, tab3, tab4 = st.tabs(["Vota", "Il tuo pool", "Admin", "Stats"])

#### Tab 1, vote    
    with tab1:
        with st.form(key='rating_form'):
            st.header("Vota")
            user_to_rate = st.selectbox("Scegli la persona:", options=users, key="user_to_rate")
            rating_p = st_star_rating("Attrattività", maxValue=5, defaultValue=3, key="rating_p")
            st.write('C\'è attrazione fisica ed estetica?')
            rating_i = st_star_rating("Interazione", maxValue=5, defaultValue=3, key="rating_i")
            st.write('L\'interazione nel gioco di conoscenza è stata buona?')
            rating_v = st_star_rating("Interessi comuni", maxValue=5, defaultValue=3, key="rating_v")
            st.write('Quante cose avete in comune?')
            st.write('Hai appena parlato con qualcun* che sicuramente non ti interessa, oppure che già conosci? Se vuoi, puoi escluderl* dal tuo pool selezionando questa casella.')
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
                    st.success(f"Hai valutato {user_to_rate} con {rating_p}/5 (attrazione), con {rating_i}/5 (interazione) e con {rating_v}/5 (cose in comune).")
                
                # Save rating to dataframe
                try:
                    doc_ref = db.collection('ratings').document()
                    doc_ref.set(rating_details)
                    st.success("Il tuo voto è stato registrato correttamente.")
                except Exception as e:
                    st.error(f"Mmmh, qualcosa è andato storto: {e}")
#### Tab 2, pool
    with tab2:
        try:
            pool_name = 'pool_' + username
            pool_ref = db.collection('pools').document(pool_name)
            pool = pool_ref.get()
            pool_dict = pool.to_dict()
            sorted_pool_dict = {key: pool_dict[key] for key in sorted(pool_dict)}
            st.header('Ecco il tuo pool')
            control_list = []
            for key, item in sorted_pool_dict.items(): 
                st.write(f'-  {item}')
                if '😉' in item:
                    control_list.append(1)
            if len(control_list) > 0:
                st.write('Se di fianco ad un nome vedi una faccina 😉 significa che hai fatto un\'impressione particolarmente buona.')
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
            #st.write(ratings_df)

            # Group by 'rated_user' and calculate the mean of 'mean_score' for each user
            average_scores_df = ratings_df.groupby('rated_user')['mean_score'].mean().reset_index()
            # Sort the DataFrame by 'average score' from lowest to highest
            average_scores_df = average_scores_df.sort_values(axis=0, by='mean_score', ascending=True).reset_index()
            #st.write(average_scores_df)

            # calculate pools
            pools_global_dict = {}
            for user in average_scores_df['rated_user'].tolist():
                st.write(user)
                df_user = ratings_df[ratings_df['rated_user'] == user]
                df_user = df_user[df_user['exclude'] == False]
                # Initialize the 'reciprocal' column
                df_user['reciprocal'] = None
                for index, row in df_user.iterrows():
                    # Find the reciprocal rating
                    reciprocal_rating = ratings_df[(ratings_df['rated_user'] == row['rating_user']) & (ratings_df['rating_user'] == user)]['mean_score'].values
                    # There could be multiple ratings. Here, we'll just take the first one if it exists.
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
                df_user_ordered = df_user.sort_values(by=['match_mean', 'delta_module'], ascending=[False, True])
                # Get top 5
                top_5_df = df_user_ordered.head(5)
                # create dictionary of top 5
                dict_name = 'pool_' + user
                pool_dict = {}
                for i, row in enumerate(top_5_df.itertuples(), 1):
                    key = f'recommended_{i}'
                    value = f"{row.rating_user}{' 😉' if row.special_match else ''}"
                    pool_dict[key] = value
                    
                # append pool dict to global pool dict
                pools_global_dict[dict_name] = pool_dict
                
                # show data
                st.write(df_user_ordered)
                st.write(pool_dict)
            # save pools to firebase
            pools_button = st.button("Genera pools")
            if pools_button:
                for pool_name, pool_data in pools_global_dict.items():
                    try:
                        doc_ref = db.collection('pools').document(pool_name)
                        doc_ref.set(pool_data)
                        st.success(f"Pool per {pool_name} generato correttamente")
                    except Exception as e:
                        st.error(f"Mmmh, qualcosa è andato storto: {e}")
#### Tab 4, stats
    with tab4:
        try:
            stats_name = 'stats_' + username
            stats_ref = db.collection('stats').document(stats_name)
            stats = stats_ref.get()
            stats_dict = pool.to_dict()
            
            st.header('Le tue statistiche')
            
        except: 
            st.write("Non abbiamo ancora calcolato le tue statistiche, abbi un attimino di pazienza :)")

        
else:
    st.info("Please login to access the application.")

