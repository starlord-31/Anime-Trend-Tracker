from pymongo import MongoClient
import pandas as pd

# MongoDB connection details
client = MongoClient("mongodb://localhost:27017/")
db = client.anime_tracker_reviews
collection = db.reviews

# Fetch all reviews and save them as a CSV
try:
    reviews = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's `_id` field
    df = pd.DataFrame(reviews)
    df.to_csv("reviews_data.csv", index=False)
    print("Reviews data exported to reviews_data.csv")
except Exception as e:
    print(f"Error exporting data: {e}")
finally:
    client.close()
