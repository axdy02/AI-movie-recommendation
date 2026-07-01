import { Eye, Heart, Info, Star, ThumbsDown, ThumbsUp } from "lucide-react";
import { Link } from "react-router-dom";

import { ratingsApi, watchHistoryApi } from "../api/endpoints.js";
import { formatRating, getPrimaryGenre } from "../utils/formatters.js";
import Poster from "./Poster.jsx";

export default function MovieCard({ movie, onChanged, compact = false }) {
  async function markWatched() {
    await watchHistoryApi.create({
      movie_id: movie.id,
      watch_duration_seconds: movie.duration || 0,
      completion_percentage: 100,
    });
    onChanged?.();
  }

  async function rate(status, value) {
    await ratingsApi.create({
      movie_id: movie.id,
      value,
      status,
    });
    onChanged?.();
  }

  return (
    <article className="group overflow-hidden rounded-lg border border-white/10 bg-white/[0.04] transition hover:-translate-y-1 hover:border-signal/40 hover:bg-white/[0.07]">
      <Link to={`/movies/${movie.id}`} className="block">
        <Poster
          movie={movie}
          className={compact ? "h-44 w-full object-cover" : "h-60 w-full object-cover"}
        />
      </Link>

      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-signal">
              {getPrimaryGenre(movie)}
            </p>
            <Link
              to={`/movies/${movie.id}`}
              className="mt-1 block text-lg font-semibold text-white hover:text-signal"
            >
              {movie.title}
            </Link>
          </div>
          <div className="flex items-center gap-1 rounded-lg bg-amber-300/10 px-2 py-1 text-sm text-amber-200">
            <Star className="h-4 w-4 fill-amber-200" />
            {formatRating(movie.rating)}
          </div>
        </div>

        <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-400">
          {movie.description}
        </p>

        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <span>{movie.release_year || "Unknown year"}</span>
          <span className="h-1 w-1 rounded-full bg-slate-600" />
          <span className="capitalize">{movie.language || "Unknown"}</span>
        </div>

        <div className="mt-4 grid grid-cols-4 gap-2">
          <button
            type="button"
            onClick={markWatched}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-slate-300 hover:border-signal/40 hover:text-signal"
            title="Mark watched"
          >
            <Eye className="mx-auto h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => rate("liked", 5)}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-slate-300 hover:border-emerald-300/40 hover:text-emerald-300"
            title="Like"
          >
            <ThumbsUp className="mx-auto h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => rate("disliked", 1)}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-slate-300 hover:border-rose-300/40 hover:text-rose-300"
            title="Dislike"
          >
            <ThumbsDown className="mx-auto h-4 w-4" />
          </button>
          <Link
            to={`/movies/${movie.id}`}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-center text-slate-300 hover:border-violetSignal/40 hover:text-violet-200"
            title="Details"
          >
            <Info className="mx-auto h-4 w-4" />
          </Link>
        </div>

        {!compact ? (
          <button
            type="button"
            onClick={() => rate("liked", 4.5)}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-4 py-2 text-sm font-semibold text-white hover:opacity-90"
          >
            <Heart className="h-4 w-4" />
            Rate as a strong match
          </button>
        ) : null}
      </div>
    </article>
  );
}
