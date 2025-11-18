"""Agent implementation using OpenAI-compatible API with function calling."""

import json
from datetime import datetime, timedelta
from typing import Any

from openai import OpenAI

from tools import ToolRegistry


class Agent:
    """AI agent that analyzes transcripts and executes tools."""

    def __init__(self, llm_client: OpenAI, model: str, tool_registry: ToolRegistry):
        self.llm_client = llm_client
        self.model = model
        self.tool_registry = tool_registry
        print(f"🤖 Agent initialized with {len(tool_registry)} tools")

    def process_transcript(self, transcript: str) -> dict[str, Any]:
        """Process transcript: LLM selects tools, execute them, generate summary."""
        if not transcript:
            return {"tool_calls": [], "results": [], "summary": "", "success": True}

        print("\n🤖 Agent analyzing transcript...")
        preview = transcript[:150] + "..." if len(transcript) > 150 else transcript
        print(f"📋 Preview: {preview}\n")

        try:
            tool_calls = self._select_tools(transcript)
            results = self._execute_tools(tool_calls)
            summary = self._generate_summary(transcript, tool_calls, results)

            print(f"✅ Processing complete: {len(tool_calls)} tool(s) executed\n")

            return {
                "tool_calls": tool_calls,
                "results": results,
                "summary": summary,
                "success": True,
            }

        except Exception as e:
            print(f"\n⚠️  Agent error: {e}")
            return {
                "tool_calls": [],
                "results": [],
                "summary": f"Error processing transcript: {str(e)}",
                "success": False,
                "error": str(e),
            }

    def _select_tools(self, transcript: str) -> list[dict[str, Any]]:
        """Ask LLM to analyze transcript and select tools to call."""
        print("\n🔍 PHASE 1: Tool Selection\n")

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A")
        one_week_from_now = (now.replace(hour=0, minute=0, second=0, microsecond=0) +
                             timedelta(days=7)).strftime("%Y-%m-%d")

        system_prompt = f"""You are a meeting assistant that processes transcripts and extracts structured information.

**CURRENT DATE/TIME CONTEXT:**
- Today is {current_day}, {current_date}
- One week from now: {one_week_from_now}

Analyze the transcript and call the appropriate tool(s) to extract relevant information.

**Important**: You can call MULTIPLE tools for the same transcript if appropriate:
- Incident call → incident report + calendar (for follow-up actions)
- Architecture review with implementation tasks → decision record + calendar
- But if a meeting is ONLY about decisions (no immediate tasks) → decision record ONLY

For calendar reminders: If the transcript mentions specific deadlines, set reminder_date 1-2 days before the earliest deadline. Otherwise use {one_week_from_now}. Always use YYYY-MM-DD format."""

        user_prompt = f"Process this meeting transcript using the appropriate tools:\n\n{transcript}"

        tools_formatted = self.tool_registry.to_openai_format()

        request_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "tools": tools_formatted,
            "tool_choice": "auto",
            "temperature": 0.3
        }

        print("📋 FULL API REQUEST:")
        print(json.dumps(request_payload, indent=2))

        print("\n⏳ Calling LLM...")
        response = self.llm_client.chat.completions.create(**request_payload)

        message = response.choices[0].message

        print("\n📤 LLM RESPONSE:")
        if message.tool_calls:
            print(f"Tool calls selected: {len(message.tool_calls)}")
            for tool_call in message.tool_calls:
                print(f"\n• Tool: {tool_call.function.name}")
                print(f"  Arguments: {tool_call.function.arguments[:200]}...")
        else:
            print("No tools selected")
            if message.content:
                print(f"Reason: {message.content}")

        tool_calls = []
        if message.tool_calls:
            print(f"\n✓ LLM selected {len(message.tool_calls)} tool(s)")
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                tool_calls.append({"name": tool_name, "input": tool_input})
                print(f"  • {tool_name}")
        else:
            print("\nℹ️  No tools selected")

        return tool_calls

    def _execute_tools(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute the tools selected by the LLM."""
        if not tool_calls:
            return []

        print(f"\n⚙️  PHASE 2: Tool Execution ({len(tool_calls)} tool(s))\n")

        results = []
        for tool_call in tool_calls:
            result = self.tool_registry.execute(
                name=tool_call["name"], tool_input=tool_call["input"]
            )
            results.append(result)

            status = "✓" if result.get("status") == "success" else "✗"
            print(f"{status} {tool_call['name']}: {result.get('status', 'unknown')}")

        return results

    def _generate_summary(
        self, transcript: str, tool_calls: list[dict[str, Any]], results: list[dict[str, Any]]
    ) -> str:
        """Generate a user-friendly summary of what the agent did."""
        print("\n📝 PHASE 3: Summary Generation\n")

        if not tool_calls:
            return self._generate_no_tools_summary(transcript)

        system_prompt = """You are a helpful assistant explaining what you did with a transcript.

Write a friendly, concise summary (2-4 sentences) explaining:
1. What you found in the transcript
2. What actions you took
3. What the user should do next (if applicable)

Be conversational and helpful. Don't use technical jargon like "tool_calls" or "agent" - just explain what you did."""

        tools_summary = json.dumps(
            {"tool_calls": tool_calls, "results": results}, indent=2
        )

        user_prompt = f"""I analyzed a transcript and executed these tools:

{tools_summary}

Write a friendly 2-4 sentence summary for the user explaining what I did and what they should do next."""

        request_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        }

        print("📋 FULL API REQUEST:")
        print(json.dumps(request_payload, indent=2))

        try:
            print("\n⏳ Calling LLM...")
            response = self.llm_client.chat.completions.create(**request_payload)

            summary = response.choices[0].message.content.strip()

            print("\n📤 LLM RESPONSE:")
            print(summary)

            print("\n✓ Summary generated\n")
            return summary

        except Exception as e:
            print(f"⚠️  Error generating summary: {e}")
            tool_names = [tc["name"].replace("_", " ").title() for tc in tool_calls]
            return f"I processed your transcript and completed {len(tool_calls)} action(s): {', '.join(tool_names)}."

    def _generate_no_tools_summary(self, transcript: str) -> str:
        """Generate a summary when no tools were needed."""
        system_prompt = "You are a helpful assistant explaining why a transcript didn't need any special processing. Be concise and friendly."
        user_prompt = f"I analyzed this transcript but didn't find anything that needed special processing (like action items, blockers, or urgent issues). Explain why in 1-2 sentences:\n\n{transcript[:500]}"

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=150,
            )
            summary = response.choices[0].message.content.strip()
            print("✓ Summary generated\n")
            return summary
        except Exception as e:
            print(f"⚠️  Error generating summary: {e}")
            return "I analyzed your transcript but didn't find any action items, blockers, or urgent issues that needed special handling."
