import pandas as pd
from sqlalchemy import create_engine

# Define database connection using SQLAlchemy
DATABASE_URI = "postgresql+psycopg2://luffy:casper@anime_tracker_postgres:5432/anime_tracker"

# Create an engine
engine = create_engine(DATABASE_URI)

# SQL Query
query = "SELECT * FROM anime"

# Export data
try:
    df = pd.read_sql(query, engine)
    df.to_csv("anime_data.csv", index=False)
    print("Anime data exported to anime_data.csv")
except Exception as e:
    print(f"Error exporting data: {e}")
