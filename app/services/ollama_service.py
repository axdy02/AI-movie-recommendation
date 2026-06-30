from __future__ import annotations

from collections import Counter
from typing import Any, ClassVar
import re

import httpx

from app.config import settings
from app.models.movie import Movie


TAG_SPLIT_PATTERN = re.compile(r"[,;\n]+")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "about",
    "after",
    "against",
    "and",
    "are",
    "because",
    "between",
    "from",
    "into",
    "movie",
    "must",
    "that",
    "the",
    "their",
    "this",
    "through",
    "with",
}


class OllamaService:
    _available: ClassVar[bool | None] = None

    @classmethod
    def generate_tags_from_description(
        cls,
        *,
        title: str,
        description: str | None,
        max_tags: int = 8,
    ) -> list[str]:
        fallback_tags = cls.rule_based_tags(
            title=title,
            description=description,
            max_tags=max_tags,
        )
        if not description:
            return fallback_tags

        prompt = (
            "Generate concise movie metadata tags. "
            "Return only comma-separated lowercase tags, no numbering.\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Maximum tags: {max_tags}"
        )
        response_text = cls._generate(prompt)
        if response_text is None:
            return fallback_tags

        tags = clean_tags(response_text, max_tags=max_tags)
        return tags or fallback_tags

    @classmethod
    def generate_recommendation_reason(
        cls,
        *,
        movie: Movie,
        fallback_reason: str,
        signals: dict[str, float] | None = None,
    ) -> str:
        signal_text = ", ".join(
            f"{name}: {value:.2f}" for name, value in (signals or {}).items()
        )
        prompt = (
            "Write one short human-readable movie recommendation reason. "
            "Do not mention algorithms, scores, vectors, or internal systems. "
            "Keep it under 25 words.\n\n"
            f"Movie: {movie.title}\n"
            f"Genres: {', '.join(movie.genres)}\n"
            f"Tags: {', '.join(movie.tags)}\n"
            f"Language: {movie.language or 'unknown'}\n"
            f"Fallback reason: {fallback_reason}\n"
            f"Signals: {signal_text or 'none'}"
        )
        response_text = cls._generate(prompt)
        if response_text is None:
            return fallback_reason

        reason = clean_reason(response_text)
        return reason or fallback_reason

    @staticmethod
    def rule_based_tags(
        *,
        title: str,
        description: str | None,
        max_tags: int = 8,
    ) -> list[str]:
        text = f"{title} {description or ''}".lower()
        candidates = [
            token
            for token in TOKEN_PATTERN.findall(text)
            if len(token) > 2 and token not in STOPWORDS and not token.isdigit()
        ]
        counts = Counter(candidates)
        ranked_tokens = sorted(counts, key=lambda token: (-counts[token], token))
        return ranked_tokens[:max_tags]

    @classmethod
    def _generate(cls, prompt: str) -> str | None:
        if cls._available is False or not settings.ollama_model:
            return None

        try:
            with httpx.Client(
                base_url=settings.ollama_base_url,
                timeout=settings.ollama_timeout_seconds,
            ) as client:
                response = client.post(
                    "/api/generate",
                    json={
                        "model": settings.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                response_data: dict[str, Any] = response.json()
        except (httpx.HTTPError, ValueError):
            cls._available = False
            return None

        cls._available = True
        response_text = response_data.get("response")
        if not isinstance(response_text, str):
            return None
        return response_text.strip()


def clean_tags(value: str, *, max_tags: int) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()
    for raw_item in TAG_SPLIT_PATTERN.split(value):
        cleaned = " ".join(raw_item.strip().lower().split())
        cleaned = cleaned.strip("-*0123456789. ")
        if not cleaned or cleaned in seen:
            continue
        if len(cleaned) > 40:
            continue
        seen.add(cleaned)
        tags.append(cleaned)
        if len(tags) >= max_tags:
            break
    return tags


def clean_reason(value: str) -> str:
    cleaned = " ".join(value.strip().strip('"').split())
    if not cleaned:
        return ""
    if len(cleaned) > 240:
        return ""
    if not cleaned.endswith((".", "!", "?")):
        cleaned += "."
    return cleaned
