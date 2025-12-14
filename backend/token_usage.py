"""
Token usage tracking for LLM calls.

Provides consistent logging and accumulation of token usage across the application.
"""

from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Accumulated token usage across LLM calls."""

    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0

    def add(self, input_tokens: int, output_tokens: int) -> None:
        """Add tokens from an LLM call."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.requests += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "requests": self.requests,
        }

    def __str__(self) -> str:
        return f"{self.input_tokens} in / {self.output_tokens} out"


def log_token_usage(
    source: str,
    input_tokens: int,
    output_tokens: int,
    accumulated: TokenUsage | None = None,
) -> None:
    """Log token usage from an LLM call.

    Args:
        source: Identifier for the LLM call (e.g., "clean", "agent", "issue-review")
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens
        accumulated: Optional TokenUsage to add to for running totals
    """
    total = input_tokens + output_tokens
    print(f"[{source}] Tokens: {input_tokens} in / {output_tokens} out ({total} total)")

    if accumulated:
        accumulated.add(input_tokens, output_tokens)
        print(f"[{source}] Running total: {accumulated}")


def extract_openai_usage(response) -> tuple[int, int]:
    """Extract token usage from an OpenAI API response.

    Args:
        response: OpenAI ChatCompletion response object

    Returns:
        tuple of (input_tokens, output_tokens)
    """
    if hasattr(response, "usage") and response.usage:
        return (
            response.usage.prompt_tokens or 0,
            response.usage.completion_tokens or 0,
        )
    return (0, 0)


def extract_pydantic_usage(result) -> tuple[int, int]:
    """Extract token usage from a PydanticAI result.

    Args:
        result: PydanticAI AgentRunResult object

    Returns:
        tuple of (input_tokens, output_tokens)
    """
    usage = result.usage()
    return (
        usage.input_tokens or 0,
        usage.output_tokens or 0,
    )
