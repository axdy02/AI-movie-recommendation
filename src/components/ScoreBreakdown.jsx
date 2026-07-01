import { formatScore } from "../utils/formatters.js";

const SCORES = [
  ["content_score", "Content"],
  ["collaborative_score", "Collaborative"],
  ["rating_score", "Rating"],
  ["popularity_score", "Popularity"],
  ["freshness_score", "Freshness"],
];

export default function ScoreBreakdown({ recommendation }) {
  return (
    <div className="space-y-3">
      {SCORES.map(([key, label]) => (
        <div key={key}>
          <div className="mb-1 flex items-center justify-between text-xs text-slate-400">
            <span>{label}</span>
            <span>{formatScore(recommendation[key])}</span>
          </div>
          <div className="h-2 rounded-full bg-white/10">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-signal via-violetSignal to-emerald-300"
              style={{ width: formatScore(recommendation[key]) }}
            />
          </div>
        </div>
      ))}
      <div className="rounded-lg border border-signal/20 bg-signal/10 px-3 py-2 text-sm text-slate-200">
        Final score: <span className="font-semibold">{formatScore(recommendation.final_score)}</span>
      </div>
    </div>
  );
}
