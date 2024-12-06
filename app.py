from flask import Flask, jsonify, request
import psycopg2
from pymongo import MongoClient
import requests
import time

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
        cursor = pg_conn.cursor()
        page = 1
        while True:
            response = requests.get(f"https://api.jikan.moe/v4/anime?page={page}")
            response.raise_for_status()
            data = response.json()

            # Break the loop if no more data is returned
            if not data.get("data"):
                break

            for anime in data["data"]:
                cursor.execute(
                    """
                    INSERT INTO anime (id, title, genre, rating, synopsis, aired_start, aired_end, popularity, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        anime['mal_id'],
                        anime['title'],
                        ', '.join([g["name"] for g in anime.get("genres", [])]),
                        anime.get("score"),
                        anime.get("synopsis"),
                        anime.get("aired", {}).get("from"),
                        anime.get("aired", {}).get("to"),
                        anime.get("popularity"),
                        anime.get("type")
                    )
                )
            pg_conn.commit()
            page += 1
            time.sleep(1)  # Respect the API rate limit

        cursor.close()
        return jsonify({"message": "Anime data inserted successfully"}), 201
    except Exception as e:
        pg_conn.rollback()
        return jsonify({"error": str(e)}), 500

# Populate Reviews into MongoDB
@app.route('/api/populate/reviews', methods=['POST'])
def populate_reviews_mongo():
    """Fetch and populate reviews into MongoDB."""
    try:
        anime_id = request.json.get("anime_id")
        if not anime_id:
            return jsonify({"error": "anime_id is required"}), 400

        page = 1
        while True:
            response = requests.get(f"https://api.jikan.moe/v4/anime/{anime_id}/reviews?page={page}")
            response.raise_for_status()
            reviews = response.json().get("data", [])

            if not reviews:
                break

            for review in reviews:
                mongo_db.reviews.insert_one({
                    "anime_id": anime_id,
                    "username": review.get("user", {}).get("username", "Anonymous"),
                    "review": review.get("review", "No review available"),
                    "score": review.get("scores", {}).get("overall", 0)
                })

            page += 1
            time.sleep(1)  # Respect the API rate limit

        return jsonify({"message": f"Reviews for anime_id {anime_id} inserted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All Anime from PostgreSQL
@app.route('/api/anime', methods=['GET'])
def get_anime():
    """Retrieve all anime from PostgreSQL."""
    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT id, title, genre, rating, synopsis, aired_start, aired_end, popularity, type FROM anime")
        rows = cursor.fetchall()
        cursor.close()
        anime_list = [
            {
                "id": row[0],
                "title": row[1],
                "genre": row[2],
                "rating": row[3],
                "synopsis": row[4],
                "aired_start": row[5],
                "aired_end": row[6],
                "popularity": row[7],
                "type": row[8]
            } for row in rows
        ]
        return jsonify(anime_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Reviews for a Specific Anime from MongoDB
@app.route('/api/reviews/<int:anime_id>', methods=['GET'])
def get_reviews(anime_id):
    """Retrieve reviews for a specific anime."""
    try:
        reviews = list(mongo_db.reviews.find({"anime_id": anime_id}, {"_id": 0}))
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
