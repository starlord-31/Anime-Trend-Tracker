# Anime Trend Tracker

Anime Trend Tracker is a web application that provides anime recommendations, trending anime, and other features using a combination of Flask (backend), Streamlit (frontend), Celery (worker tasks), RabbitMQ, and PostgreSQL.

## Features

1. **Anime Recommender System**:
   - Users can input their favorite anime titles to get personalized recommendations.

2. **Trending Anime**:
   - Displays the most popular anime based on predefined criteria using Celery tasks.

3. **Anime Search**:
   - Users can search for anime by title, genre, rating, or type.

4. **Backend API**:
   - RESTful API built using Flask to handle requests for recommendations, trending anime, and more.

5. **Streamlit Frontend**:
   - A simple and interactive web interface for user interaction.

## Prerequisites

- **Docker**: Ensure Docker and Docker Compose are installed on your machine.
- **Python 3.8+**: For local modifications and testing.
- **Postman or curl**: For repopulating anime and review data.

---

## Setting Up and Running Locally

Follow these steps to set up and run the project locally.

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd anime-trend-tracker
```

### Step 2: Start RabbitMQ and PostgreSQL with Docker Compose
Run the `docker-compose` file to set up the environment:
```bash
docker-compose up -d
```
This will start:
- RabbitMQ (Message Queue)
- PostgreSQL (Database)
- Backend service (Flask API)

### Step 3: Run the Celery Worker
Start the Celery worker in a separate terminal to handle tasks like fetching trending anime:
```bash
docker-compose run backend celery -A worker.app worker --loglevel=info
```

### Step 4: Populate the Databases
Repopulate the anime data and review data using `POST` requests via Postman or curl.

1. **Populate Anime Data**:
   ```bash
   curl -X POST http://localhost:5000/api/anime/populate
   ```

2. **Populate Reviews Data**:
   ```bash
   curl -X POST http://localhost:5000/api/reviews/populate
   ```

3. **Verify the Data**:
   - Use a PostgreSQL client or admin tool to check the `anime` and `reviews` tables in the database.
   - Alternatively, run GET requests on the `/api/anime` or `/api/reviews` endpoints.

### Step 5: Run the Frontend
Start the Streamlit frontend in a new terminal:
```bash
streamlit run streamlit_frontend.py
```

### Step 6: Access the Application
- **Backend**: The Flask API runs on `http://localhost:5000`.
- **Frontend**: The Streamlit frontend runs on `http://localhost:8501`.

---

## Running the Project Components

### Docker Compose Services

1. RabbitMQ (Message Queue): Handles background tasks like processing trending anime.
2. PostgreSQL (Database): Stores anime and reviews data.
3. Backend (Flask API): Processes requests from the frontend and interacts with the database.

### Celery Worker

The Celery worker processes tasks such as fetching trending anime using RabbitMQ as the broker.

Command:
```bash
docker-compose run backend celery -A worker.app worker --loglevel=info
```

---

## File Structure

```
.
├── app.py                # Flask backend application
├── worker.py             # Celery worker tasks for background processing
├── anime_recommender.py  # Recommendation logic
├── streamlit_frontend.py # Streamlit frontend application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration for backend
├── Dockerfile.streamlit  # Docker configuration for Streamlit frontend
├── docker-compose.yml    # Docker Compose for multi-service setup
├── reviews_data.csv      # Example reviews data
├── anime_data.csv        # Example anime data
├── init_anime.sql        # SQL file to initialize anime data in PostgreSQL
├── README.md             # Project documentation
```

---

## API Endpoints

1. **Recommendations**:
   - Endpoint: `/api/recommend`
   - Method: `POST`
   - Payload:
     ```json
     {
       "titles": ["Naruto", "Attack on Titan"]
     }
     ```
   - Response:
     ```json
     [
       {
         "title": "Bleach",
         "genre": "Action",
         "rating": 8.0,
         "similarity": 0.85
       }
     ]
     ```

2. **Trending Anime**:
   - Endpoint: `/api/anime/trending`
   - Method: `GET`
   - Query Parameters: `limit` (optional, default is 10).

3. **Populate Anime Data**:
   - Endpoint: `/api/anime/populate`
   - Method: `POST`

4. **Populate Reviews Data**:
   - Endpoint: `/api/reviews/populate`
   - Method: `POST`

---

## Notes

1. **MongoDB Removal**:
   - MongoDB has been removed, and data is now handled using PostgreSQL.

2. **Celery Worker**:
   - Ensure the Celery worker is running before testing trending anime tasks.

3. **Streamlit**:
   - If the frontend does not load, verify that the backend is running and accessible.

4. **RabbitMQ**:
   - RabbitMQ is essential for Celery to function. Ensure it is running and accessible.

---

## Troubleshooting

1. **RabbitMQ Errors**:
   - Ensure RabbitMQ is running on `localhost:5672` and is accessible from the backend.

2. **Database Connection Errors**:
   - Check PostgreSQL credentials in `docker-compose.yml` and `worker.py`.

3. **Frontend Issues**:
   - Verify the backend is running and that Streamlit is correctly configured.

4. **Populate Data**:
   - If anime or reviews data is missing, repopulate using the `/api/anime/populate` and `/api/reviews/populate` endpoints.

---

This README provides all steps for setting up and running the Anime Trend Tracker project locally. For any additional issues, refer to the source code or contact the maintainer.
