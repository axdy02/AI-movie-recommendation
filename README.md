# AI Movie Recommendation API

Production-style FastAPI backend for an AI movie recommendation system. The
project focuses on backend architecture, authentication, movie data management,
watch history, ratings, and deterministic hybrid recommendations.

This is not a frontend project and it is not a Netflix clone. The API is built
to demonstrate how recommendation data can be modeled, collected, and ranked in
a clean service-oriented FastAPI codebase.

## Project Overview

The backend lets users register, log in, browse movies, record watch history,
rate movies, and request recommendations. Admin users can manage the movie
catalog. The recommendation engine combines content-based filtering,
collaborative filtering, movie quality signals, popularity, and freshness.

The project is intentionally modular:

```text
.
|-- app/
|   |-- admin/
|   |-- auth/
|   |-- models/
|   |-- movies/
|   |-- ratings/
|   |-- recommendations/
|   |-- routers/
|   |-- schemas/
|   |-- services/
|   |-- users/
|   |-- watch_history/
|   |-- config.py
|   |-- database.py
|   `-- main.py
|-- alembic/
|-- main.py
|-- seed.py
|-- requirements.txt
`-- .env.example
```

## Tech Stack

- FastAPI for HTTP APIs and dependency injection
- SQLAlchemy ORM for database models and queries
- PostgreSQL as the production database
- Alembic for database migrations
- Pydantic for request and response schemas
- JWT access tokens for authentication
- passlib with bcrypt for password hashing
- Pytest and FastAPI TestClient for automated tests
- Optional Ollama integration for generated tags and readable explanations

## Database Schema

### users

Stores account and role data.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `email` | Unique login email |
| `hashed_password` | Bcrypt password hash |
| `full_name` | Optional display name |
| `role` | Either `user` or `admin` |
| `is_active` | Enables or disables login |
| `created_at`, `updated_at` | Audit timestamps |

Relationships: one user has many watch-history rows, many ratings, one optional
preference row, and many recommendation logs.

### movies

Stores the movie catalog.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `title` | Movie title |
| `description` | Plot or synopsis text |
| `genres` | JSON list of normalized genres |
| `tags` | JSON list of searchable topic tags |
| `poster_url` | Optional image URL |
| `rating` | Aggregate rating from 0 to 5 |
| `release_year` | Release year |
| `language` | Normalized language string |
| `cast` | JSON list of cast names |
| `duration` | Runtime in seconds |
| `popularity_score` | Popularity signal used during ranking |
| `created_at`, `updated_at` | Audit timestamps |

Relationships: one movie has many watch-history rows, ratings, and
recommendation logs.

### watch_history

Stores user engagement events.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `user_id` | Foreign key to `users.id` |
| `movie_id` | Foreign key to `movies.id` |
| `watched_at` | Time the watch event happened |
| `watch_duration_seconds` | How long the user watched |
| `completion_percentage` | Completion value from 0 to 100 |
| `created_at` | Insert timestamp |

This table feeds both content-based and collaborative recommendations.

### ratings

Stores explicit user feedback.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `user_id` | Foreign key to `users.id` |
| `movie_id` | Foreign key to `movies.id` |
| `value` | Rating from 0 to 5 |
| `status` | Optional `liked` or `disliked` signal |
| `created_at`, `updated_at` | Audit timestamps |

Each user can have only one rating per movie.

### user_preferences

Stores cold-start preference data.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `user_id` | Unique foreign key to `users.id` |
| `preferred_genres` | JSON list of genres |
| `preferred_tags` | JSON list of tags |
| `preferred_languages` | JSON list of languages |
| `created_at`, `updated_at` | Audit timestamps |

### recommendation_logs

Stores recommendation audit data for future analytics.

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `user_id` | Foreign key to `users.id` |
| `movie_id` | Foreign key to `movies.id` |
| `recommendation_score` | Stored score |
| `algorithm_version` | Version label for the algorithm |
| `reason` | Explanation shown to the user |
| `created_at` | Insert timestamp |

## API List

Base API prefix: `/api/v1`

| Method | Endpoint | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | Public | Health check |
| `POST` | `/api/v1/auth/register` | Public | Register a user |
| `POST` | `/api/v1/auth/login` | Public | Log in and receive JWT |
| `GET` | `/api/v1/auth/me` | User | Return current user |
| `GET` | `/api/v1/movies` | User | List movies |
| `GET` | `/api/v1/movies/{movie_id}` | User | Get one movie |
| `GET` | `/api/v1/movies/search?q=` | User | Search movies |
| `GET` | `/api/v1/movies/genre/{genre}` | User | Browse by genre |
| `POST` | `/api/v1/watch-history` | User | Record a watch event |
| `GET` | `/api/v1/watch-history/me` | User | List my watch history |
| `POST` | `/api/v1/ratings` | User | Create or update a rating |
| `GET` | `/api/v1/ratings/me` | User | List my ratings |
| `GET` | `/api/v1/recommendations/me` | User | Hybrid recommendations |
| `GET` | `/api/v1/recommendations/because-you-watched/{movie_id}` | User | Similar movies |
| `GET` | `/api/v1/recommendations/similar-users` | User | Collaborative results |
| `GET` | `/api/v1/recommendations/trending` | User | Popular and highly rated |
| `POST` | `/api/v1/admin/movies` | Admin | Create movie |
| `PUT` | `/api/v1/admin/movies/{movie_id}` | Admin | Update movie |
| `DELETE` | `/api/v1/admin/movies/{movie_id}` | Admin | Delete movie |
| `GET` | `/api/v1/admin/movies` | Admin | Admin movie list |
| `GET` | `/api/v1/admin/movies/{movie_id}` | Admin | Admin movie detail |

## Recommendation Algorithms

The recommendation engine lives in `app/services/recommendation_service.py`.
It returns ranked movies with score breakdowns and a human-readable `reason`.

The system combines five signals:

- `content_score`: similarity between candidate movies and watched movies
- `collaborative_score`: signal from similar users
- `rating_score`: normalized movie rating
- `popularity_score`: normalized catalog popularity
- `freshness_score`: normalized release-year freshness

All ranking signals are deterministic. Optional Ollama calls can improve text
explanations, but they do not change recommendation scores or ordering.

## Content-Based Filtering

Content-based filtering recommends movies similar to the current user's watch
history.

The algorithm:

1. Builds a text document for each movie using title, description, genres, tags,
   cast, and language.
2. Tokenizes that document into searchable lowercase terms.
3. Builds TF-IDF vectors for each movie.
4. Creates a weighted user profile from watched movies. Movies with higher
   completion percentages contribute more strongly.
5. Computes cosine similarity between the user profile and every candidate
   movie.
6. Excludes movies the user has already watched.

This works well when the user has watched enough movies to reveal content
patterns, such as "action thrillers with crime themes" or "Hindi romance with
music and family themes."

## Collaborative Filtering

Collaborative filtering recommends movies based on users with similar behavior.

The algorithm:

1. Builds a user-movie interaction matrix.
2. Adds implicit feedback from watch history:
   - completion percentage
   - positive watch duration
3. Adds explicit feedback from ratings:
   - rating value from 0 to 5
   - `liked` boosts the interaction score
   - `disliked` lowers the interaction score
4. Computes cosine similarity between the current user and other users.
5. Finds movies watched or liked by similar users.
6. Excludes movies the current user has already watched.

The seed data intentionally includes users with overlapping action, sci-fi,
thriller, and crime histories so this endpoint clearly demonstrates
collaborative filtering:

```text
GET /api/v1/recommendations/similar-users
```

## Hybrid Scoring Formula

The final recommendation score is a weighted blend:

```text
final_score =
  content_score * 0.45 +
  collaborative_score * 0.30 +
  rating_score * 0.10 +
  popularity_score * 0.10 +
  freshness_score * 0.05
```

Weights are intentionally biased toward content similarity and collaborative
behavior because those are the strongest personalization signals. Rating,
popularity, and freshness help break ties and keep recommendations useful when
personalized data is limited.

## Cold Start Handling

If a user has no watch history, the system falls back gracefully:

1. If user preferences exist, recommend movies matching preferred genres, tags,
   and languages.
2. If no preferences exist, return trending movies based on rating and
   popularity.

This keeps the recommendation endpoint useful before the user has generated
watch history or rating data.

## Ollama Usage

Ollama support is optional. The core recommendation engine works without it.

Ollama can be used for:

- generating tags from a movie description
- generating a shorter, more natural recommendation reason

Environment variables:

```env
OLLAMA_MODEL="llama3.1"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_TIMEOUT_SECONDS="1.5"
```

If Ollama is unavailable, times out, or `OLLAMA_MODEL` is empty, the backend
uses deterministic rule-based tags and explanations.

Important: Ollama is never used to rank movies. It only improves wording.

## How To Run Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE ai_movie_recommendation;
```

Apply migrations:

```bash
alembic upgrade head
```

Seed sample data:

```bash
python seed.py
```

Start the API:

```bash
uvicorn main:app --reload
```

Open the interactive docs:

```text
http://localhost:8000/docs
```

Run tests:

```bash
pytest -q
```

## Seed Data

`seed.py` creates:

- 20 movies across action, sci-fi, thriller, crime, romance, comedy, horror,
  sports, fantasy, adventure, musical, and drama
- 5 users
- realistic watch history
- ratings and liked/disliked signals
- user preferences for cold-start tests

All seeded users use this password:

```text
password123
```

Good users for testing collaborative filtering:

- `maya@example.com`
- `leo@example.com`
- `nora@example.com`

These users intentionally overlap on action, sci-fi, thriller, and crime
movies.

## Example API Responses

### Health Check

Request:

```text
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "AI Movie Recommendation API",
  "environment": "local"
}
```

### Login

Request:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"maya@example.com\",\"password\":\"password123\"}"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Movie Response

```json
{
  "id": 1,
  "title": "Neon Pursuit",
  "description": "A courier races through a cyberpunk city after stealing evidence from a crime syndicate.",
  "genres": ["action", "sci fi", "thriller"],
  "tags": ["cyberpunk", "crime", "chase", "conspiracy"],
  "poster_url": "https://example.com/posters/neon-pursuit.jpg",
  "rating": 4.7,
  "release_year": 2022,
  "language": "english",
  "cast": ["Maya Chen", "Rafael Stone"],
  "duration": 6900,
  "popularity_score": 96,
  "created_at": "2026-06-30T10:00:00Z",
  "updated_at": "2026-06-30T10:00:00Z"
}
```

### Recommendation Response

Request:

```bash
curl http://localhost:8000/api/v1/recommendations/me \
  -H "Authorization: Bearer <access_token>"
```

Response:

```json
[
  {
    "movie": {
      "id": 18,
      "title": "Silent Jury",
      "description": "A defense attorney finds the jury in a high-profile murder trial is being blackmailed.",
      "genres": ["crime", "drama", "thriller"],
      "tags": ["courtroom", "blackmail", "murder", "justice"],
      "poster_url": "https://example.com/posters/silent-jury.jpg",
      "rating": 4.5,
      "release_year": 2020,
      "language": "english",
      "cast": ["Nadia Cole", "Peter Voss"],
      "duration": 7140,
      "popularity_score": 89,
      "created_at": "2026-06-30T10:00:00Z",
      "updated_at": "2026-06-30T10:00:00Z"
    },
    "final_score": 0.6812,
    "content_score": 0.7123,
    "collaborative_score": 0.8841,
    "rating_score": 0.9,
    "popularity_score": 0.9271,
    "freshness_score": 0.9565,
    "reason": "Recommended because users with similar watch and rating patterns also liked this movie."
  }
]
```

## Interview Explanation

### Short Pitch

This project is a FastAPI backend for movie recommendations. It models users,
movies, watch history, ratings, user preferences, and recommendation logs. The
recommendation engine is hybrid: it combines content-based filtering from movie
metadata with collaborative filtering from similar users, then reranks results
with rating, popularity, and freshness signals.

### How I Would Explain The Architecture

The system separates API routing, validation schemas, SQLAlchemy models, and
business logic into different modules. FastAPI routers handle HTTP concerns,
Pydantic schemas validate request and response data, SQLAlchemy models define
the database shape, and service classes contain the actual application logic.
This makes the code easier to test and extend.

### Why Hybrid Recommendations

Content-based filtering is good when users have a clear genre or tag pattern,
but it can become narrow. Collaborative filtering is good at discovering movies
liked by similar users, but it needs enough interaction data. A hybrid approach
uses both strengths and gives better results than either method alone.

### How The Ranking Stays Deterministic

The final score is calculated from numeric signals only. TF-IDF, cosine
similarity, ratings, popularity, and freshness produce repeatable scores.
Ollama can rewrite the explanation text, but it cannot change the score or
ranking order.

### What I Would Improve Next

- Persist recommendation logs for analytics and debugging.
- Add pagination metadata to list endpoints.
- Add user preference APIs.
- Add background jobs for precomputing vectors on larger catalogs.
- Add integration tests with PostgreSQL.
