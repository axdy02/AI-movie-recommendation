import {
  defaultPreferences,
  mockMovies,
  mockRatings,
  mockUsers,
  mockWatchHistory,
} from "./mockData.js";

const MOCK_TOKEN_KEY = "ai_movie_access_token";

const state = {
  users: [...mockUsers],
  movies: [...mockMovies],
  watchHistory: [...mockWatchHistory],
  ratings: [...mockRatings],
  preferences: {
    2: defaultPreferences,
  },
};

function delay(value, ms = 180) {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(value), ms);
  });
}

function toPublicUser(user) {
  if (!user) return null;
  const { password: _password, ...publicUser } = user;
  return publicUser;
}

function currentUser() {
  const token = window.sessionStorage.getItem(MOCK_TOKEN_KEY);
  if (!token?.startsWith("mock-token-")) return null;
  const userId = Number(token.replace("mock-token-", ""));
  return state.users.find((user) => user.id === userId) || null;
}

function requireUser() {
  const user = currentUser();
  if (!user) throw new Error("Not authenticated.");
  return user;
}

function now() {
  return new Date().toISOString();
}

function scoreMovie(movie, index = 0) {
  const content = Math.max(0.25, 0.88 - index * 0.05);
  const collaborative = Math.max(0.12, 0.72 - index * 0.04);
  const rating = movie.rating / 5;
  const popularity = movie.popularity_score / 100;
  const freshness = Math.min(1, (movie.release_year - 1888) / (2026 - 1888));
  const final =
    content * 0.45 +
    collaborative * 0.3 +
    rating * 0.1 +
    popularity * 0.1 +
    freshness * 0.05;

  return {
    movie,
    final_score: Number(final.toFixed(4)),
    content_score: Number(content.toFixed(4)),
    collaborative_score: Number(collaborative.toFixed(4)),
    rating_score: Number(rating.toFixed(4)),
    popularity_score: Number(popularity.toFixed(4)),
    freshness_score: Number(freshness.toFixed(4)),
    reason:
      "Recommended because users with similar watch and rating patterns also liked this movie.",
  };
}

function getUnwatchedMovies(userId) {
  const watchedIds = new Set(
    state.watchHistory
      .filter((item) => item.user_id === userId)
      .map((item) => item.movie_id),
  );
  return state.movies.filter((movie) => !watchedIds.has(movie.id));
}

function buildAnalytics() {
  const genreCounts = new Map();
  const ratingByGenre = new Map();
  for (const movie of state.movies) {
    for (const genre of movie.genres) {
      genreCounts.set(genre, (genreCounts.get(genre) || 0) + 1);
      const bucket = ratingByGenre.get(genre) || { total: 0, count: 0 };
      bucket.total += movie.rating;
      bucket.count += 1;
      ratingByGenre.set(genre, bucket);
    }
  }

  return {
    totals: {
      movies: state.movies.length,
      users: state.users.length,
      watchEvents: state.watchHistory.length,
      ratings: state.ratings.length,
    },
    genreDistribution: [...genreCounts.entries()].map(([genre, count]) => ({
      genre,
      count,
    })),
    ratingByGenre: [...ratingByGenre.entries()].map(([genre, item]) => ({
      genre,
      rating: Number((item.total / item.count).toFixed(2)),
    })),
    topMovies: [...state.movies]
      .sort((left, right) => right.popularity_score - left.popularity_score)
      .slice(0, 6),
  };
}

export const mockApi = {
  async login({ email, password }) {
    const user = state.users.find(
      (item) => item.email === email && item.password === password,
    );
    if (!user) throw new Error("Incorrect email or password.");
    const token = `mock-token-${user.id}`;
    window.sessionStorage.setItem(MOCK_TOKEN_KEY, token);
    return delay({ access_token: token, token_type: "bearer", expires_in: 1800 });
  },

  async register(payload) {
    const exists = state.users.some((user) => user.email === payload.email);
    if (exists) throw new Error("Email already registered.");
    const user = {
      id: state.users.length + 1,
      email: payload.email,
      password: payload.password,
      full_name: payload.full_name || "",
      role: "user",
      is_active: true,
      created_at: now(),
      updated_at: now(),
    };
    state.users.push(user);
    const token = `mock-token-${user.id}`;
    window.sessionStorage.setItem(MOCK_TOKEN_KEY, token);
    return delay({
      user: toPublicUser(user),
      token: { access_token: token, token_type: "bearer", expires_in: 1800 },
    });
  },

  async me() {
    return delay(toPublicUser(requireUser()));
  },

  async listMovies({ offset = 0, limit = 50 } = {}) {
    return delay(state.movies.slice(offset, offset + limit));
  },

  async searchMovies(query) {
    const normalized = query.toLowerCase();
    return delay(
      state.movies.filter((movie) =>
        [movie.title, movie.description, ...movie.genres, ...movie.tags]
          .join(" ")
          .toLowerCase()
          .includes(normalized),
      ),
    );
  },

  async moviesByGenre(genre) {
    const normalized = genre.toLowerCase();
    return delay(
      state.movies.filter((movie) =>
        movie.genres.some((item) => item.toLowerCase() === normalized),
      ),
    );
  },

  async movie(movieId) {
    const movie = state.movies.find((item) => item.id === Number(movieId));
    if (!movie) throw new Error("Movie not found.");
    return delay(movie);
  },

  async createMovie(payload) {
    requireUser();
    const movie = {
      ...payload,
      id: Math.max(...state.movies.map((item) => item.id)) + 1,
      created_at: now(),
      updated_at: now(),
    };
    state.movies.unshift(movie);
    return delay(movie);
  },

  async updateMovie(movieId, payload) {
    requireUser();
    const index = state.movies.findIndex((movie) => movie.id === Number(movieId));
    if (index === -1) throw new Error("Movie not found.");
    state.movies[index] = {
      ...state.movies[index],
      ...payload,
      updated_at: now(),
    };
    return delay(state.movies[index]);
  },

  async deleteMovie(movieId) {
    requireUser();
    state.movies = state.movies.filter((movie) => movie.id !== Number(movieId));
    return delay(null);
  },

  async recordWatch(payload) {
    const user = requireUser();
    const item = {
      id: state.watchHistory.length + 1,
      user_id: user.id,
      movie_id: payload.movie_id,
      watched_at: payload.watched_at || now(),
      watch_duration_seconds: payload.watch_duration_seconds || 0,
      completion_percentage: payload.completion_percentage || 0,
      created_at: now(),
    };
    state.watchHistory.unshift(item);
    return delay(item);
  },

  async myWatchHistory() {
    const user = requireUser();
    return delay(
      state.watchHistory.filter((item) => item.user_id === user.id),
    );
  },

  async rateMovie(payload) {
    const user = requireUser();
    const existing = state.ratings.find(
      (item) => item.user_id === user.id && item.movie_id === payload.movie_id,
    );
    if (existing) {
      existing.value = payload.value;
      existing.status = payload.status;
      existing.updated_at = now();
      return delay(existing);
    }
    const rating = {
      id: state.ratings.length + 1,
      user_id: user.id,
      created_at: now(),
      updated_at: now(),
      ...payload,
    };
    state.ratings.unshift(rating);
    return delay(rating);
  },

  async myRatings() {
    const user = requireUser();
    return delay(state.ratings.filter((item) => item.user_id === user.id));
  },

  async recommendations({ limit = 10 } = {}) {
    const user = requireUser();
    return delay(getUnwatchedMovies(user.id).slice(0, limit).map(scoreMovie));
  },

  async becauseYouWatched(movieId, { limit = 10 } = {}) {
    const source = state.movies.find((movie) => movie.id === Number(movieId));
    const sourceGenres = new Set(source?.genres || []);
    return delay(
      state.movies
        .filter(
          (movie) =>
            movie.id !== Number(movieId) &&
            movie.genres.some((genre) => sourceGenres.has(genre)),
        )
        .slice(0, limit)
        .map((movie, index) => ({
          ...scoreMovie(movie, index),
          reason: `Recommended because it is similar to ${source?.title}.`,
        })),
    );
  },

  async similarUsers({ limit = 10 } = {}) {
    requireUser();
    return delay(state.movies.slice(3, 3 + limit).map(scoreMovie));
  },

  async trending({ limit = 10 } = {}) {
    return delay(
      [...state.movies]
        .sort((left, right) => right.popularity_score - left.popularity_score)
        .slice(0, limit)
        .map((movie, index) => ({
          ...scoreMovie(movie, index),
          content_score: 0,
          collaborative_score: 0,
          reason: "Trending because it has strong ratings and popularity.",
        })),
    );
  },

  async getPreferences() {
    const user = requireUser();
    return delay(state.preferences[user.id] || defaultPreferences);
  },

  async updatePreferences(payload) {
    const user = requireUser();
    state.preferences[user.id] = payload;
    return delay(payload);
  },

  async analytics() {
    requireUser();
    return delay(buildAnalytics());
  },
};
