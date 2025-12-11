"""Base Tool class for all tools."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any


class Tool(ABC):
    """Base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        pass

    def to_openai_format(self) -> dict[str, Any]:
        """Convert tool to OpenRouter/OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            }
        }

    def _save_markdown(self, output_dir: Path, title: str, content: str) -> Path:
        """Save markdown content to a file with timestamped filename.

        Args:
            output_dir: Directory to save the file in (will be created if needed)
            title: Title to use in filename (will be sanitized)
            content: Markdown content to write

        Returns:
            Path to the saved file
        """
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_title = safe_title.replace(" ", "_")[:50]
        filename = f"{timestamp}_{safe_title}.md"
        filepath = output_dir / filename

        filepath.write_text(content, encoding="utf-8")
        return filepath
