import { ArrowRight, BarChart3, BrainCircuit, Gauge, Shield, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

import { useAuth } from "../context/AuthContext.jsx";

const signals = [
  ["Content", "TF-IDF + cosine similarity", "45%"],
  ["Similar users", "Collaborative matrix", "30%"],
  ["Quality", "Ratings + popularity", "20%"],
  ["Freshness", "Release-year signal", "5%"],
];

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen overflow-hidden bg-ink text-white">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-4 py-6 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-signal to-violetSignal">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-signal">
              RecSys
            </p>
            <p className="font-semibold">Movie AI</p>
          </div>
        </Link>
        <nav className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-ink"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="px-3 py-2 text-sm text-slate-300 hover:text-white">
                Login
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-ink"
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="relative mx-auto grid min-h-[calc(100vh-92px)] max-w-7xl items-center gap-12 px-4 pb-16 pt-8 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
        <div className="absolute inset-0 -z-10 opacity-80">
          <div className="absolute left-1/2 top-16 h-80 w-80 -translate-x-1/2 rounded-full bg-signal/10 blur-3xl" />
          <div className="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-violetSignal/10 blur-3xl" />
        </div>

        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <p className="inline-flex items-center gap-2 rounded-full border border-signal/30 bg-signal/10 px-3 py-1 text-sm text-signal">
            <BrainCircuit className="h-4 w-4" />
            Recommendation engine showcase
          </p>
          <h1 className="mt-6 max-w-3xl text-5xl font-semibold tracking-tight text-white md:text-6xl">
            Explainable movie recommendations, not another streaming clone.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300">
            A clean frontend for inspecting personalized recommendations,
            score breakdowns, watch signals, ratings, user preferences, and
            admin analytics from the FastAPI backend.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to={isAuthenticated ? "/recommendations" : "/login"}
              className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-5 py-3 text-sm font-semibold text-white"
            >
              View recommendations
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/register"
              className="rounded-lg border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-semibold text-slate-200 hover:bg-white/[0.08]"
            >
              Choose favorite genres
            </Link>
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="rounded-lg border border-white/10 bg-white/[0.04] p-4 shadow-glow"
        >
          <div className="rounded-lg border border-white/10 bg-panel p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-signal">
                  Hybrid ranking
                </p>
                <h2 className="mt-2 text-2xl font-semibold">Silent Jury</h2>
              </div>
              <div className="rounded-lg bg-emerald-300/10 px-3 py-2 text-sm text-emerald-200">
                91% match
              </div>
            </div>

            <div className="mt-6 grid gap-3">
              {signals.map(([label, helper, score]) => (
                <div key={label} className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium text-white">{label}</p>
                      <p className="mt-1 text-sm text-slate-400">{helper}</p>
                    </div>
                    <span className="text-xl font-semibold text-signal">{score}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <MiniMetric icon={Gauge} label="Final score" value="0.6812" />
              <MiniMetric icon={BarChart3} label="Popularity" value="0.9271" />
              <MiniMetric icon={Shield} label="Role-gated" value="Admin" />
            </div>
          </div>
        </motion.section>
      </main>
    </div>
  );
}

function MiniMetric({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <Icon className="h-4 w-4 text-signal" />
      <p className="mt-3 text-xs text-slate-400">{label}</p>
      <p className="mt-1 font-semibold text-white">{value}</p>
    </div>
  );
}
