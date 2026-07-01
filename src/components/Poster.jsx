import { Film } from "lucide-react";
import { useState } from "react";

export default function Poster({ movie, className = "" }) {
  const [failed, setFailed] = useState(false);
  const showImage = movie?.poster_url && !failed;

  if (showImage) {
    return (
      <img
        src={movie.poster_url}
        alt={`${movie.title} poster`}
        className={className}
        loading="lazy"
        onError={() => setFailed(true)}
      />
    );
  }

  return (
    <div
      className={`${className} flex items-center justify-center bg-[radial-gradient(circle_at_25%_15%,rgba(56,189,248,0.28),transparent_36%),linear-gradient(135deg,#172554,#111827_48%,#312e81)]`}
    >
      <div className="text-center">
        <Film className="mx-auto h-10 w-10 text-white/80" />
        <p className="mt-3 px-4 text-sm font-semibold text-white">{movie?.title}</p>
      </div>
    </div>
  );
}
