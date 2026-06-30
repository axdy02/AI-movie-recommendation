from app.models.movie import Movie
from app.services.ollama_service import OllamaService


def test_generate_tags_uses_ollama_response(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        OllamaService,
        "_generate",
        lambda _prompt: "Crime, Revenge, Action, crime",
    )

    tags = OllamaService.generate_tags_from_description(
        title="Example",
        description="A revenge thriller about a detective.",
    )

    assert tags == ["crime", "revenge", "action"]


def test_generate_tags_falls_back_when_ollama_unavailable(
    monkeypatch,
) -> None:
    monkeypatch.setattr(OllamaService, "_generate", lambda _prompt: None)

    tags = OllamaService.generate_tags_from_description(
        title="Detective Story",
        description="A detective solves a mystery in a haunted city.",
    )

    assert "detective" in tags
    assert "mystery" in tags


def test_generate_recommendation_reason_falls_back_when_ollama_unavailable(
    monkeypatch,
) -> None:
    monkeypatch.setattr(OllamaService, "_generate", lambda _prompt: None)
    movie = Movie(
        title="Example Movie",
        description="A test movie.",
        genres=["thriller"],
        tags=["mystery"],
        rating=4.0,
        language="english",
        cast=[],
        popularity_score=10.0,
    )

    reason = OllamaService.generate_recommendation_reason(
        movie=movie,
        fallback_reason="Recommended because you watched thriller movies.",
        signals={"content_score": 0.8},
    )

    assert reason == "Recommended because you watched thriller movies."


def test_generate_recommendation_reason_uses_clean_ollama_text(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        OllamaService,
        "_generate",
        lambda _prompt: ' "Because you enjoy tense mystery thrillers" ',
    )
    movie = Movie(
        title="Example Movie",
        description="A test movie.",
        genres=["thriller"],
        tags=["mystery"],
        rating=4.0,
        language="english",
        cast=[],
        popularity_score=10.0,
    )

    reason = OllamaService.generate_recommendation_reason(
        movie=movie,
        fallback_reason="Fallback.",
        signals={"content_score": 0.8},
    )

    assert reason == "Because you enjoy tense mystery thrillers."
