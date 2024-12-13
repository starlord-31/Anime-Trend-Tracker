#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# In[2]:


anime_data=pd.read_csv('anime_data.csv')


# In[3]:


anime_data.head()


# In[4]:


anime_data.info()


# In[5]:


anime_data.drop('aired_end', axis=1, inplace=True)
anime_data.head()


# In[6]:


review_data=pd.read_csv('review_data.csv')
review_data.head()


# In[7]:


anime_data= anime_data.dropna()


# In[8]:


anime_data['genre'] = anime_data['genre'].fillna('') 
anime_data['title'] = anime_data['title'].fillna('Unknown')


# In[9]:


anime_data['genre'] = anime_data['genre'].apply(lambda x: x.replace(',', ' '))


# In[10]:


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# In[11]:


tfidf = TfidfVectorizer(stop_words='english')
genre_matrix = tfidf.fit_transform(anime_data['genre'])


# In[12]:


title_to_index = {title: i for i, title in enumerate(anime_data['title'])}


# In[ ]:


def search_anime(query, top_n=10):
    # Case-insensitive partial match
    matches = anime_data[anime_data['title'].str.contains(query, case=False, na=False)]
    return matches.head(top_n)[['id', 'title']]


# In[13]:


def get_preference_vector(user_titles):
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
    pref_vector = np.asarray(pref_vector)  # convert np.matrix to np.ndarray
    pref_vector = pref_vector.reshape(1, -1)

    user_ratings = anime_data.iloc[indices]['rating'].dropna()
    avg_rating = user_ratings.mean() if not user_ratings.empty else None

    return pref_vector, avg_rating


# In[14]:


def recommend(user_titles, top_n=5, rating_tolerance=1.0):
    pref_vector, avg_rating = get_preference_vector(user_titles)
    if pref_vector is None:
        return pd.DataFrame()

    # Compute similarity with all anime
    sim_scores = cosine_similarity(pref_vector, genre_matrix).flatten()

    # Put results in a DataFrame
    results = anime_data.copy()
    results['similarity'] = sim_scores

    # Exclude the anime the user already likes
    results = results[~results['title'].isin([t.strip() for t in user_titles])]

    # If we have an average rating, filter to similar rating
    if avg_rating is not None and not pd.isna(avg_rating):
        # Filter results to anime within ±1 rating of the user's average rating
        results = results[results['rating'].between(avg_rating - rating_tolerance, avg_rating + rating_tolerance)]

    # Sort by similarity descending
    results = results.sort_values(by='similarity', ascending=False)

    return results.head(top_n)[['title', 'genre', 'rating', 'similarity']]


# In[28]:


if __name__ == "__main__":
    # Ask user to input one or more anime they like
    user_input = input("Enter one or more anime titles you like (comma-separated): ").strip()
    if user_input:
        user_titles = user_input.split(',')
        recommendations = recommend(user_titles, top_n=5)
        if not recommendations.empty:
            print("\nBased on your preferences, you might like:")
            print(recommendations.to_string(index=False))
        else:
            print("No recommendations found. Try different titles or data.")
    else:
        print("No input provided.")


# In[26]:


anime_data[anime_data['title'] == 'Shigatsu wa Kimi no Uso']


# In[ ]:




