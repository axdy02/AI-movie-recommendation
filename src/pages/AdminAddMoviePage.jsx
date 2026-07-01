import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { adminApi } from "../api/endpoints.js";
import MovieForm from "../components/MovieForm.jsx";
import PageHeader from "../components/PageHeader.jsx";

export default function AdminAddMoviePage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  async function createMovie(payload) {
    setError("");
    try {
      await adminApi.createMovie(payload);
      navigate("/admin/movies");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Admin"
        title="Add movie"
        description="Create clean movie metadata for search, tagging, and recommendation ranking."
      />
      {error ? <p className="mb-5 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p> : null}
      <MovieForm onSubmit={createMovie} submitLabel="Create movie" />
    </>
  );
}
