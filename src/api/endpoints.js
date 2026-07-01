import { apiClient, rootClient, USE_MOCKS } from "./axios.js";
import { mockApi } from "./mockApi.js";
import { getLocalPreferences, saveLocalPreferences } from "../utils/preferences.js";

function params(options = {}) {
  return { params: options };
}

export const healthApi = {
  async check() {
    if (USE_MOCKS) {
      return {
        status: "ok",
        service: "AI Movie Recommendation API",
        environment: "mock",
      };
    }
    const { data } = await rootClient.get("/health");
    return data;
  },
};

export const authApi = {
  async login(payload) {
    if (USE_MOCKS) return mockApi.login(payload);
    const { data } = await apiClient.post("/auth/login", payload);
    return data;
  },

  async register(payload) {
    if (USE_MOCKS) return mockApi.register(payload);
    const { data } = await apiClient.post("/auth/register", payload);
    return data;
  },

  async me() {
    if (USE_MOCKS) return mockApi.me();
    const { data } = await apiClient.get("/auth/me");
    return data;
  },
};

export const moviesApi = {
  async list(options) {
    if (USE_MOCKS) return mockApi.listMovies(options);
    const { data } = await apiClient.get("/movies", params(options));
    return data;
  },

  async search(query, options) {
    if (USE_MOCKS) return mockApi.searchMovies(query, options);
    const { data } = await apiClient.get(
      "/movies/search",
      params({ q: query, ...options }),
    );
    return data;
  },

  async byGenre(genre, options) {
    if (USE_MOCKS) return mockApi.moviesByGenre(genre, options);
    const { data } = await apiClient.get(
      `/movies/genre/${encodeURIComponent(genre)}`,
      params(options),
    );
    return data;
  },

  async get(movieId) {
    if (USE_MOCKS) return mockApi.movie(movieId);
    const { data } = await apiClient.get(`/movies/${movieId}`);
    return data;
  },
};

export const adminApi = {
  async listMovies(options) {
    if (USE_MOCKS) return mockApi.listMovies(options);
    const { data } = await apiClient.get("/admin/movies", params(options));
    return data;
  },

  async createMovie(payload) {
    if (USE_MOCKS) return mockApi.createMovie(payload);
    const { data } = await apiClient.post("/admin/movies", payload);
    return data;
  },

  async updateMovie(movieId, payload) {
    if (USE_MOCKS) return mockApi.updateMovie(movieId, payload);
    const { data } = await apiClient.put(`/admin/movies/${movieId}`, payload);
    return data;
  },

  async deleteMovie(movieId) {
    if (USE_MOCKS) return mockApi.deleteMovie(movieId);
    await apiClient.delete(`/admin/movies/${movieId}`);
    return null;
  },

  async analytics() {
    if (USE_MOCKS) return mockApi.analytics();
    const movies = await this.listMovies({ limit: 100 });
    return buildCatalogAnalytics(movies);
  },
};

export const watchHistoryApi = {
  async create(payload) {
    if (USE_MOCKS) return mockApi.recordWatch(payload);
    const { data } = await apiClient.post("/watch-history", payload);
    return data;
  },

  async mine(options) {
    if (USE_MOCKS) return mockApi.myWatchHistory(options);
    const { data } = await apiClient.get("/watch-history/me", params(options));
    return data;
  },
};

export const ratingsApi = {
  async create(payload) {
    if (USE_MOCKS) return mockApi.rateMovie(payload);
    const { data } = await apiClient.post("/ratings", payload);
    return data;
  },

  async mine(options) {
    if (USE_MOCKS) return mockApi.myRatings(options);
    const { data } = await apiClient.get("/ratings/me", params(options));
    return data;
  },
};

export const recommendationsApi = {
  async mine(options) {
    if (USE_MOCKS) return mockApi.recommendations(options);
    const { data } = await apiClient.get("/recommendations/me", params(options));
    return data;
  },

  async becauseYouWatched(movieId, options) {
    if (USE_MOCKS) return mockApi.becauseYouWatched(movieId, options);
    const { data } = await apiClient.get(
      `/recommendations/because-you-watched/${movieId}`,
      params(options),
    );
    return data;
  },

  async similarUsers(options) {
    if (USE_MOCKS) return mockApi.similarUsers(options);
    const { data } = await apiClient.get(
      "/recommendations/similar-users",
      params(options),
    );
    return data;
  },

  async trending(options) {
    if (USE_MOCKS) return mockApi.trending(options);
    const { data } = await apiClient.get("/recommendations/trending", params(options));
    return data;
  },
};

export const preferencesApi = {
  async get(userId) {
    if (USE_MOCKS) return mockApi.getPreferences();
    return getLocalPreferences(userId);
  },

  async update(userId, payload) {
    if (USE_MOCKS) return mockApi.updatePreferences(payload);
    saveLocalPreferences(userId, payload);
    return payload;
  },
};

function buildCatalogAnalytics(movies) {
  const genreMap = new Map();
  const ratingMap = new Map();

  for (const movie of movies) {
    for (const genre of movie.genres || []) {
      genreMap.set(genre, (genreMap.get(genre) || 0) + 1);
      const bucket = ratingMap.get(genre) || { total: 0, count: 0 };
      bucket.total += movie.rating || 0;
      bucket.count += 1;
      ratingMap.set(genre, bucket);
    }
  }

  return {
    totals: {
      movies: movies.length,
      users: null,
      watchEvents: null,
      ratings: null,
    },
    genreDistribution: [...genreMap.entries()].map(([genre, count]) => ({
      genre,
      count,
    })),
    ratingByGenre: [...ratingMap.entries()].map(([genre, item]) => ({
      genre,
      rating: Number((item.total / item.count).toFixed(2)),
    })),
    topMovies: [...movies]
      .sort((left, right) => right.popularity_score - left.popularity_score)
      .slice(0, 6),
  };
}
