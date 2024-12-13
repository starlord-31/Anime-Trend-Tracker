# Anime Recommender System

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load Anime Data
def load_data():
    anime_data = pd.read_csv('anime_data.csv')
    reviews_data = pd.read_csv('reviews_data.csv')

    # Drop unnecessary columns
    anime_data.drop('aired_end', axis=1, inplace=True)

    # Handle missing values
    anime_data.dropna(inplace=True)
    anime_data['genre'] = anime_data['genre'].fillna('')
    anime_data['title'] = anime_data['title'].fillna('Unknown')

    # Clean the genre column
    anime_data['genre'] = anime_data['genre'].apply(lambda x: x.replace(',', ' '))

    return anime_data, reviews_data

# Initialize TF-IDF Vectorizer
def initialize_vectorizer(anime_data):
    tfidf = TfidfVectorizer(stop_words='english')
    genre_matrix = tfidf.fit_transform(anime_data['genre'])
    title_to_index = {title: i for i, title in enumerate(anime_data['title'])}
    return tfidf, genre_matrix, title_to_index

# Search for Anime by Title
def search_anime(query, anime_data, top_n=10):
    matches = anime_data[anime_data['title'].str.contains(query, case=False, na=False)]
    return matches.head(top_n)[['id', 'title']]

# Compute User Preference Vector
def get_preference_vector(user_titles, title_to_index, genre_matrix, anime_data):
    indices = []
    for title in user_titles:
        title = title.strip()
        if title in title_to_index:
            indices.append(title_to_index[title])
        else:
            print(f"Warning: '{title}' not found in the dataset.")

    if not indices:
        return None, None

    # Compute preference vector as average of chosen anime genre vectors
    chosen_vectors = genre_matrix[indices]
    pref_vector = chosen_vectors.mean(axis=0)
    pref_vector = np.asarray(pref_vector).reshape(1, -1)

    user_ratings = anime_data.iloc[indices]['rating'].dropna()
    avg_rating = user_ratings.mean() if not user_ratings.empty else None

    return pref_vector, avg_rating

# Recommend Anime Based on User Preferences
def recommend(user_titles, anime_data, title_to_index, genre_matrix, top_n=5, rating_tolerance=1.0):
    pref_vector, avg_rating = get_preference_vector(user_titles, title_to_index, genre_matrix, anime_data)
    if pref_vector is None:
        return pd.DataFrame()

    # Compute similarity with all anime
    sim_scores = cosine_similarity(pref_vector, genre_matrix).flatten()

    # Put results in a DataFrame
    results = anime_data.copy()
    results['similarity'] = sim_scores

    # Exclude the anime the user already likes
    results = results[~results['title'].isin([t.strip() for t in user_titles])]

    # If we have an average rating, filter to similar ratings
    if avg_rating is not None and not pd.isna(avg_rating):
        results = results[results['rating'].between(avg_rating - rating_tolerance, avg_rating + rating_tolerance)]

    # Sort by similarity descending
    results = results.sort_values(by='similarity', ascending=False)

    return results.head(top_n)[['title', 'genre', 'rating', 'similarity']]

if __name__ == "__main__":
    # Load data
    anime_data, reviews_data = load_data()

    # Initialize vectorizer and matrix
    tfidf, genre_matrix, title_to_index = initialize_vectorizer(anime_data)

    # Input from user
    user_input = input("Enter one or more anime titles you like (comma-separated): ").strip()
    if user_input:
        user_titles = user_input.split(',')
        recommendations = recommend(user_titles, anime_data, title_to_index, genre_matrix, top_n=5)
        if not recommendations.empty:
            print("\nBased on your preferences, you might like:")
            print(recommendations.to_string(index=False))
        else:
            print("No recommendations found. Try different titles or data.")
    else:
        print("No input provided.")
