import psycopg2

try:
    # Connect to PostgreSQL
    connection = psycopg2.connect(
        database="anime_tracker",
        user="luffy",
        password="casper",
        host="127.0.0.1",
        port="5432"
    )
    print("Database connection successful!")
except Exception as error:
    print(f"Error: {error}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("Database connection closed.")
