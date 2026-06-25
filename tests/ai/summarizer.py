"""
Hypothetical AI feature: an article summariser that wraps an LLM client.

This module exists solely to give the AI testing patterns in
test_ai_summarizer.py something real to test. It is NOT wired into
the running application.
"""
from dataclasses import dataclass


class LLMError(Exception):
    pass


@dataclass
class LLMResponse:
    text: str
    key_points: list[str]


class ArticleSummarizer:
    MAX_INPUT_CHARS = 4000  # rough proxy for token limit

    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client

    def summarize(self, title: str, body: str) -> dict:
        truncated_body = body[: self.MAX_INPUT_CHARS]
        prompt = (
            f"Summarise this article titled '{title}':\n\n{truncated_body}\n\n"
            "Return a short summary and three key points."
        )
        try:
            response: LLMResponse = self.llm_client.complete(prompt)
        except Exception as exc:
            raise LLMError(f"LLM call failed: {exc}") from exc

        return {
            "summary": response.text,
            "key_points": response.key_points,
            "word_count": len(response.text.split()),
        }
