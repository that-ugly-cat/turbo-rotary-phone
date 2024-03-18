import streamlit as st
import numpy as np

# Mock data for user selection
users = ['Persona 1', 'Persona 2', 'Persona 3', 'Persona 4', 'Persona 5']

st.title('TRP System🔥')

with st.form(key='rating_form'):
    st.header("La mia opinione su...")
    st.write("Poche brevi informazioni sul ranking")
    # Dropdown to select the user to rate
    user_to_rate = st.selectbox("Scegli la persona:", options=users)

    # Slider 1 for the rating
    rating_p = st.slider("Voto alla persona (1 = 😠, 5 = 🤩):", 1, 5, value=3)

    # Slider 2 for the rating
    rating_i = st.slider("Voto all'interazione (1 = 😠, 5 = 🤩):", 1, 5, value=3)

    # Slider 3 for the rating
    rating_v = st.slider("Voto alle vibes (1 = 😠, 5 = 🤩):", 1, 5, value=3)
    
    # Exclude
    st.write("Poche brevi informazioni sull'esclusione")
    exclude = st.checkbox('Non voglio più interagire con questa persona')

    # Submit button
    submit_button = st.form_submit_button("Submit Rating")

if submit_button:
    # Calculate mean, max, and min of the scores
    # Calculating mean, max, min, and standard deviation
    mean_score = np.mean(scores)
    max_score = np.max(scores)
    min_score = np.min(scores)
    std_score = np.std(scores)

    # Organizing inputs into a dictionary
    rating_details = {
        "rated_user": user_to_rate,
        "rating_p": rating_p,
        "rating_i": rating_i,
        "rating_v": rating_v,
        "exclude": exclude,
        "mean_score": mean_score,
        "max_score": max_score,
        "min_score": min_score,
        "std_score": std_score
    }
    
    if exclude:
        st.warning(f"Hai deciso di non proseguire con {user_to_rate}")
    else:
        st.success(f"Hai valutato {user_to_rate} con {rating_p}/5 (alla persona), con {rating_i}/5 (all'interazione) e con con {rating_v}/5 (alle vibes).")
  # Showing the dictionary content for debugging or confirmation
    st.json(rating_details)
