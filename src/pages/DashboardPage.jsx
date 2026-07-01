import { BarChart3, Clock3, Film, Sparkles, Star } from "lucide-react";
import { Link } from "react-router-dom";

import { moviesApi, recommendationsApi, watchHistoryApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import MovieCard from "../components/MovieCard.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useAsync } from "../hooks/useAsync.js";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, loading, error } = useAsync(async () => {
    const [movies, history, recommendations] = await Promise.all([
      moviesApi.list({ limit: 6 }),
      watchHistoryApi.mine({ limit: 50 }),
      recommendationsApi.mine({ limit: 3 }),
    ]);
    return { movies, history, recommendations };
  }, []);

  if (loading) return <LoadingState label="Loading dashboard" />;

  const movies = data?.movies || [];
  const history = data?.history || [];
  const recommendations = data?.recommendations || [];

  return (
    <>
      <PageHeader
        eyebrow="User dashboard"
        title={`Welcome${user?.full_name ? `, ${user.full_name}` : ""}`}
        description="Track watch signals, inspect recommendation health, and keep feeding the model with ratings."
        actions={
          <Link
            to="/recommendations"
            className="rounded-lg bg-gradient-to-r from-signal to-violetSignal px-4 py-3 text-sm font-semibold text-white"
          >
            Open recommendations
          </Link>
        }
      />

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Movies loaded" value={movies.length} icon={Film} helper="Catalog preview" />
        <StatCard label="Watch events" value={history.length} icon={Clock3} helper="Your activity" />
        <StatCard
          label="Recommendations"
          value={recommendations.length}
          icon={Sparkles}
          helper="Personalized candidates"
        />
        <StatCard label="Signal quality" value="Hybrid" icon={BarChart3} helper="Content + users" />
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-[1fr_360px]">
        <div>
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 className="text-xl font-semibold text-white">Catalog preview</h2>
            <Link to="/movies" className="text-sm font-semibold text-signal hover:text-white">
              View all
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {movies.map((movie) => (
              <MovieCard key={movie.id} movie={movie} compact />
            ))}
          </div>
        </div>

        <aside className="rounded-lg border border-white/10 bg-white/[0.04] p-5">
          <div className="flex items-center gap-2">
            <Star className="h-5 w-5 text-amber-200" />
            <h2 className="text-xl font-semibold text-white">Top matches</h2>
          </div>
          <div className="mt-5 space-y-4">
            {recommendations.length ? (
              recommendations.map((item) => (
                <Link
                  key={item.movie.id}
                  to={`/movies/${item.movie.id}`}
                  className="block rounded-lg border border-white/10 bg-black/20 p-4 hover:border-signal/40"
                >
                  <p className="font-semibold text-white">{item.movie.title}</p>
                  <p className="mt-1 text-sm text-slate-400">{item.reason}</p>
                  <p className="mt-2 text-xs text-signal">
                    Final score {Math.round(item.final_score * 100)}%
                  </p>
                </Link>
              ))
            ) : (
              <EmptyState
                title="No recommendations yet"
                message="Watch or rate a few movies to build your profile."
              />
            )}
          </div>
        </aside>
      </section>
    </>
  );
}
