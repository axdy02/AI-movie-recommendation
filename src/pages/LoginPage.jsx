import { LogIn, Sparkles } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "maya@example.com", password: "password123" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await login(form);
      const fallback = user.role === "admin" ? "/admin" : "/dashboard";
      navigate(location.state?.from?.pathname || fallback, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthFrame title="Welcome back" subtitle="Log in to inspect recommendations.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(value) => setForm((current) => ({ ...current, email: value }))}
        />
        <Input
          label="Password"
          type="password"
          value={form.password}
          onChange={(value) => setForm((current) => ({ ...current, password: value }))}
        />
        {error ? <p className="rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
        >
          <LogIn className="h-4 w-4" />
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-slate-400">
        New here?{" "}
        <Link to="/register" className="font-semibold text-signal hover:text-white">
          Create an account
        </Link>
      </p>
    </AuthFrame>
  );
}

export function AuthFrame({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4 py-10 text-white">
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-white/[0.04] p-6 shadow-glow">
        <Link to="/" className="mb-8 flex items-center justify-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-signal to-violetSignal">
            <Sparkles className="h-6 w-6" />
          </div>
          <span className="text-lg font-semibold">Movie AI</span>
        </Link>
        <h1 className="text-center text-3xl font-semibold">{title}</h1>
        <p className="mt-2 text-center text-sm text-slate-400">{subtitle}</p>
        <div className="mt-8">{children}</div>
      </div>
    </div>
  );
}

export function Input({ label, value, onChange, ...props }) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input
        {...props}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-3 text-sm text-white outline-none transition focus:border-signal"
        required
      />
    </label>
  );
}
