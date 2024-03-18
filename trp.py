import streamlit as st
import numpy as np

# Mock data for user selection
users = ['Persona 1', 'Persona 2', 'Persona 3', 'Persona 4', 'Persona 5']

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
        submit_button = st.form_submit_button("Submit Rating", on_click=reset_form)

    if submit_button:
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
            "std_score": round(std_score, 2)
        }

        if exclude:
            st.error(f"Hai deciso di non proseguire con {user_to_rate}.")
        else:
            st.success(f"Hai valutato {user_to_rate} con {rating_p}/5 (alla persona), con {rating_i}/5 (all'interazione) e con {rating_v}/5 (alle vibes).")
        st.json(rating_details)

with tab2:
    st.write("Your matches will be displayed here.")
