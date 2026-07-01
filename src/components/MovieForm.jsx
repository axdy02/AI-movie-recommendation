import { useMemo, useState } from "react";

import { splitCsv } from "../utils/formatters.js";

const DEFAULT_FORM = {
  title: "",
  description: "",
  genres: "",
  tags: "",
  poster_url: "",
  rating: 0,
  release_year: new Date().getFullYear(),
  language: "english",
  cast: "",
  duration: 0,
  popularity_score: 0,
};

export default function MovieForm({ initialValue, onSubmit, submitLabel = "Save movie" }) {
  const initial = useMemo(() => normalizeInitial(initialValue), [initialValue]);
  const [form, setForm] = useState(initial);
  const [saving, setSaving] = useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSubmit({
        title: form.title,
        description: form.description || null,
        genres: splitCsv(form.genres),
        tags: splitCsv(form.tags),
        poster_url: form.poster_url || null,
        rating: Number(form.rating),
        release_year: Number(form.release_year),
        language: form.language || null,
        cast: splitCsv(form.cast),
        duration: Number(form.duration),
        popularity_score: Number(form.popularity_score),
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-lg border border-white/10 bg-white/[0.04] p-6">
      <div className="grid gap-5 lg:grid-cols-2">
        <Field label="Title" name="title" value={form.title} onChange={updateField} required />
        <Field
          label="Poster URL"
          name="poster_url"
          value={form.poster_url}
          onChange={updateField}
          placeholder="https://..."
        />
        <Field
          label="Genres"
          name="genres"
          value={form.genres}
          onChange={updateField}
          placeholder="action, sci fi, thriller"
          required
        />
        <Field
          label="Tags"
          name="tags"
          value={form.tags}
          onChange={updateField}
          placeholder="cyberpunk, crime, heist"
        />
        <Field label="Language" name="language" value={form.language} onChange={updateField} />
        <Field label="Cast" name="cast" value={form.cast} onChange={updateField} />
        <Field
          label="Rating"
          name="rating"
          value={form.rating}
          onChange={updateField}
          type="number"
          min="0"
          max="5"
          step="0.1"
        />
        <Field
          label="Release year"
          name="release_year"
          value={form.release_year}
          onChange={updateField}
          type="number"
          min="1888"
          max="2100"
        />
        <Field
          label="Duration seconds"
          name="duration"
          value={form.duration}
          onChange={updateField}
          type="number"
          min="0"
        />
        <Field
          label="Popularity score"
          name="popularity_score"
          value={form.popularity_score}
          onChange={updateField}
          type="number"
          min="0"
        />
      </div>

      <label className="block">
        <span className="text-sm text-slate-300">Description</span>
        <textarea
          name="description"
          value={form.description}
          onChange={updateField}
          rows={5}
          className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-3 text-sm text-white outline-none transition focus:border-signal"
          placeholder="Movie synopsis"
        />
      </label>

      <button
        type="submit"
        disabled={saving}
        className="rounded-lg bg-gradient-to-r from-signal to-violetSignal px-5 py-3 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-60"
      >
        {saving ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}

function Field({ label, ...props }) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input
        {...props}
        className="mt-2 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-signal"
      />
    </label>
  );
}

function normalizeInitial(value) {
  if (!value) return DEFAULT_FORM;
  return {
    ...DEFAULT_FORM,
    ...value,
    genres: (value.genres || []).join(", "),
    tags: (value.tags || []).join(", "),
    cast: (value.cast || []).join(", "),
  };
}
