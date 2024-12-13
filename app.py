from flask import Flask, jsonify, request
from celery import Celery
from anime_recommender import load_data, initialize_vectorizer, recommend
import psycopg2
from pymongo import MongoClient
import requests
import time

app = Flask(__name__)
celery = Celery(broker="amqp://guest:guest@rabbitmq:5672//", backend="rpc://")

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
                # Ensure required fields are available
                synopsis = anime.get("synopsis")
                aired_start = anime.get("aired", {}).get("from")
                
                # Skip entries with missing synopsis or aired_start
                if not synopsis or not aired_start:
                    continue

                # Insert data into PostgreSQL
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
                        synopsis,
                        aired_start,
                        anime.get("aired", {}).get("to"),
                        anime.get("popularity"),
                        anime.get("type")
                    )
                )

            # Commit changes to the database after processing each page
            pg_conn.commit()
            page += 1
            time.sleep(1)  # Respect the API rate limit

        cursor.close()
        return jsonify({"message": "Anime data inserted successfully"}), 201
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Request Error: {str(e)}"}), 500
    except psycopg2.Error as e:
        pg_conn.rollback()
        return jsonify({"error": f"Database Error: {str(e)}"}), 500
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
        page = int(request.args.get('page', 1))  # Default to page 1
        limit = int(request.args.get('limit', 10))  # Default to 10 items per page
        offset = (page - 1) * limit

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

@app.route('/api/anime/search', methods=['GET'])
def search_anime():
    """Search anime by genre, rating, or type."""
    try:
        title = request.args.get('title', '').lower()
        genre = request.args.get('genre')
        rating = request.args.get('rating')
        type_ = request.args.get('type')
        sort_by = request.args.get('sort_by', 'popularity')  # Default to popularity

        query = "SELECT id, title, genre, rating, synopsis, aired_start, aired_end, popularity, type FROM anime WHERE 1=1"
        params = []
        
        if title:
            query += " AND LOWER(title) LIKE %s"
            params.append(f"%{title}%")

        if genre:
            query += " AND genre ILIKE %s"
            params.append(f"%{genre}%")
        if rating:
            query += " AND rating >= %s"
            params.append(rating)
        if type_:
            query += " AND type = %s"
            params.append(type_)
        
        # Add sorting
        if sort_by in ['rating', 'popularity']:
            query += f" ORDER BY {sort_by} DESC"

        cursor = pg_conn.cursor()
        cursor.execute(query, params)
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

@app.route('/api/anime/trending', methods=['GET'])
def get_trending_anime():
    """Get trending anime asynchronously."""
    try:
        limit = int(request.args.get('limit', 10))  # Default to top 10
        task = celery.send_task("worker.get_trending_anime", args=[limit])
        result = task.get(timeout=10)  # Wait for the Celery task to complete
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:anime_id>', methods=['GET'])
def get_reviews_for_anime(anime_id):
    """Retrieve reviews for a specific anime."""
    try:
        reviews = list(mongo_db.reviews.find({"anime_id": anime_id}, {"_id": 0}))
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/stats/<int:anime_id>', methods=['GET'])
def get_review_stats(anime_id):
    """Get review stats for an anime."""
    try:
        pipeline = [
            {"$match": {"anime_id": anime_id}},
            {
                "$group": {
                    "_id": "$anime_id",
                    "average_score": {"$avg": "$score"},
                    "total_reviews": {"$sum": 1}
                }
            }
        ]
        stats = list(mongo_db.reviews.aggregate(pipeline))
        if stats:
            return jsonify(stats[0]), 200
        return jsonify({"error": "No reviews found for this anime"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/anime/genres', methods=['GET'])
def get_genres():
    """Retrieve a list of unique genres."""
    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT DISTINCT genre FROM anime WHERE genre IS NOT NULL")
        rows = cursor.fetchall()
        cursor.close()
        # Flatten genres and split by commas
        genres = set()
        for row in rows:
            for genre in row[0].split(', '):  # Genres are stored as comma-separated strings
                genres.add(genre.strip())
        return jsonify(sorted(genres)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        # Load anime data and initialize the recommender
        anime_data, _ = load_data()
        _, genre_matrix, title_to_index = initialize_vectorizer(anime_data)

        # Parse user input
        data = request.get_json()
        user_titles = data.get("titles", [])
        if not user_titles:
            return jsonify({"error": "No anime titles provided"}), 400

        # Generate recommendations
        recommendations = recommend(user_titles, anime_data, title_to_index, genre_matrix, top_n=5)
        if recommendations.empty:
            return jsonify({"message": "No recommendations found"}), 200

        # Return recommendations as JSON
        return recommendations.to_json(orient="records"), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
