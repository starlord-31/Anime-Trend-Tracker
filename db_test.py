import psycopg2
from pymongo import MongoClient

# PostgreSQL Test
try:
    pg_conn = psycopg2.connect(
        database="anime_tracker",
        user="luffy",
        password="casper",
        host="127.0.0.1",
        port="5432"
    )
    print("PostgreSQL Connection Successful!")
    pg_conn.close()
except Exception as error:
    print(f"PostgreSQL Connection Failed: {error}")

# MongoDB Test
try:
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client.test
    print("MongoDB Connection Successful!")
    mongo_client.close()
except Exception as error:
    print(f"MongoDB Connection Failed: {error}")
