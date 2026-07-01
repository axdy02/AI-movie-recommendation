import { Check } from "lucide-react";

import { GENRE_OPTIONS } from "../utils/preferences.js";
import { cx } from "../utils/formatters.js";

export default function GenrePicker({ selected, onChange }) {
  function toggle(genre) {
    if (selected.includes(genre)) {
      onChange(selected.filter((item) => item !== genre));
      return;
    }
    onChange([...selected, genre]);
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {GENRE_OPTIONS.map((genre) => {
        const active = selected.includes(genre);
        return (
          <button
            key={genre}
            type="button"
            onClick={() => toggle(genre)}
            className={cx(
              "flex items-center justify-between rounded-lg border px-3 py-3 text-left text-sm capitalize transition",
              active
                ? "border-signal/60 bg-signal/15 text-white"
                : "border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/20",
            )}
          >
            <span>{genre}</span>
            {active ? <Check className="h-4 w-4 text-signal" /> : null}
          </button>
        );
      })}
    </div>
  );
}
