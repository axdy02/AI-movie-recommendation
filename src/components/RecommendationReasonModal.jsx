import { X } from "lucide-react";

import ScoreBreakdown from "./ScoreBreakdown.jsx";

export default function RecommendationReasonModal({ recommendation, onClose }) {
  if (!recommendation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 py-8 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg border border-white/10 bg-panel p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-signal">
              Why this recommendation?
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              {recommendation.movie.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-white/10 p-2 text-slate-300 hover:bg-white/10 hover:text-white"
            aria-label="Close recommendation reason"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <p className="mt-5 rounded-lg border border-white/10 bg-white/[0.04] p-4 text-sm leading-6 text-slate-300">
          {recommendation.reason}
        </p>

        <div className="mt-6">
          <ScoreBreakdown recommendation={recommendation} />
        </div>
      </div>
    </div>
  );
}
