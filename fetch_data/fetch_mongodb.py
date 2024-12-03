from pymongo import MongoClient
import requests

# MongoDB connection details
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.anime_tracker_reviews

# Fetch reviews data from Jikan API
def fetch_reviews(anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}/reviews"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to fetch reviews for anime {anime_id}: {response.status_code}")
        return []

# Save reviews to MongoDB
def save_to_mongodb(reviews, anime_id):
    for review in reviews:
        db.reviews.insert_one({
            "anime_id": anime_id,
            "review": review["review"]
        })
    print(f"Reviews saved for anime {anime_id}")

# Main script execution
if __name__ == "__main__":
    anime_id = 1  # Example anime ID
    reviews = fetch_reviews(anime_id)
    if reviews:
        save_to_mongodb(reviews, anime_id)
