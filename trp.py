import streamlit as st

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

    #match
    match = st.checkbox('Proseguiamo?')

    # Submit button
    submit_button = st.form_submit_button("Submit Rating")

if submit_button:
    st.info(f"Hai valutato {user_to_rate} con {rating_p}/5 (alla persona) e con {rating_i}/5 (all'interazione).")
    if match:
        st.success(f"Hai deciso di proseguire con {user_to_rate}")
