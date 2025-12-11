"""ToolRegistry - manages available tools."""

from typing import Any

from .base import Tool


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    async def execute(self, name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(name)
        return await tool.execute(tool_input)

    def get_all_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def to_openai_format(self) -> list[dict[str, Any]]:
        """Get tools in OpenAI function calling format."""
        return [tool.to_openai_format() for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
