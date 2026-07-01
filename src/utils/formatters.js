export function cx(...classes) {
  return classes.filter(Boolean).join(" ");
}

export function formatScore(value) {
  const number = Number(value || 0);
  return `${Math.round(number * 100)}%`;
}

export function formatRating(value) {
  return Number(value || 0).toFixed(1);
}

export function formatDuration(seconds) {
  if (!seconds) return "Unknown";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (!hours) return `${minutes}m`;
  return `${hours}h ${minutes}m`;
}

export function formatDate(value) {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function getPrimaryGenre(movie) {
  return movie?.genres?.[0] || "movie";
}

export function splitCsv(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
