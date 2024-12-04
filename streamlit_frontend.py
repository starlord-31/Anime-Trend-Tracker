import streamlit as st
import requests

# Backend API URL (Replace with your backend URL if hosted elsewhere)
API_BASE_URL = "http://127.0.0.1:5000/api"

st.title("Anime Tracker")
st.write("Welcome to the Anime Tracker app!")

# Fetch and Display Anime Data
st.header("Anime List")
try:
    response = requests.get(f"{API_BASE_URL}/anime")
    if response.status_code == 200:
        anime_list = response.json()
        for anime in anime_list:
            st.write(f"**Title**: {anime['title']}, **Genre**: {anime['genre']}, **Rating**: {anime['rating']}")
    else:
        st.error("Failed to fetch anime data.")
except Exception as e:
    st.error(f"Error fetching anime data: {e}")

# Fetch and Display Reviews
st.header("Reviews")
try:
    response = requests.get(f"{API_BASE_URL}/reviews")
    if response.status_code == 200:
        reviews = response.json()
        for review in reviews:
            st.write(f"- {review.get('review', 'No review text available')}")  # Replace 'review_text' with the actual key
    else:
        st.error("Failed to fetch reviews.")
except Exception as e:
    st.error(f"Error fetching reviews: {e}")
