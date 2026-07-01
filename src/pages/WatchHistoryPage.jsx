import { Clock3 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { moviesApi, watchHistoryApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Poster from "../components/Poster.jsx";
import { formatDate, formatDuration } from "../utils/formatters.js";

export default function WatchHistoryPage() {
  const [history, setHistory] = useState([]);
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [historyResult, moviesResult] = await Promise.all([
          watchHistoryApi.mine({ limit: 100 }),
          moviesApi.list({ limit: 100 }),
        ]);
        setHistory(historyResult);
        setMovies(moviesResult);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const movieMap = useMemo(
    () => new Map(movies.map((movie) => [movie.id, movie])),
    [movies],
  );

  return (
    <>
      <PageHeader
        eyebrow="Watch history"
        title="Your recommendation signals"
        description="Completion percentage and watch duration both feed the collaborative interaction matrix."
      />

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
      {loading ? (
        <LoadingState label="Loading watch history" />
      ) : history.length ? (
        <div className="space-y-4">
          {history.map((item) => {
            const movie = movieMap.get(item.movie_id);
            return (
              <article
                key={item.id}
                className="grid gap-4 rounded-lg border border-white/10 bg-white/[0.04] p-4 sm:grid-cols-[120px_1fr]"
              >
                <Poster movie={movie} className="h-40 w-full rounded-lg object-cover sm:h-32" />
                <div className="flex flex-col justify-between gap-4">
                  <div>
                    <p className="text-lg font-semibold text-white">
                      {movie?.title || `Movie #${item.movie_id}`}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">
                      Watched {formatDate(item.watched_at)}
                    </p>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-3">
                    <Metric label="Completion" value={`${Math.round(item.completion_percentage)}%`} />
                    <Metric
                      label="Watch duration"
                      value={formatDuration(item.watch_duration_seconds)}
                    />
                    <Metric label="Movie ID" value={item.movie_id} />
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No watch history yet"
          message="Mark movies as watched to generate stronger recommendations."
        />
      )}
    </>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <Clock3 className="h-4 w-4 text-signal" />
      <p className="mt-2 text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-white">{value}</p>
    </div>
  );
}
