import { HelpCircle, Star } from "lucide-react";
import { Link } from "react-router-dom";

import { formatScore } from "../utils/formatters.js";
import Poster from "./Poster.jsx";
import ScoreBreakdown from "./ScoreBreakdown.jsx";

export default function RecommendationCard({ recommendation, onExplain }) {
  const { movie } = recommendation;

  return (
    <article className="overflow-hidden rounded-lg border border-white/10 bg-white/[0.04]">
      <div className="grid gap-0 md:grid-cols-[220px_1fr]">
        <Link to={`/movies/${movie.id}`} className="block">
          <Poster movie={movie} className="h-64 w-full object-cover md:h-full" />
        </Link>
        <div className="p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-signal">
                Final score {formatScore(recommendation.final_score)}
              </p>
              <Link
                to={`/movies/${movie.id}`}
                className="mt-2 block text-2xl font-semibold text-white hover:text-signal"
              >
                {movie.title}
              </Link>
              <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-400">
                {movie.description}
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-1 rounded-lg bg-amber-300/10 px-3 py-2 text-amber-200">
              <Star className="h-4 w-4 fill-amber-200" />
              {Number(movie.rating || 0).toFixed(1)}
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {(movie.genres || []).map((genre) => (
              <span
                key={genre}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs capitalize text-slate-300"
              >
                {genre}
              </span>
            ))}
          </div>

          <p className="mt-4 rounded-lg border border-white/10 bg-black/20 p-3 text-sm leading-6 text-slate-300">
            {recommendation.reason}
          </p>

          <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_auto] lg:items-end">
            <ScoreBreakdown recommendation={recommendation} />
            <button
              type="button"
              onClick={() => onExplain(recommendation)}
              className="flex items-center justify-center gap-2 rounded-lg border border-signal/30 bg-signal/10 px-4 py-3 text-sm font-semibold text-signal hover:bg-signal/15"
            >
              <HelpCircle className="h-4 w-4" />
              Why?
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
