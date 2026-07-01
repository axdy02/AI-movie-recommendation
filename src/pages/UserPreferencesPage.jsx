import { Save } from "lucide-react";
import { useEffect, useState } from "react";

import { preferencesApi } from "../api/endpoints.js";
import GenrePicker from "../components/GenrePicker.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { LANGUAGE_OPTIONS } from "../utils/preferences.js";

export default function UserPreferencesPage() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState(null);
  const [tagText, setTagText] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function load() {
      const result = await preferencesApi.get(user.id);
      setPreferences(result);
      setTagText((result.preferred_tags || []).join(", "));
    }
    load();
  }, [user.id]);

  if (!preferences) return <LoadingState label="Loading preferences" />;

  async function save(event) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    const payload = {
      ...preferences,
      preferred_tags: tagText
        .split(",")
        .map((item) => item.trim().toLowerCase())
        .filter(Boolean),
    };
    await preferencesApi.update(user.id, payload);
    setPreferences(payload);
    setSaving(false);
    setMessage("Preferences saved.");
  }

  return (
    <>
      <PageHeader
        eyebrow="User preferences"
        title="Cold-start profile"
        description="These preferences help the UI preserve cold-start signals until a dedicated backend preferences route is available."
      />

      <form onSubmit={save} className="rounded-lg border border-white/10 bg-white/[0.04] p-6">
        <section>
          <h2 className="text-lg font-semibold text-white">Favorite genres</h2>
          <div className="mt-4">
            <GenrePicker
              selected={preferences.preferred_genres || []}
              onChange={(genres) =>
                setPreferences((current) => ({ ...current, preferred_genres: genres }))
              }
            />
          </div>
        </section>

        <section className="mt-8">
          <h2 className="text-lg font-semibold text-white">Preferred tags</h2>
          <input
            value={tagText}
            onChange={(event) => setTagText(event.target.value)}
            className="mt-3 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-3 text-sm text-white outline-none focus:border-signal"
            placeholder="crime, cyberpunk, music"
          />
        </section>

        <section className="mt-8">
          <h2 className="text-lg font-semibold text-white">Languages</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {LANGUAGE_OPTIONS.map((language) => {
              const selected = preferences.preferred_languages?.includes(language);
              return (
                <button
                  key={language}
                  type="button"
                  onClick={() =>
                    setPreferences((current) => ({
                      ...current,
                      preferred_languages: selected
                        ? current.preferred_languages.filter((item) => item !== language)
                        : [...(current.preferred_languages || []), language],
                    }))
                  }
                  className={`rounded-lg border px-4 py-2 text-sm capitalize ${
                    selected
                      ? "border-signal/40 bg-signal/15 text-white"
                      : "border-white/10 bg-white/[0.04] text-slate-400"
                  }`}
                >
                  {language}
                </button>
              );
            })}
          </div>
        </section>

        {message ? <p className="mt-5 text-sm text-emerald-300">{message}</p> : null}
        <button
          type="submit"
          disabled={saving}
          className="mt-6 flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal to-violetSignal px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
        >
          <Save className="h-4 w-4" />
          {saving ? "Saving..." : "Save preferences"}
        </button>
      </form>
    </>
  );
}
