import { UserPlus } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import GenrePicker from "../components/GenrePicker.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { AuthFrame, Input } from "./LoginPage.jsx";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [genres, setGenres] = useState(["action", "sci fi"]);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register({
        ...form,
        preferences: {
          preferred_genres: genres,
          preferred_tags: [],
          preferred_languages: ["english"],
        },
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthFrame
      title="Create your profile"
      subtitle="Pick genres so cold-start recommendations have a signal."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Full name"
          value={form.full_name}
          onChange={(value) => setForm((current) => ({ ...current, full_name: value }))}
        />
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
        <div>
          <p className="mb-3 text-sm text-slate-300">Favorite genres</p>
          <GenrePicker selected={genres} onChange={setGenres} />
        </div>
        {error ? <p className="rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
        >
          <UserPlus className="h-4 w-4" />
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-slate-400">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-signal hover:text-white">
          Sign in
        </Link>
      </p>
    </AuthFrame>
  );
}
