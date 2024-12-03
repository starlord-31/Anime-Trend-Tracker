import requests
import psycopg2

# Database connection details
DB_CONFIG = {
    "dbname": "anime_tracker",
    "user": "luffy",
    "password": "casper",
    "host": "127.0.0.1",
    "port": "5432"
}

# Fetch anime data from Jikan API
def fetch_anime_data():
    url = "https://api.jikan.moe/v4/anime"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to fetch anime data: {response.status_code}")
        return []

# Save anime data to PostgreSQL
def save_to_postgres(anime_list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for anime in anime_list:
            query = """
            INSERT INTO anime (title, genre, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (title) DO NOTHING;
            """
            title = anime["title"]
            genre = ", ".join([g["name"] for g in anime.get("genres", [])])
            rating = anime.get("score", None)

            cursor.execute("""
    	    INSERT INTO anime (title, genre, rating)
    	    VALUES (%s, %s, %s)
    	    ON CONFLICT (title) DO NOTHING
	    """, (title, genre, rating))

        conn.commit()
        print("Anime data saved to PostgreSQL.")
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# Main script execution
if __name__ == "__main__":
    anime_data = fetch_anime_data()
    if anime_data:
        save_to_postgres(anime_data)
