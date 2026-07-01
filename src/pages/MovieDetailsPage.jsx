import { Clock3, Eye, Heart, Star, ThumbsDown, ThumbsUp } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { moviesApi, ratingsApi, recommendationsApi, watchHistoryApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Poster from "../components/Poster.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import RecommendationReasonModal from "../components/RecommendationReasonModal.jsx";
import { formatDuration } from "../utils/formatters.js";

export default function MovieDetailsPage() {
  const { movieId } = useParams();
  const [movie, setMovie] = useState(null);
  const [related, setRelated] = useState([]);
  const [selectedReason, setSelectedReason] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [movieResult, relatedResult] = await Promise.all([
          moviesApi.get(movieId),
          recommendationsApi.becauseYouWatched(movieId, { limit: 3 }),
        ]);
        setMovie(movieResult);
        setRelated(relatedResult);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [movieId]);

  async function markWatched(completion = 100) {
    await watchHistoryApi.create({
      movie_id: movie.id,
      watch_duration_seconds: movie.duration || 0,
      completion_percentage: completion,
    });
  }

  async function rate(status, value) {
    await ratingsApi.create({ movie_id: movie.id, value, status });
  }

  if (loading) return <LoadingState label="Loading movie details" />;
  if (error) return <EmptyState title="Could not load movie" message={error} />;
  if (!movie) return <EmptyState title="Movie not found" message="The movie was not returned by the API." />;

  return (
    <>
      <PageHeader
        eyebrow="Movie details"
        title={movie.title}
        description={movie.description}
      />

      <section className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <Poster movie={movie} className="h-[520px] w-full rounded-lg object-cover" />
        <div className="rounded-lg border border-white/10 bg-white/[0.04] p-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Detail icon={Star} label="Rating" value={Number(movie.rating || 0).toFixed(1)} />
            <Detail icon={Clock3} label="Duration" value={formatDuration(movie.duration)} />
            <Detail label="Year" value={movie.release_year || "Unknown"} />
            <Detail label="Language" value={movie.language || "Unknown"} />
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {(movie.genres || []).map((genre) => (
              <span key={genre} className="rounded-full bg-signal/10 px-3 py-1 text-sm capitalize text-signal">
                {genre}
              </span>
            ))}
            {(movie.tags || []).map((tag) => (
              <span key={tag} className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-300">
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-6">
            <h2 className="text-lg font-semibold text-white">Cast</h2>
            <p className="mt-2 text-sm text-slate-400">{(movie.cast || []).join(", ") || "Unknown"}</p>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-4">
            <ActionButton icon={Eye} label="Watched" onClick={() => markWatched(100)} />
            <ActionButton icon={ThumbsUp} label="Like" onClick={() => rate("liked", 5)} />
            <ActionButton icon={ThumbsDown} label="Dislike" onClick={() => rate("disliked", 1)} />
            <ActionButton icon={Heart} label="Rate 4.5" onClick={() => rate("liked", 4.5)} />
          </div>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="mb-4 text-2xl font-semibold text-white">Because you watched {movie.title}</h2>
        {related.length ? (
          <div className="space-y-5">
            {related.map((item) => (
              <RecommendationCard
                key={item.movie.id}
                recommendation={item}
                onExplain={setSelectedReason}
              />
            ))}
          </div>
        ) : (
          <EmptyState title="No similar movies yet" message="The API did not return related recommendations." />
        )}
      </section>

      <RecommendationReasonModal
        recommendation={selectedReason}
        onClose={() => setSelectedReason(null)}
      />
    </>
  );
}

function Detail({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-4">
      {Icon ? <Icon className="h-4 w-4 text-signal" /> : null}
      <p className="mt-3 text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-semibold capitalize text-white">{value}</p>
    </div>
  );
}

function ActionButton({ icon: Icon, label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-slate-200 hover:border-signal/40 hover:text-signal"
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}
