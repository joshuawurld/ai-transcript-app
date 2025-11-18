"""DecisionRecordTool - captures Architecture Decision Records (ADRs) from meeting transcripts."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .base import Tool

DECISION_RECORDS_DIR = Path(__file__).parent.parent / "decision_records"


class DecisionRecordTool(Tool):
    """Captures structured Architecture Decision Records (ADRs) from decision-making meetings."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "create_decision_record"

    @property
    def description(self) -> str:
        return """Create an Architecture Decision Record (ADR) for strategic or technical decisions.

Use this tool when the transcript describes:
- Architectural decisions (technology stack, framework choices, design patterns)
- Strategic product decisions (feature prioritization, direction changes)
- Process decisions (workflow changes, team structure, methodologies)
- Technical trade-off discussions with a final decision reached

DO NOT use this tool for:
- Meetings with action items and deadlines (use create_calendar_reminder instead)
- Production incidents or emergencies (use generate_incident_report instead)
- Status updates without decisions (no tool needed)

Extract and organize:
- What decision was made
- Context/background (why was this decision needed?)
- Options that were considered (alternatives discussed)
- Chosen solution and rationale
- Trade-offs and consequences
- Decision makers involved

Creates a structured ADR document for knowledge base and future reference."""

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "decision_title": {
                    "type": "string",
                    "description": "Clear, concise title of the decision (e.g., 'Use REST API instead of GraphQL for platform')",
                },
                "decision_date": {
                    "type": "string",
                    "description": "Date the decision was made (YYYY-MM-DD format)",
                },
                "status": {
                    "type": "string",
                    "enum": ["proposed", "accepted", "rejected", "deprecated", "superseded"],
                    "description": "Status of the decision (usually 'accepted' if finalized in the meeting)",
                },
                "context": {
                    "type": "string",
                    "description": "Background and context - what problem or need led to this decision? What forces are at play?",
                },
                "options_considered": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "option": {
                                "type": "string",
                                "description": "The option/alternative that was considered",
                            },
                            "pros": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Advantages of this option",
                            },
                            "cons": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Disadvantages or concerns with this option",
                            },
                        },
                        "required": ["option"],
                    },
                    "description": "All options/alternatives that were considered during the discussion",
                },
                "decision": {
                    "type": "string",
                    "description": "The final decision that was made - which option was chosen",
                },
                "rationale": {
                    "type": "string",
                    "description": "Why this decision was made - the reasoning and key factors that led to this choice",
                },
                "consequences": {
                    "type": "object",
                    "properties": {
                        "positive": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Positive outcomes and benefits of this decision",
                        },
                        "negative": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Negative consequences, trade-offs, or risks accepted",
                        },
                        "risks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Potential risks or unknowns to monitor",
                        },
                    },
                    "description": "Expected consequences and trade-offs of this decision",
                },
                "decision_makers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "People who participated in making this decision",
                },
                "additional_notes": {
                    "type": "string",
                    "description": "Any additional context, constraints, or notes relevant to this decision",
                },
            },
            "required": [
                "decision_title",
                "decision_date",
                "status",
                "context",
                "options_considered",
                "decision",
                "rationale",
            ],
        }

    def execute(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool - generate markdown file and return structured JSON data."""
        print(f"\n[decision] Recording decision: '{tool_input['decision_title']}'")
        print(f"[decision] Status: {tool_input.get('status', 'accepted')}, Date: {tool_input.get('decision_date')}")

        try:
            DECISION_RECORDS_DIR.mkdir(exist_ok=True)

            markdown = build_decision_record_markdown(tool_input)
            filepath = self._save_markdown(tool_input['decision_title'], markdown)

            print(f"[decision] ✓ Saved ADR to {filepath.name}")

            return {
                "status": "success",
                "type": "decision_record",
                "markdown_content": markdown,
                "data": tool_input,
            }

        except Exception as e:
            print(f"[decision] ✗ Error: {e}")
            return {
                "status": "error",
                "message": f"Failed to capture decision record: {str(e)}",
                "data": tool_input,
            }

    def _save_markdown(self, title: str, content: str) -> Path:
        """Save markdown to file and return filepath."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_title = safe_title.replace(" ", "_")[:50]
        filename = f"{timestamp}_{safe_title}.md"
        filepath = DECISION_RECORDS_DIR / filename

        filepath.write_text(content, encoding='utf-8')
        return filepath


# Formatting helper functions (implementation details)

def build_decision_record_markdown(data: Dict[str, Any]) -> str:
    """Build ADR markdown from LLM-provided JSON data."""
    status = data.get("status", "accepted").upper()
    status_emoji = {"PROPOSED": "💡", "ACCEPTED": "✅", "REJECTED": "❌",
                    "DEPRECATED": "⚠️", "SUPERSEDED": "🔄"}.get(status, "📋")

    md = f"# ADR: {data['decision_title']}\n\n"
    md += f"**Status:** {status_emoji} {status}\n\n"
    md += f"**Date:** {data['decision_date']}\n\n"

    if data.get('decision_makers'):
        md += f"**Decision Makers:** {', '.join(data['decision_makers'])}\n\n"

    md += "---\n\n"
    md += "## Context\n\n"
    md += f"{data['context']}\n\n"

    md += format_options_section(data.get('options_considered', []))

    md += "## Decision\n\n"
    md += f"{data['decision']}\n\n"
    md += "## Rationale\n\n"
    md += f"{data['rationale']}\n\n"

    md += format_consequences_section(data.get('consequences'))

    if data.get('additional_notes'):
        md += "## Additional Notes\n\n"
        md += f"{data['additional_notes']}\n\n"

    return md


def format_options_section(options: list) -> str:
    """Format the 'Options Considered' section of the ADR."""
    if not options:
        return ""

    section = "## Options Considered\n\n"
    for idx, option in enumerate(options, 1):
        section += f"### Option {idx}: {option['option']}\n\n"
        if option.get('pros'):
            section += "**Pros:**\n"
            for pro in option['pros']:
                section += f"- {pro}\n"
            section += "\n"
        if option.get('cons'):
            section += "**Cons:**\n"
            for con in option['cons']:
                section += f"- {con}\n"
            section += "\n"
    return section


def format_consequences_section(consequences: dict) -> str:
    """Format the 'Consequences' section of the ADR."""
    if not consequences:
        return ""

    section = "## Consequences\n\n"
    if consequences.get('positive'):
        section += "### Positive\n\n"
        for item in consequences['positive']:
            section += f"- {item}\n"
        section += "\n"
    if consequences.get('negative'):
        section += "### Negative\n\n"
        for item in consequences['negative']:
            section += f"- {item}\n"
        section += "\n"
    if consequences.get('risks'):
        section += "### Risks to Monitor\n\n"
        for item in consequences['risks']:
            section += f"- {item}\n"
        section += "\n"
    return section
