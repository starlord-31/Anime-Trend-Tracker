from flask import Flask, jsonify, request
import psycopg2
from pymongo import MongoClient
import requests

app = Flask(__name__)

# PostgreSQL Connection
try:
    pg_conn = psycopg2.connect(
        database="anime_tracker",
        user="luffy",
        password="casper",
        host="anime_tracker_postgres",  # Docker container name
        port="5432"
    )
    print("Connected to PostgreSQL")
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

# MongoDB Connection
try:
    mongo_client = MongoClient("mongodb://mongo:27017/")  # Docker container name
    mongo_db = mongo_client.anime_tracker_reviews
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Populate Anime Data into PostgreSQL
@app.route('/api/populate/anime', methods=['POST'])
def populate_anime_postgres():
    """Fetch and populate anime data into PostgreSQL."""
    try:
        response = requests.get("https://api.jikan.moe/v4/anime")
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()

        cursor = pg_conn.cursor()
        for anime in data["data"]:
            cursor.execute(
                """
                INSERT INTO anime (id, title, genre, rating)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    anime['mal_id'],
                    anime['title'],
                    ', '.join([g["name"] for g in anime.get("genres", [])]),
                    anime.get("score"),
                )
            )
        pg_conn.commit()
        cursor.close()
        return jsonify({"message": "Anime data inserted successfully"}), 201
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Request Error: {str(e)}"}), 500
    except psycopg2.Error as e:
        return jsonify({"error": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Populate Reviews into MongoDB
@app.route('/api/populate/reviews', methods=['POST'])
def populate_reviews_mongo():
    """Fetch and populate reviews into MongoDB."""
    try:
        anime_id = request.json.get("anime_id")  # Get anime_id from request body
        if not anime_id:
            return jsonify({"error": "anime_id is required"}), 400

        response = requests.get(f"https://api.jikan.moe/v4/anime/{anime_id}/reviews")
        response.raise_for_status()
        reviews = response.json()["data"]

        for review in reviews:
            mongo_db.reviews.insert_one({"anime_id": anime_id, "review": review["review"]})

        return jsonify({"message": f"Reviews for anime_id {anime_id} inserted successfully"}), 201
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Request Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All Anime from PostgreSQL
@app.route('/api/anime', methods=['GET'])
def get_anime():
    """Retrieve all anime from PostgreSQL."""
    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT id, title, genre, rating FROM anime")
        rows = cursor.fetchall()
        cursor.close()
        anime_list = [
            {"id": row[0], "title": row[1], "genre": row[2], "rating": row[3]}
            for row in rows
        ]
        return jsonify(anime_list), 200
    except psycopg2.Error as e:
        return jsonify({"error": f"Database Error: {str(e)}"}), 500

# Get All Reviews from MongoDB
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Retrieve all reviews from MongoDB."""
    try:
        reviews = list(mongo_db.reviews.find({}, {"_id": 0}))  # Exclude `_id` field
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
