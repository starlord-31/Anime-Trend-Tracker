import streamlit as st
import requests

# Backend base URL
BASE_URL = "http://localhost:5000/api"

# Streamlit application
st.set_page_config(page_title="Anime Tracker Dashboard", layout="wide")
st.title("Anime Tracker Dashboard")
st.sidebar.title("Navigation")

# Sidebar Navigation
menu = st.sidebar.radio("Go to:", ["Home", "Search Anime", "Trending Anime", "Anime Reviews", "Review Stats"])

if menu == "Home":
    st.header("Top 10 Anime by Popularity")

    response = requests.get(f"{BASE_URL}/anime/trending", params={"limit": 10}, timeout=30)

    if response.status_code == 200:
        trending_anime = response.json()
        for anime in trending_anime:
            st.subheader(anime['title'])
            st.write(f"**Genre:** {anime['genre']}")
            st.write(f"**Rating:** {anime['rating']}")
            st.write(f"**Synopsis:** {anime['synopsis']}")
            st.write(f"**Type:** {anime['type']}")
            st.write(f"**Popularity:** {anime['popularity']}")
            st.write("---")
    else:
        st.error("Failed to fetch top anime.")

elif menu == "Search Anime":
    st.header("Search Anime")
    title = st.text_input("Title")

    # Fetch genres from backend
    genre_response = requests.get(f"{BASE_URL}/anime/genres")
    if genre_response.status_code == 200:
        genres = [genre.strip() for genre in genre_response.json() if genre.strip()]
        genres.insert(0, "")  # Add an empty option
        genre = st.selectbox("Genre", genres)
    else:
        genre = ""
        st.error("Failed to fetch genres.")

    rating = st.number_input("Minimum Rating", min_value=0.0, max_value=10.0, step=0.1)
    type_ = st.selectbox("Type", ["", "TV", "Movie", "OVA", "Special", "ONA", "Music"])
    sort_by = st.selectbox("Sort By", ["popularity", "rating"])

    if st.button("Search"):
        params = {"title": title, "genre": genre, "rating": rating, "type": type_, "sort_by": sort_by}
        response = requests.get(f"{BASE_URL}/anime/search", params=params)

        if response.status_code == 200:
            anime_list = response.json()
            for anime in anime_list:
                st.subheader(anime['title'])
                st.write(f"**Genre:** {anime['genre']}")
                st.write(f"**Rating:** {anime['rating']}")
                st.write(f"**Synopsis:** {anime['synopsis']}")
                st.write(f"**Type:** {anime['type']}")
                st.write(f"**Popularity:** {anime['popularity']}")
                st.write("---")
        else:
            st.error("Failed to fetch search results.")

elif menu == "Trending Anime":
    st.header("Trending Anime")
    limit = st.number_input("Number of Trending Anime", min_value=1, value=10, step=1)

    response = requests.get(f"{BASE_URL}/anime/trending", params={"limit": limit}, timeout=30)

    if response.status_code == 200:
        trending_anime = response.json()
        for anime in trending_anime:
            st.subheader(anime['title'])
            st.write(f"**Genre:** {anime['genre']}")
            st.write(f"**Rating:** {anime['rating']}")
            st.write(f"**Synopsis:** {anime['synopsis']}")
            st.write(f"**Type:** {anime['type']}")
            st.write(f"**Popularity:** {anime['popularity']}")
            st.write("---")
    else:
        st.error("Failed to fetch trending anime.")

elif menu == "Anime Reviews":
    st.header("Anime Reviews")
    anime_id = st.number_input("Anime ID", min_value=1, step=1)

    if st.button("Get Reviews"):
        response = requests.get(f"{BASE_URL}/reviews/{anime_id}")

        if response.status_code == 200:
            reviews = response.json()
            if reviews:
                for review in reviews:
                    st.subheader(f"User: {review['username']}")
                    st.write(f"**Review:** {review['review']}")
                    st.write(f"**Score:** {review['score']}")
                    st.write("---")
            else:
                st.info("No reviews found for this anime.")
        else:
            st.error("Failed to fetch reviews.")

elif menu == "Review Stats":
    st.header("Review Stats")
    anime_id = st.number_input("Anime ID", min_value=1, step=1)

    if st.button("Get Stats"):
        response = requests.get(f"{BASE_URL}/reviews/stats/{anime_id}")

        if response.status_code == 200:
            stats = response.json()
            st.write(f"**Average Score:** {stats.get('average_score', 'N/A')}")
            st.write(f"**Total Reviews:** {stats.get('total_reviews', 0)}")
        else:
            st.error("Failed to fetch review stats.")
