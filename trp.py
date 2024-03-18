import streamlit as st

# Mock data for user selection
users = ['User 1', 'User 2', 'User 3', 'User 4', 'User 5']

st.title('User Rating System')

with st.form(key='rating_form'):
    st.header("Rate a User")
    # Dropdown to select the user to rate
    user_to_rate = st.selectbox("Choose a user to rate:", options=users)

    # Slider for the rating
    rating = st.slider("Rate the user (1 = Worst, 5 = Best):", 1, 5, value=3)

    # Text input for optional comments
    comments = st.text_area("Comments (Optional):")

    # Submit button
    submit_button = st.form_submit_button("Submit Rating")

if submit_button:
    st.success(f"You rated {user_to_rate} as {rating}/5")
    if comments:
        st.info(f"Comments: {comments}")
