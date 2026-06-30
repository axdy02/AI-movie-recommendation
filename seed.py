from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password
from app.database import Base, SessionLocal, engine
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.watch_history import WatchHistory


SAMPLE_PASSWORD = "password123"
BASE_TIME = datetime.now(timezone.utc) - timedelta(days=30)


MOVIES: list[dict[str, Any]] = [
    {
        "title": "Neon Pursuit",
        "description": (
            "A courier races through a cyberpunk city after stealing evidence "
            "from a crime syndicate."
        ),
        "genres": ["action", "sci fi", "thriller"],
        "tags": ["cyberpunk", "crime", "chase", "conspiracy"],
        "poster_url": "https://example.com/posters/neon-pursuit.jpg",
        "rating": 4.7,
        "release_year": 2022,
        "language": "english",
        "cast": ["Maya Chen", "Rafael Stone"],
        "duration": 6900,
        "popularity_score": 96,
    },
    {
        "title": "Shadow Protocol",
        "description": (
            "An ex-agent uncovers a covert operation linking assassins, "
            "hackers, and stolen identities."
        ),
        "genres": ["action", "thriller"],
        "tags": ["spy", "assassin", "conspiracy", "crime"],
        "poster_url": "https://example.com/posters/shadow-protocol.jpg",
        "rating": 4.5,
        "release_year": 2020,
        "language": "english",
        "cast": ["Elena Cross", "Jonah Vale"],
        "duration": 7200,
        "popularity_score": 91,
    },
    {
        "title": "Quantum Heist",
        "description": (
            "A crew uses unstable time technology to rob a vault before a "
            "rival corporation can erase them."
        ),
        "genres": ["sci fi", "action"],
        "tags": ["time travel", "heist", "team", "technology"],
        "poster_url": "https://example.com/posters/quantum-heist.jpg",
        "rating": 4.6,
        "release_year": 2021,
        "language": "english",
        "cast": ["Nora Vale", "Isaac Kim"],
        "duration": 7080,
        "popularity_score": 93,
    },
    {
        "title": "Crimson Streets",
        "description": "Two detectives chase a ruthless crime family through a city split by corruption.",
        "genres": ["crime", "thriller"],
        "tags": ["detective", "crime", "corruption", "noir"],
        "poster_url": "https://example.com/posters/crimson-streets.jpg",
        "rating": 4.4,
        "release_year": 2019,
        "language": "english",
        "cast": ["Ava Brooks", "Miles Hart"],
        "duration": 6600,
        "popularity_score": 88,
    },
    {
        "title": "Orbital Dawn",
        "description": (
            "Astronauts stranded near Jupiter discover a signal that may be "
            "humanity's first alien contact."
        ),
        "genres": ["sci fi", "drama"],
        "tags": ["space", "alien contact", "survival", "mystery"],
        "poster_url": "https://example.com/posters/orbital-dawn.jpg",
        "rating": 4.3,
        "release_year": 2023,
        "language": "english",
        "cast": ["Leah Novak", "Samir Patel"],
        "duration": 7500,
        "popularity_score": 86,
    },
    {
        "title": "The Last Archive",
        "description": (
            "A historian follows forbidden letters to expose a royal betrayal "
            "buried for centuries."
        ),
        "genres": ["drama", "mystery"],
        "tags": ["historical", "betrayal", "archive", "secrets"],
        "poster_url": "https://example.com/posters/last-archive.jpg",
        "rating": 4.1,
        "release_year": 2018,
        "language": "english",
        "cast": ["Iris Bell", "Theo Grant"],
        "duration": 6840,
        "popularity_score": 72,
    },
    {
        "title": "Laugh Track Love",
        "description": (
            "Two rival sitcom writers accidentally become roommates while "
            "competing for the same showrunner job."
        ),
        "genres": ["comedy", "romance"],
        "tags": ["workplace", "roommates", "writers", "rivals"],
        "poster_url": "https://example.com/posters/laugh-track-love.jpg",
        "rating": 3.9,
        "release_year": 2020,
        "language": "english",
        "cast": ["Mina Ray", "Leo Finch"],
        "duration": 5940,
        "popularity_score": 68,
    },
    {
        "title": "Coastal Hearts",
        "description": "A burned-out chef returns to her hometown and reconnects with a lighthouse keeper.",
        "genres": ["romance", "drama"],
        "tags": ["small town", "second chance", "chef", "healing"],
        "poster_url": "https://example.com/posters/coastal-hearts.jpg",
        "rating": 4.0,
        "release_year": 2021,
        "language": "english",
        "cast": ["Clara Wynn", "Noah Reed"],
        "duration": 6120,
        "popularity_score": 66,
    },
    {
        "title": "Forest of Whispers",
        "description": "Friends camping in an ancient forest awaken a presence that mimics their voices.",
        "genres": ["horror", "mystery"],
        "tags": ["forest", "supernatural", "survival", "voices"],
        "poster_url": "https://example.com/posters/forest-whispers.jpg",
        "rating": 4.2,
        "release_year": 2022,
        "language": "english",
        "cast": ["Jules Hart", "Priya Shah"],
        "duration": 5700,
        "popularity_score": 82,
    },
    {
        "title": "Midnight Signal",
        "description": "A radio host receives calls from the future warning her about a missing child case.",
        "genres": ["horror", "thriller"],
        "tags": ["radio", "future", "missing child", "supernatural"],
        "poster_url": "https://example.com/posters/midnight-signal.jpg",
        "rating": 4.1,
        "release_year": 2021,
        "language": "english",
        "cast": ["Tara Lane", "Owen Pike"],
        "duration": 5880,
        "popularity_score": 79,
    },
    {
        "title": "Goal Line",
        "description": (
            "A retired football captain trains a failing local team before "
            "the national qualifier."
        ),
        "genres": ["sports", "drama"],
        "tags": ["football", "team", "underdog", "coach"],
        "poster_url": "https://example.com/posters/goal-line.jpg",
        "rating": 4.0,
        "release_year": 2017,
        "language": "english",
        "cast": ["Marco Silva", "Ben Ames"],
        "duration": 6420,
        "popularity_score": 64,
    },
    {
        "title": "Summit Run",
        "description": "A climber and a medic cross a deadly mountain route to deliver an experimental cure.",
        "genres": ["adventure", "drama"],
        "tags": ["mountain", "survival", "rescue", "journey"],
        "poster_url": "https://example.com/posters/summit-run.jpg",
        "rating": 4.2,
        "release_year": 2019,
        "language": "english",
        "cast": ["Hana Park", "Eli Moore"],
        "duration": 6900,
        "popularity_score": 74,
    },
    {
        "title": "Moonlit Raga",
        "description": (
            "A classical singer and a street musician bridge family "
            "expectations through an unlikely collaboration."
        ),
        "genres": ["musical", "romance"],
        "tags": ["music", "family", "collaboration", "tradition"],
        "poster_url": "https://example.com/posters/moonlit-raga.jpg",
        "rating": 4.3,
        "release_year": 2020,
        "language": "hindi",
        "cast": ["Anika Rao", "Dev Malhotra"],
        "duration": 7200,
        "popularity_score": 77,
    },
    {
        "title": "Festival of Sparks",
        "description": "A wedding planner and a cynical photographer clash during a chaotic festival season.",
        "genres": ["comedy", "romance"],
        "tags": ["festival", "wedding", "family", "rivals"],
        "poster_url": "https://example.com/posters/festival-sparks.jpg",
        "rating": 3.8,
        "release_year": 2022,
        "language": "hindi",
        "cast": ["Riya Sen", "Arjun Mehta"],
        "duration": 6600,
        "popularity_score": 70,
    },
    {
        "title": "Desert Cipher",
        "description": (
            "A linguist and a mercenary decode symbols that point to a hidden "
            "city beneath the dunes."
        ),
        "genres": ["adventure", "mystery"],
        "tags": ["desert", "ancient code", "hidden city", "treasure"],
        "poster_url": "https://example.com/posters/desert-cipher.jpg",
        "rating": 4.1,
        "release_year": 2018,
        "language": "english",
        "cast": ["Amara Field", "Cole Rivers"],
        "duration": 7020,
        "popularity_score": 73,
    },
    {
        "title": "Pixel Knights",
        "description": (
            "Teen gamers are pulled into a fantasy game where every level "
            "changes their real lives."
        ),
        "genres": ["fantasy", "adventure"],
        "tags": ["game", "quest", "friendship", "magic"],
        "poster_url": "https://example.com/posters/pixel-knights.jpg",
        "rating": 4.0,
        "release_year": 2021,
        "language": "english",
        "cast": ["Ollie Chen", "Sofia Brooks"],
        "duration": 6300,
        "popularity_score": 76,
    },
    {
        "title": "Dragon Orchard",
        "description": (
            "A botanist discovers that her family's orchard shelters the last "
            "dragon in the valley."
        ),
        "genres": ["fantasy", "family"],
        "tags": ["dragon", "orchard", "family", "magic"],
        "poster_url": "https://example.com/posters/dragon-orchard.jpg",
        "rating": 4.2,
        "release_year": 2023,
        "language": "english",
        "cast": ["Lina Park", "Gabe West"],
        "duration": 6000,
        "popularity_score": 81,
    },
    {
        "title": "Silent Jury",
        "description": (
            "A defense attorney finds the jury in a high-profile murder trial "
            "is being blackmailed."
        ),
        "genres": ["crime", "drama", "thriller"],
        "tags": ["courtroom", "blackmail", "murder", "justice"],
        "poster_url": "https://example.com/posters/silent-jury.jpg",
        "rating": 4.5,
        "release_year": 2020,
        "language": "english",
        "cast": ["Nadia Cole", "Peter Voss"],
        "duration": 7140,
        "popularity_score": 89,
    },
    {
        "title": "Archive 7",
        "description": (
            "Investigators reopen seven cold cases after a warehouse fire "
            "reveals a pattern of disappearances."
        ),
        "genres": ["crime", "mystery"],
        "tags": ["cold case", "investigation", "disappearance", "archive"],
        "poster_url": "https://example.com/posters/archive-7.jpg",
        "rating": 4.4,
        "release_year": 2021,
        "language": "english",
        "cast": ["Mara Blake", "Ian Frost"],
        "duration": 6840,
        "popularity_score": 85,
    },
    {
        "title": "Solar Tide",
        "description": (
            "Ocean engineers race to stop a solar-powered storm system from "
            "flooding coastal megacities."
        ),
        "genres": ["sci fi", "adventure"],
        "tags": ["climate", "ocean", "technology", "disaster"],
        "poster_url": "https://example.com/posters/solar-tide.jpg",
        "rating": 4.0,
        "release_year": 2024,
        "language": "english",
        "cast": ["Ivy Stone", "Malik Reed"],
        "duration": 6960,
        "popularity_score": 84,
    },
]


USERS: list[dict[str, Any]] = [
    {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "preferences": {
            "preferred_genres": ["action", "sci fi", "thriller"],
            "preferred_tags": ["crime", "conspiracy", "cyberpunk"],
            "preferred_languages": ["english"],
        },
    },
    {
        "email": "maya@example.com",
        "full_name": "Maya Action Fan",
        "role": "user",
        "preferences": {
            "preferred_genres": ["action", "sci fi", "thriller"],
            "preferred_tags": ["crime", "heist", "cyberpunk"],
            "preferred_languages": ["english"],
        },
    },
    {
        "email": "leo@example.com",
        "full_name": "Leo Thriller Fan",
        "role": "user",
        "preferences": {
            "preferred_genres": ["action", "thriller", "crime"],
            "preferred_tags": ["crime", "assassin", "conspiracy"],
            "preferred_languages": ["english"],
        },
    },
    {
        "email": "nora@example.com",
        "full_name": "Nora Sci Fi Fan",
        "role": "user",
        "preferences": {
            "preferred_genres": ["sci fi", "action", "adventure"],
            "preferred_tags": ["technology", "space", "time travel"],
            "preferred_languages": ["english"],
        },
    },
    {
        "email": "rhea@example.com",
        "full_name": "Rhea Romance Fan",
        "role": "user",
        "preferences": {
            "preferred_genres": ["romance", "comedy", "musical"],
            "preferred_tags": ["family", "music", "wedding"],
            "preferred_languages": ["english", "hindi"],
        },
    },
]


WATCH_PLANS: dict[str, list[tuple[str, int, float]]] = {
    "maya@example.com": [
        ("Neon Pursuit", 6400, 96),
        ("Shadow Protocol", 6100, 89),
        ("Quantum Heist", 6500, 94),
        ("Crimson Streets", 5400, 82),
        ("Orbital Dawn", 4200, 58),
    ],
    "leo@example.com": [
        ("Neon Pursuit", 6100, 91),
        ("Shadow Protocol", 6600, 97),
        ("Crimson Streets", 6200, 93),
        ("Silent Jury", 5900, 86),
        ("Archive 7", 5100, 76),
    ],
    "nora@example.com": [
        ("Neon Pursuit", 6000, 90),
        ("Quantum Heist", 6800, 97),
        ("Orbital Dawn", 7000, 92),
        ("Solar Tide", 6200, 88),
        ("Pixel Knights", 3600, 55),
    ],
    "rhea@example.com": [
        ("Laugh Track Love", 5200, 91),
        ("Coastal Hearts", 5700, 94),
        ("Moonlit Raga", 6400, 90),
        ("Festival of Sparks", 6100, 88),
        ("Dragon Orchard", 3000, 50),
    ],
    "admin@example.com": [
        ("Silent Jury", 6500, 92),
        ("Archive 7", 6300, 90),
        ("Desert Cipher", 4500, 63),
    ],
}


RATING_PLANS: dict[str, list[tuple[str, float, str | None]]] = {
    "maya@example.com": [
        ("Neon Pursuit", 5.0, "liked"),
        ("Shadow Protocol", 4.6, "liked"),
        ("Quantum Heist", 4.8, "liked"),
        ("Crimson Streets", 4.2, "liked"),
        ("Laugh Track Love", 2.0, "disliked"),
    ],
    "leo@example.com": [
        ("Neon Pursuit", 4.7, "liked"),
        ("Shadow Protocol", 4.9, "liked"),
        ("Crimson Streets", 4.6, "liked"),
        ("Silent Jury", 4.8, "liked"),
        ("Forest of Whispers", 2.2, "disliked"),
    ],
    "nora@example.com": [
        ("Neon Pursuit", 4.5, "liked"),
        ("Quantum Heist", 5.0, "liked"),
        ("Orbital Dawn", 4.7, "liked"),
        ("Solar Tide", 4.3, "liked"),
        ("Festival of Sparks", 2.1, "disliked"),
    ],
    "rhea@example.com": [
        ("Laugh Track Love", 4.4, "liked"),
        ("Coastal Hearts", 4.7, "liked"),
        ("Moonlit Raga", 4.8, "liked"),
        ("Festival of Sparks", 4.5, "liked"),
        ("Shadow Protocol", 2.0, "disliked"),
    ],
    "admin@example.com": [
        ("Silent Jury", 4.7, "liked"),
        ("Archive 7", 4.5, "liked"),
        ("Desert Cipher", 3.8, None),
    ],
}


def reset_seed_data(db: Session) -> None:
    user_emails = [user["email"] for user in USERS]
    movie_titles = [movie["title"] for movie in MOVIES]
    user_ids = list(db.scalars(select(User.id).where(User.email.in_(user_emails))))
    movie_ids = list(db.scalars(select(Movie.id).where(Movie.title.in_(movie_titles))))

    if user_ids:
        db.execute(delete(UserPreference).where(UserPreference.user_id.in_(user_ids)))
        db.execute(delete(WatchHistory).where(WatchHistory.user_id.in_(user_ids)))
        db.execute(delete(Rating).where(Rating.user_id.in_(user_ids)))

    if movie_ids:
        db.execute(delete(WatchHistory).where(WatchHistory.movie_id.in_(movie_ids)))
        db.execute(delete(Rating).where(Rating.movie_id.in_(movie_ids)))
        db.execute(delete(Movie).where(Movie.id.in_(movie_ids)))

    if user_ids:
        db.execute(delete(User).where(User.id.in_(user_ids)))

    db.commit()


def create_movies(db: Session) -> dict[str, Movie]:
    movies = {movie["title"]: Movie(**movie) for movie in MOVIES}
    db.add_all(movies.values())
    db.flush()
    return movies


def create_users(db: Session) -> dict[str, User]:
    users: dict[str, User] = {}
    for user_data in USERS:
        user = User(
            email=user_data["email"],
            hashed_password=hash_password(SAMPLE_PASSWORD),
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True,
        )
        db.add(user)
        db.flush()
        preference_data = user_data["preferences"]
        db.add(
            UserPreference(
                user_id=user.id,
                preferred_genres=preference_data["preferred_genres"],
                preferred_tags=preference_data["preferred_tags"],
                preferred_languages=preference_data["preferred_languages"],
            )
        )
        users[user.email] = user
    return users


def create_activity(
    db: Session,
    *,
    users: dict[str, User],
    movies: dict[str, Movie],
) -> None:
    day_offset = 0
    for email, watch_events in WATCH_PLANS.items():
        for title, duration, completion in watch_events:
            db.add(
                WatchHistory(
                    user_id=users[email].id,
                    movie_id=movies[title].id,
                    watch_duration_seconds=duration,
                    completion_percentage=completion,
                    watched_at=BASE_TIME + timedelta(days=day_offset),
                )
            )
            day_offset += 1

    for email, rating_events in RATING_PLANS.items():
        for title, value, status in rating_events:
            db.add(
                Rating(
                    user_id=users[email].id,
                    movie_id=movies[title].id,
                    value=value,
                    status=status,
                )
            )


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        reset_seed_data(db)
        movies = create_movies(db)
        users = create_users(db)
        create_activity(db, users=users, movies=movies)
        db.commit()

    print("Seed data created.")
    print(f"Movies: {len(MOVIES)}")
    print(f"Users: {len(USERS)}")
    print(f"Sample password for all users: {SAMPLE_PASSWORD}")
    print("Try logging in as maya@example.com, leo@example.com, or nora@example.com.")
    print("Those three users intentionally overlap on action/sci-fi/crime movies.")


if __name__ == "__main__":
    seed()
