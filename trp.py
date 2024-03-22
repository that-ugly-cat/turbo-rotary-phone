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

# Initialize username in session state
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# Login form in the sidebar
with st.sidebar:
    st.title("Login")
    username_login = st.text_input("Username")
    password_login = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username_login, password_login):
            st.success("You are successfully logged in.")
            st.session_state['login_status'] = True
            st.session_state['username'] = username_login
        else:
            st.error("Username/password is incorrect.")
#### end login section

#### Main app content
if st.session_state['login_status']:
    username = st.session_state['username']
    # List users
    userlist = list(user_password_dict.keys())
    userlist.remove(username)
    users = sorted(userlist)
    
    st.title('Barbecue 🔥')
    
    tab1, tab2, tab3, tab4 = st.tabs(["Vota", "Portate principali", "Admin", "Stats"])

#### Tab 1, vote    
    with tab1:
        with st.form(key='rating_form'):
            st.subheader("Con chi hai interagito?")
            user_to_rate = st.selectbox("Scegli dalla lista:", options=users, key="user_to_rate")
            st.divider()
            
            st.subheader('Com\'è stato parlarci?')
            st.write('Hai riso, ti ha lasciato spazio, è interessante, hai scoperto cose nuove, ...')
            rating_i = st_star_rating("", maxValue=5, defaultValue=3, key="rating_i", emoticons = True)
            st.divider()
            
            st.subheader('Com\'è stata l\'attrazione?')
            st.write('Lo stile, l\'età, è il tuo tipo, ha il giusto atteggiamento ...')
            rating_p = st_star_rating("", maxValue=5, defaultValue=3, key="rating_p", emoticons = True)
            st.divider()
            
            st.subheader('Sembra che ci siano passioni in comune?')
            st.write('Vi piacciono cose simili, oppure ti interessano cose che lei/lui sa/fa, ...')
            rating_v = st_star_rating("", maxValue=5, defaultValue=3, key="rating_v", emoticons = True)
            st.divider()

            st.subheader('Siamo qui per conoscere persone nuove e interessanti...')
            exclude = st.checkbox('Escludi questa persona dal tuo pool perché la conosci già, o perché proprio non ti interessa', key="exclude")
            st.divider()
            submit_button = st.form_submit_button("Vota!", type = 'primary')

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
            st.header('Ecco il tuo menù per la serata:')
            st.write('Queste sono le persone con cui ti consigliamo di interagire per il resto della serata 😉')
            control_list = []
            for key, item in sorted_pool_dict.items(): 
                st.write(f'-  {item}')
                if '😉' in item:
                    control_list.append(1)
            if len(control_list) > 0:
                st.write('Se di fianco ad un nome vedi una faccina 😉 significa che hai fatto un\'impressione particolarmente buona.')
            st.write('\n Ora è il momento di conoscere meglio queste persone, auguri!')
        except: 
            st.write("Non abbiamo ancora creato un \"menù\" per te, abbi un attimino di pazienza :)")

#### Tab 3, admin
    with tab3:
        if username != 'admin':
            st.write('Non sei l\'admin, quindi qui non c\'è niente di interessante per te.')
        else:
            generate_pools_button = st.button("Genera pools")
            if generate_pools_button:
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
                    df_user['special_match'] = df_user['mean_score'] >= 4.5
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
                pools_button = st.button("Salva pools")
                if pools_button:
                    for pool_name, pool_data in pools_global_dict.items():
                        try:
                            doc_ref = db.collection('pools').document(pool_name)
                            doc_ref.set(pool_data)
                            st.success(f"Pool per {pool_name} generato correttamente")
                        except Exception as e:
                            st.error(f"Mmmh, qualcosa è andato storto: {e}")
                
            # calculate stats for users
            calculate_stats_button = st.button("Calcola stats")
            if calculate_stats_button:
                import pandas as pd
                ratings = list(db.collection('ratings').stream())
                ratings_l = list(map(lambda x: x.to_dict(), ratings))
                ratings_df = pd.DataFrame(ratings_l)
                # Group by 'rated_user' and calculate the mean of 'mean_score' for each user
                average_scores_df = ratings_df.groupby('rated_user')['mean_score'].mean().reset_index()
                # Sort the DataFrame by 'average score' from lowest to highest
                average_scores_df = average_scores_df.sort_values(axis=0, by='mean_score', ascending=True).reset_index()
                # calculate stats
                stats_global_dict = {}
                mean_p_score = ratings_df['rating_p'].mean()
                mean_i_score = ratings_df['rating_i'].mean()
                mean_v_score = ratings_df['rating_v'].mean()
                mean_rating = ratings_df['mean_score'].mean()
                
                for user in average_scores_df['rated_user'].tolist():
                    st.write(user)
                    df_user = ratings_df[ratings_df['rated_user'] == user]
                    
                    stat_dict_name = 'stats_' + user
                    stats_dict = {}
                    stats_dict['global_mean_p'] = mean_p_score.round(2)
                    stats_dict['global_mean_i'] = mean_i_score.round(2)
                    stats_dict['global_mean_v'] = mean_v_score.round(2)
                    stats_dict['global_mean'] = mean_rating.round(2)
                    stats_dict['stats_mean_rating_p'] = df_user['rating_p'].mean().round(2) # attrattività
                    stats_dict['stats_mean_rating_i'] = df_user['rating_i'].mean().round(2) # interazione
                    stats_dict['stats_mean_rating_v'] = df_user['rating_v'].mean().round(2) # interessi comuni
                    stats_dict['stats_mean_rating'] = df_user['mean_score'].mean().round(2) # media punteggi
                    stats_dict['excluded_by'] = len(df_user[df_user['exclude'] == True]) # esclusioni
                    stats_dict['rated_by'] = len(df_user) # rated by
                    
                    stats_global_dict[stat_dict_name] = stats_dict
                    st.write(stats_dict)
                # save stats to firebase
                stats_button = st.button("Salva stats")
                if stats_button:
                    for stat_dict_name, stats_data in stats_global_dict.items():
                        try:
                            doc_ref = db.collection('stats').document(stat_dict_name)
                            doc_ref.set(stats_data)
                            st.success(f"Stats per {stat_dict_name} generato correttamente")
                        except Exception as e:
                            st.error(f"Mmmh, qualcosa è andato storto: {e}")
                
#### Tab 4, stats
    with tab4:
        st.write('Le statistiche non servono a giudicare, ma ad offrirci la possibilità di scoprire come gli altri ci percepiscono. Questa è un\'opportunità per vederci da una nuova prospettiva, attraverso gli occhi degli altri. Le statistiche sono pensate per essere divertenti e positive, per celebrare le vostre qualità uniche e i momenti condivisi. Se volete, godetevi la scoperta!')
        st.write('Per vedere le tue statistiche ti serve una password. Chiedi a Spit')
        password_stats = st.text_input("Password per le stat", type="password")
        stats_show_button = st.button("Mostra stats")
        if stats_show_button:
            if password_stats != 'la curiosità uccise il gatto':
                st.error('Mmmh, password sbagliata.')
            else:
                import matplotlib.pyplot as plt
                import numpy as np
                try:
                    stats_name = 'stats_' + username
                    stats_ref = db.collection('stats').document(stats_name)
                    stats = stats_ref.get()
                    stats_dict = stats.to_dict()
                    
                    st.header('Le tue statistiche')
                    #st.write(stats_dict)
        
                    # Define categories and their corresponding values
                    categories = ['Attrattività', 'Interazione', 'Cose in comune']
                    stats_means = [stats_dict['stats_mean_rating_p'], stats_dict['stats_mean_rating_i'], stats_dict['stats_mean_rating_v']]
                    global_means = [stats_dict['global_mean_p'], stats_dict['global_mean_i'], stats_dict['global_mean_v']]
        
                    # The individual and global averages to be plotted as horizontal lines
                    individual_avg = stats_dict['stats_mean_rating']
                    global_avg = stats_dict['global_mean']
                    
                    # Create the bar plot
                    fig, ax = plt.subplots()
                    bar_width = 0.35
                    index = np.arange(len(categories))
                    
                    bars1 = ax.bar(index, stats_means, bar_width, label='Le tue medie')
                    bars2 = ax.bar(index + bar_width, global_means, bar_width, label='Le medie generali')
        
                    # Add horizontal lines for individual and global averages
                    ax.axhline(y=individual_avg, color='gray', linestyle='-', label='La tua media')
                    ax.axhline(y=global_avg, color='gray', linestyle='--', label='La media generale')
        
                    # Set the y-axis range from 0 to 5
                    ax.set_ylim(0, 5)
                    
                    ax.set_xlabel('Categoria')
                    ax.set_ylabel('Valutazioni')
                    ax.set_title('Valutazioni medie per categoria')
                    ax.set_xticks(index + bar_width / 2)
                    ax.set_xticklabels(categories)
                    ax.legend()
                    
                    # Display the plot
                    
                    st.pyplot(fig)
                    
                except: 
                    st.write("Non abbiamo ancora calcolato le tue statistiche, abbi un attimino di pazienza :)")

        
else:
    st.info("Please login to access the application.")

