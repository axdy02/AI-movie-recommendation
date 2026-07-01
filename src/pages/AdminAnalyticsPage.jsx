import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { adminApi } from "../api/endpoints.js";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { useAsync } from "../hooks/useAsync.js";

export default function AdminAnalyticsPage() {
  const { data, loading, error } = useAsync(() => adminApi.analytics(), []);

  if (loading) return <LoadingState label="Loading analytics" />;

  const totals = data?.totals || {};

  return (
    <>
      <PageHeader
        eyebrow="Admin analytics"
        title="Recommendation data overview"
        description="Catalog analytics are available from existing movie APIs. User-wide engagement metrics need a backend admin analytics endpoint."
      />

      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Movies" value={totals.movies ?? 0} helper="Catalog size" />
        <StatCard label="Users" value={totals.users ?? "Pending"} helper="Needs API support" />
        <StatCard label="Watch events" value={totals.watchEvents ?? "Pending"} helper="Needs API support" />
        <StatCard label="Ratings" value={totals.ratings ?? "Pending"} helper="Needs API support" />
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-2">
        <ChartPanel title="Genre distribution">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data?.genreDistribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.14)" />
              <XAxis dataKey="genre" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(56,189,248,0.08)" }} />
              <Bar dataKey="count" fill="#38bdf8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Average rating by genre">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data?.ratingByGenre || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.14)" />
              <XAxis dataKey="genre" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 5]} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="rating"
                stroke="#a78bfa"
                strokeWidth={3}
                dot={{ fill: "#38bdf8", strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartPanel>
      </section>

      <section className="mt-8 rounded-lg border border-white/10 bg-white/[0.04] p-6">
        <h2 className="text-xl font-semibold text-white">Most popular movies</h2>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(data?.topMovies || []).map((movie) => (
            <div key={movie.id} className="rounded-lg border border-white/10 bg-black/20 p-4">
              <p className="font-semibold text-white">{movie.title}</p>
              <p className="mt-1 text-sm text-slate-400">{movie.genres?.join(", ")}</p>
              <p className="mt-2 text-xs text-signal">Popularity {movie.popularity_score}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

const tooltipStyle = {
  background: "#0d1224",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "8px",
  color: "#f8fafc",
};

function ChartPanel({ title, children }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] p-5">
      <h2 className="mb-5 text-xl font-semibold text-white">{title}</h2>
      {children}
    </div>
  );
}
