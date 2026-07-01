import { RefreshCw, Sparkles, Users, Zap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { recommendationsApi } from "../api/endpoints.js";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import RecommendationReasonModal from "../components/RecommendationReasonModal.jsx";
import { cx } from "../utils/formatters.js";

const tabs = [
  { id: "personal", label: "Personalized", icon: Sparkles },
  { id: "similar", label: "Similar users", icon: Users },
  { id: "trending", label: "Trending", icon: Zap },
];

export default function RecommendationsPage() {
  const [activeTab, setActiveTab] = useState("personal");
  const [items, setItems] = useState([]);
  const [selectedReason, setSelectedReason] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async (tab = activeTab) => {
    setLoading(true);
    setError("");
    try {
      const result =
        tab === "similar"
          ? await recommendationsApi.similarUsers({ limit: 10 })
          : tab === "trending"
            ? await recommendationsApi.trending({ limit: 10 })
            : await recommendationsApi.mine({ limit: 10 });
      setItems(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    load(activeTab);
  }, [activeTab, load]);

  return (
    <>
      <PageHeader
        eyebrow="Recommendation lab"
        title="Personalized recommendations"
        description="Inspect hybrid scores, content similarity, collaborative signals, and explanation text for each movie."
        actions={
          <button
            type="button"
            onClick={() => load()}
            className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-slate-200 hover:border-signal/40 hover:text-signal"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        }
      />

      <div className="mb-6 flex flex-wrap gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cx(
                "flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-semibold",
                activeTab === tab.id
                  ? "border-signal/40 bg-signal/15 text-white"
                  : "border-white/10 bg-white/[0.04] text-slate-400 hover:text-white",
              )}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
      {loading ? (
        <LoadingState label="Ranking movies" />
      ) : items.length ? (
        <div className="space-y-5">
          {items.map((recommendation) => (
            <RecommendationCard
              key={recommendation.movie.id}
              recommendation={recommendation}
              onExplain={setSelectedReason}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No recommendations returned"
          message="Add watch history, ratings, or seed data to give the engine useful signals."
        />
      )}

      <RecommendationReasonModal
        recommendation={selectedReason}
        onClose={() => setSelectedReason(null)}
      />
    </>
  );
}
