import { Edit3, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { adminApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import MovieForm from "../components/MovieForm.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Poster from "../components/Poster.jsx";

export default function AdminManageMoviesPage() {
  const [movies, setMovies] = useState([]);
  const [editingMovie, setEditingMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadMovies();
  }, []);

  async function loadMovies() {
    setLoading(true);
    setError("");
    try {
      setMovies(await adminApi.listMovies({ limit: 100 }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteMovie(movieId) {
    await adminApi.deleteMovie(movieId);
    await loadMovies();
  }

  async function updateMovie(payload) {
    await adminApi.updateMovie(editingMovie.id, payload);
    setEditingMovie(null);
    await loadMovies();
  }

  return (
    <>
      <PageHeader
        eyebrow="Admin"
        title="Manage movies"
        description="Edit catalog fields that drive search, content-based filtering, and hybrid scores."
      />

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
      {loading ? (
        <LoadingState label="Loading movies" />
      ) : movies.length ? (
        <div className="space-y-4">
          {movies.map((movie) => (
            <article
              key={movie.id}
              className="grid gap-4 rounded-lg border border-white/10 bg-white/[0.04] p-4 md:grid-cols-[120px_1fr_auto]"
            >
              <Poster movie={movie} className="h-36 w-full rounded-lg object-cover md:h-28" />
              <div>
                <p className="text-lg font-semibold text-white">{movie.title}</p>
                <p className="mt-1 line-clamp-2 text-sm text-slate-400">{movie.description}</p>
                <p className="mt-2 text-xs capitalize text-signal">
                  {(movie.genres || []).join(", ")} · {movie.release_year}
                </p>
              </div>
              <div className="flex items-center gap-2 md:flex-col md:justify-center">
                <button
                  type="button"
                  onClick={() => setEditingMovie(movie)}
                  className="rounded-lg border border-white/10 p-2 text-slate-300 hover:border-signal/40 hover:text-signal"
                  title="Edit movie"
                >
                  <Edit3 className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => deleteMovie(movie.id)}
                  className="rounded-lg border border-white/10 p-2 text-slate-300 hover:border-rose-300/40 hover:text-rose-300"
                  title="Delete movie"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState title="No movies found" message="Add the first movie to start the catalog." />
      )}

      {editingMovie ? (
        <section className="mt-8">
          <PageHeader
            eyebrow="Editing"
            title={editingMovie.title}
            description="Update the selected movie and save changes to the admin API."
          />
          <MovieForm
            key={editingMovie.id}
            initialValue={editingMovie}
            onSubmit={updateMovie}
            submitLabel="Update movie"
          />
        </section>
      ) : null}
    </>
  );
}
