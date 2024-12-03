from flask import Flask, jsonify
import psycopg2
from pymongo import MongoClient

app = Flask(__name__)

# PostgreSQL Connection
pg_conn = psycopg2.connect(
    database="anime_tracker",
    user="luffy",
    password="casper",
    host="127.0.0.1",
    port="5432"
)

# MongoDB Connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client.anime_tracker_reviews


@app.route('/api/anime', methods=['GET'])
def get_anime():
    """Retrieve all anime from PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        cursor.execute("SELECT id, title, genre, rating FROM anime")
        rows = cursor.fetchall()
        anime_list = [
            {"id": row[0], "title": row[1], "genre": row[2], "rating": row[3]}
            for row in rows
        ]
        return jsonify(anime_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Retrieve all reviews from MongoDB"""
    try:
        reviews = list(mongo_db.reviews.find({}, {"_id": 0}))  # Exclude the `_id` field
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
