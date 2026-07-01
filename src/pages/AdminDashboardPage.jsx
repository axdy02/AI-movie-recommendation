import { BarChart3, Film, LibraryBig, PlusCircle, Star, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { adminApi } from "../api/endpoints.js";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { useAsync } from "../hooks/useAsync.js";

export default function AdminDashboardPage() {
  const { data, loading, error } = useAsync(() => adminApi.analytics(), []);

  if (loading) return <LoadingState label="Loading admin dashboard" />;

  const totals = data?.totals || {};
  const topMovies = data?.topMovies || [];

  return (
    <>
      <PageHeader
        eyebrow="Admin dashboard"
        title="Catalog operations"
        description="Manage movies, inspect catalog coverage, and keep recommendation metadata healthy."
        actions={
          <>
            <Link
              to="/admin/movies/new"
              className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-4 py-3 text-sm font-semibold text-white"
            >
              <PlusCircle className="h-4 w-4" />
              Add movie
            </Link>
            <Link
              to="/admin/analytics"
              className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-slate-200 hover:text-signal"
            >
              <BarChart3 className="h-4 w-4" />
              Analytics
            </Link>
          </>
        }
      />

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Movies" value={totals.movies ?? "Ready"} icon={Film} helper="Catalog records" />
        <StatCard label="Users" value={totals.users ?? "API pending"} icon={Users} helper="Needs admin metrics endpoint" />
        <StatCard
          label="Watch events"
          value={totals.watchEvents ?? "API pending"}
          icon={LibraryBig}
          helper="Needs admin metrics endpoint"
        />
        <StatCard label="Ratings" value={totals.ratings ?? "API pending"} icon={Star} helper="Feedback volume" />
      </section>

      <section className="mt-8 rounded-lg border border-white/10 bg-white/[0.04] p-6">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-xl font-semibold text-white">Top catalog items</h2>
          <Link to="/admin/movies" className="text-sm font-semibold text-signal hover:text-white">
            Manage movies
          </Link>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {topMovies.map((movie) => (
            <div key={movie.id} className="rounded-lg border border-white/10 bg-black/20 p-4">
              <p className="font-semibold text-white">{movie.title}</p>
              <p className="mt-1 text-sm text-slate-400">
                {movie.release_year} · {movie.genres?.join(", ")}
              </p>
              <p className="mt-2 text-xs text-signal">Popularity {movie.popularity_score}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
