from celery import Celery
import psycopg2

app = Celery(broker="amqp://guest:guest@rabbitmq:5672//", backend="rpc://")

# PostgreSQL Connection Parameters
PG_HOST = "anime_tracker_postgres"
PG_DB = "anime_tracker"
PG_USER = "luffy"
PG_PASSWORD = "casper"

@app.task(name="worker.get_trending_anime")
def get_trending_anime(limit=10):
    try:
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT id, title, genre, rating, synopsis, aired_start, aired_end, popularity, type "
            "FROM anime ORDER BY popularity ASC LIMIT %s", (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        pg_conn.close()

        trending_anime = [
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
        return trending_anime
    except Exception as e:
        return {"error": str(e)}
