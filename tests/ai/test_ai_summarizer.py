"""
Demonstrates patterns for testing non-deterministic AI features.

Real LLM calls are never made here — the LLM client is always mocked.
The patterns shown apply to any feature that wraps a generative model:
  1. Schema validation        — response shape is deterministic even if content isn't
  2. Property assertions      — invariants that must hold regardless of wording
  3. Semantic similarity      — content is meaningfully related to the input
  4. PII / safety guardrails  — model output doesn't leak sensitive data
  5. Token-limit enforcement  — long inputs are truncated before reaching the LLM
  6. Graceful LLM failure     — downstream errors are wrapped, not propagated raw
  7. Golden-set regression    — a curated input produces output above a quality floor
"""
import re
from unittest.mock import MagicMock, call

import pytest

from tests.ai.summarizer import ArticleSummarizer, LLMError, LLMResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_summarizer(summary_text: str, key_points: list[str] | None = None) -> tuple[ArticleSummarizer, MagicMock]:
    """Return a summarizer whose LLM always returns the given canned response."""
    mock_llm = MagicMock()
    mock_llm.complete.return_value = LLMResponse(
        text=summary_text,
        key_points=key_points or ["Point A", "Point B", "Point C"],
    )
    return ArticleSummarizer(llm_client=mock_llm), mock_llm


def _word_overlap(a: str, b: str) -> float:
    """Jaccard similarity on word sets — cheap proxy for semantic closeness."""
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / len(a_words | b_words)


# ---------------------------------------------------------------------------
# 1. Schema validation
#
# Even though the model output is non-deterministic, the *shape* of the
# response our service returns is fully deterministic.  Validate it first.
# ---------------------------------------------------------------------------

def test_summary_response_has_required_fields() -> None:
    summarizer, _ = _make_summarizer("A short summary.")
    result = summarizer.summarize(title="My Article", body="Article body text here.")

    assert "summary" in result, "response must contain 'summary'"
    assert "key_points" in result, "response must contain 'key_points'"
    assert "word_count" in result, "response must contain 'word_count'"


def test_summary_response_field_types() -> None:
    summarizer, _ = _make_summarizer("A short summary.", key_points=["p1", "p2"])
    result = summarizer.summarize(title="My Article", body="Article body text here.")

    assert isinstance(result["summary"], str)
    assert isinstance(result["key_points"], list)
    assert all(isinstance(p, str) for p in result["key_points"])
    assert isinstance(result["word_count"], int)


# ---------------------------------------------------------------------------
# 2. Property assertions
#
# Things that must be true regardless of what the model outputs.
# These catch regressions when the model or prompt changes.
# ---------------------------------------------------------------------------

def test_summary_is_shorter_than_original_body() -> None:
    long_body = "data analytics " * 200          # 400 words
    summarizer, _ = _make_summarizer("A two sentence summary of the article.")
    result = summarizer.summarize(title="Analytics Report", body=long_body)

    assert result["word_count"] < len(long_body.split()), (
        "summary must be shorter than the original article"
    )


def test_key_points_list_is_not_empty() -> None:
    summarizer, _ = _make_summarizer("Summary.", key_points=["p1"])
    result = summarizer.summarize(title="T", body="Body text.")

    assert len(result["key_points"]) > 0, "key_points must never be an empty list"


def test_word_count_matches_summary_text() -> None:
    summary = "This is a five word summary."
    summarizer, _ = _make_summarizer(summary)
    result = summarizer.summarize(title="T", body="Body.")

    assert result["word_count"] == len(summary.split())


# ---------------------------------------------------------------------------
# 3. Semantic similarity
#
# The summary should be meaningfully related to the input content.
# A strict equality check is wrong; a similarity floor is the right tool.
# Threshold (0.05) is intentionally low — the goal is to catch a model
# that returns completely unrelated text, not to enforce paraphrasing.
# ---------------------------------------------------------------------------

SIMILARITY_THRESHOLD = 0.05


def test_summary_is_semantically_related_to_article() -> None:
    body = "Machine learning models require large datasets to generalise well."
    summary = "Large datasets help machine learning models generalise."

    summarizer, _ = _make_summarizer(summary)
    result = summarizer.summarize(title="ML Basics", body=body)

    similarity = _word_overlap(result["summary"], body)
    assert similarity >= SIMILARITY_THRESHOLD, (
        f"summary has low word overlap ({similarity:.2f}) with source — "
        "may indicate the model drifted to off-topic output"
    )


# ---------------------------------------------------------------------------
# 4. PII / safety guardrails
#
# If the article body contains personal data, the summary must not echo it.
# In production this would run against real model output; here we verify
# the *detection logic* by testing it on a mock response that leaks PII.
# ---------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def _contains_pii(text: str) -> bool:
    return bool(EMAIL_PATTERN.search(text) or CREDIT_CARD_PATTERN.search(text))


def test_pii_detector_flags_email_in_model_output() -> None:
    # Verify the detector itself works — this is what you'd call in a post-
    # processing guardrail before returning the response to the client.
    leaky_summary = "Contact john.doe@example.com for details."
    assert _contains_pii(leaky_summary), "detector must catch an email address"


def test_clean_summary_passes_pii_check() -> None:
    body = "Contact john.doe@example.com for more details on this research."
    clean_summary = "Researchers encourage interested parties to reach out directly."

    summarizer, _ = _make_summarizer(clean_summary)
    result = summarizer.summarize(title="Research", body=body)

    assert not _contains_pii(result["summary"]), (
        "a well-behaved model output should not contain PII from the source article"
    )


# ---------------------------------------------------------------------------
# 5. Token-limit enforcement
#
# The service must truncate long inputs before calling the LLM.
# We assert on the prompt the mock received, not on model output.
# ---------------------------------------------------------------------------

def test_long_article_body_is_truncated_before_llm_call() -> None:
    very_long_body = "x" * 10_000
    summarizer, mock_llm = _make_summarizer("Short summary.")

    summarizer.summarize(title="Long Article", body=very_long_body)

    prompt_sent: str = mock_llm.complete.call_args[0][0]
    # The raw 10 000-char body must NOT appear in the prompt verbatim
    assert very_long_body not in prompt_sent, "full body was sent to LLM — token limit not enforced"
    assert len(prompt_sent) < len(very_long_body), "prompt must be shorter than the raw input"


def test_short_article_is_not_truncated() -> None:
    short_body = "A brief article."
    summarizer, mock_llm = _make_summarizer("Summary.")

    summarizer.summarize(title="Short", body=short_body)

    prompt_sent: str = mock_llm.complete.call_args[0][0]
    assert short_body in prompt_sent, "short body must be sent to LLM in full"


# ---------------------------------------------------------------------------
# 6. Graceful LLM failure
#
# When the LLM call raises (network error, rate limit, timeout), the
# service must wrap it into a domain error rather than propagating raw.
# ---------------------------------------------------------------------------

def test_llm_network_error_raises_llm_error() -> None:
    mock_llm = MagicMock()
    mock_llm.complete.side_effect = ConnectionError("upstream timeout")
    summarizer = ArticleSummarizer(llm_client=mock_llm)

    with pytest.raises(LLMError, match="LLM call failed"):
        summarizer.summarize(title="T", body="Body.")


def test_llm_is_called_exactly_once_per_summarize() -> None:
    summarizer, mock_llm = _make_summarizer("Summary.")
    summarizer.summarize(title="T", body="Body.")

    assert mock_llm.complete.call_count == 1, "summarize must call the LLM exactly once"


# ---------------------------------------------------------------------------
# 7. Golden-set regression
#
# A curated (input, acceptable_output_floor) pair that captures the
# minimum quality bar for a known article.  Run this in CI to detect
# prompt regressions — if the similarity score drops below the floor,
# a prompt or model change has degraded quality.
#
# In production: replace _word_overlap with an embeddings-based scorer
# (e.g. sentence-transformers or an LLM-as-judge call) and raise the
# threshold to ~0.7.  Track the score over time in an eval dashboard
# (LangSmith, W&B, RAGAS) rather than just asserting a hard cutoff.
# ---------------------------------------------------------------------------

GOLDEN_SET = [
    {
        "title": "Introduction to Neural Networks",
        "body": (
            "Neural networks are computing systems inspired by biological neural networks. "
            "They consist of layers of interconnected nodes that process information. "
            "Deep learning uses multiple layers to learn representations of data."
        ),
        "expected_summary": (
            "Neural networks are inspired by biology and use layered nodes. "
            "Deep learning extends this with multiple layers."
        ),
        "min_similarity": 0.15,
    },
]


@pytest.mark.parametrize("case", GOLDEN_SET, ids=[c["title"] for c in GOLDEN_SET])
def test_golden_set_similarity_above_floor(case: dict) -> None:
    summarizer, _ = _make_summarizer(case["expected_summary"])
    result = summarizer.summarize(title=case["title"], body=case["body"])

    similarity = _word_overlap(result["summary"], case["body"])
    assert similarity >= case["min_similarity"], (
        f"golden-set similarity {similarity:.2f} is below floor {case['min_similarity']} "
        f"for article '{case['title']}' — prompt or model may have regressed"
    )
