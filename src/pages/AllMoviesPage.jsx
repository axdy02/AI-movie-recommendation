import { Search } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { moviesApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import MovieCard from "../components/MovieCard.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { GENRE_OPTIONS } from "../utils/preferences.js";

export default function AllMoviesPage() {
  const [movies, setMovies] = useState([]);
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadMovies = useCallback(async (searchQuery = "") => {
    setLoading(true);
    setError("");
    try {
      const result = searchQuery
        ? await moviesApi.search(searchQuery, { limit: 50 })
        : genre
          ? await moviesApi.byGenre(genre, { limit: 50 })
          : await moviesApi.list({ limit: 50 });
      setMovies(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [genre]);

  useEffect(() => {
    loadMovies();
  }, [loadMovies]);

  function handleSearch(event) {
    event.preventDefault();
    loadMovies(query);
  }

  return (
    <>
      <PageHeader
        eyebrow="Movie catalog"
        title="Browse movies"
        description="Every interaction here can become a recommendation signal: watched, liked, disliked, or rated."
      />

      <form onSubmit={handleSearch} className="mb-6 grid gap-3 lg:grid-cols-[1fr_220px_auto]">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by title, tag, genre, description"
            className="w-full rounded-lg border border-white/10 bg-white/[0.04] py-3 pl-10 pr-3 text-sm text-white outline-none focus:border-signal"
          />
        </label>
        <select
          value={genre}
          onChange={(event) => {
            setGenre(event.target.value);
            setQuery("");
          }}
          className="rounded-lg border border-white/10 bg-panel px-3 py-3 text-sm text-white outline-none focus:border-signal"
        >
          <option value="">All genres</option>
          {GENRE_OPTIONS.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="rounded-lg bg-gradient-to-r from-signal to-violetSignal px-5 py-3 text-sm font-semibold text-white"
        >
          Search
        </button>
      </form>

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
      {loading ? (
        <LoadingState label="Loading movies" />
      ) : movies.length ? (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      ) : (
        <EmptyState title="No movies found" message="Try a different search or genre filter." />
      )}
    </>
  );
}
