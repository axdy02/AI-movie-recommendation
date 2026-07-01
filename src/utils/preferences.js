const PREFERENCES_KEY = "ai_movie_preferences";

export const GENRE_OPTIONS = [
  "action",
  "adventure",
  "comedy",
  "crime",
  "drama",
  "fantasy",
  "horror",
  "mystery",
  "romance",
  "sci fi",
  "thriller",
  "musical",
];

export const LANGUAGE_OPTIONS = ["english", "hindi", "spanish", "korean", "japanese"];

export function getLocalPreferences(userId) {
  const allPreferences = readAllPreferences();
  return (
    allPreferences[userId] || {
      preferred_genres: ["action", "sci fi"],
      preferred_tags: ["technology", "crime"],
      preferred_languages: ["english"],
    }
  );
}

export function saveLocalPreferences(userId, preferences) {
  const allPreferences = readAllPreferences();
  allPreferences[userId] = preferences;
  window.localStorage.setItem(PREFERENCES_KEY, JSON.stringify(allPreferences));
}

function readAllPreferences() {
  try {
    return JSON.parse(window.localStorage.getItem(PREFERENCES_KEY) || "{}");
  } catch {
    return {};
  }
}
