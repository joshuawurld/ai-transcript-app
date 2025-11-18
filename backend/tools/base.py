"""Base Tool class for all tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any


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
    def input_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenRouter/OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            }
        }
