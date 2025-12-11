"""IncidentTool - captures structured incident reports for production issues."""

from pathlib import Path
from typing import Any

from github_integration import write_issue

from .base import Tool

INCIDENT_REPORTS_DIR = Path(__file__).parent.parent / "incident_reports"


class IncidentTool(Tool):
    """Captures structured incident reports from emergency/production incident transcripts."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "generate_incident_report"

    @property
    def description(self) -> str:
        return """Generate a structured incident report for production issues, outages, or critical problems.

Use this tool when the transcript describes:
- Production incidents, outages, or system failures
- Emergency response calls
- Critical issues affecting users or revenue
- Post-mortem discussions

DO NOT use any other tools when using this tool. Incident reports are comprehensive and include action items, so no separate calendar reminder is needed.

Extract and organize:
- Incident title and severity level
- Timeline of events (when issue started, detected, resolved)
- Root cause analysis
- Business impact metrics (downtime, affected users, revenue loss, failed transactions)
- Resolution steps taken
- Follow-up actions to prevent recurrence
- Stakeholders who were notified

Creates a comprehensive incident report for documentation and review."""

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "incident_title": {
                    "type": "string",
                    "description": "Clear, concise title describing the incident (e.g., 'Payment Processing API Outage')",
                },
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Severity level based on business impact and urgency",
                },
                "start_time": {
                    "type": "string",
                    "description": "When the incident started (extract from transcript, e.g., '10:15 AM' or 'around 10am')",
                },
                "detection_time": {
                    "type": "string",
                    "description": "When the incident was detected or reported (if mentioned)",
                },
                "resolution_time": {
                    "type": "string",
                    "description": "When the incident was resolved (if resolved, otherwise 'ongoing')",
                },
                "root_cause": {
                    "type": "string",
                    "description": "Root cause of the incident if identified (e.g., 'API credentials expired')",
                },
                "business_impact": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Overall description of business impact",
                        },
                        "downtime_duration": {
                            "type": "string",
                            "description": "Duration of downtime (e.g., '15 minutes', '2 hours')",
                        },
                        "affected_users": {
                            "type": "string",
                            "description": "Number or description of affected users (e.g., '200 users', 'all customers')",
                        },
                        "failed_transactions": {
                            "type": "string",
                            "description": "Number of failed transactions or operations",
                        },
                        "revenue_impact": {
                            "type": "string",
                            "description": "Revenue loss or financial impact if mentioned",
                        },
                    },
                    "description": "Quantitative and qualitative business impact",
                },
                "timeline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "time": {
                                "type": "string",
                                "description": "Time of the event (e.g., '10:15 AM', 'immediately after')",
                            },
                            "event": {
                                "type": "string",
                                "description": "What happened at this time",
                            },
                            "actor": {
                                "type": "string",
                                "description": "Who performed the action or discovered the event",
                            },
                        },
                        "required": ["time", "event"],
                    },
                    "description": "Chronological timeline of incident events",
                },
                "resolution_steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Steps taken to resolve the incident",
                },
                "stakeholders_notified": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "People or teams notified about the incident (e.g., 'CEO', 'VP Engineering', 'customers')",
                },
                "follow_up_actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Follow-up action to prevent recurrence",
                            },
                            "owner": {
                                "type": "string",
                                "description": "Person responsible for the action",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Priority level",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "When the action should be completed",
                            },
                        },
                        "required": ["action", "owner"],
                    },
                    "description": "Post-incident follow-up actions and preventive measures",
                },
                "additional_notes": {
                    "type": "string",
                    "description": "Any additional context or notes about the incident",
                },
            },
            "required": [
                "incident_title",
                "severity",
                "start_time",
                "root_cause",
                "business_impact",
                "timeline",
                "resolution_steps",
            ],
        }

    async def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool - generate markdown file and return structured JSON data."""
        severity = tool_input.get("severity", "medium").upper()
        print(f"\n[incident] Processing incident: '{tool_input['incident_title']}'")
        print(f"[incident] Severity: {severity}, Status: {tool_input.get('resolution_time', 'ongoing')}")

        try:
            markdown = build_incident_report_markdown(tool_input)
            filepath = self._save_markdown(INCIDENT_REPORTS_DIR, tool_input['incident_title'], markdown)

            print(f"[incident] ✓ Saved report to {filepath.name}")

            result = {
                "status": "success",
                "type": "incident_report",
                "markdown_content": markdown,
                "data": tool_input,
            }

            # Create GitHub issue (if configured)
            github_result = await write_issue("incident_report", tool_input)
            if github_result:
                result["github_issue"] = github_result

            return result

        except Exception as e:
            print(f"[incident] ✗ Error: {e}")
            return {
                "status": "error",
                "message": f"Failed to capture incident report: {str(e)}",
                "data": tool_input,
            }


# Formatting helper functions (implementation details)

def build_incident_report_markdown(data: dict[str, Any]) -> str:
    """Build incident report markdown from LLM-provided JSON data."""
    severity = data.get("severity", "medium").upper()
    severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠",
                      "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "⚪")

    md = f"# Incident Report: {data['incident_title']}\n\n"
    md += f"**Severity:** {severity_emoji} {severity}\n\n"

    md += "## Timeline Summary\n\n"
    md += f"- **Started:** {data['start_time']}\n"
    if data.get('detection_time'):
        md += f"- **Detected:** {data['detection_time']}\n"
    md += f"- **Resolved:** {data.get('resolution_time', 'Ongoing')}\n\n"

    md += "## Root Cause\n\n"
    md += f"{data['root_cause']}\n\n"

    md += format_business_impact(data.get('business_impact'))
    md += format_timeline(data.get('timeline', []))
    md += format_resolution_steps(data.get('resolution_steps', []))
    md += format_stakeholders(data.get('stakeholders_notified', []))
    md += format_follow_up_actions(data.get('follow_up_actions', []))

    if data.get('additional_notes'):
        md += "## Additional Notes\n\n"
        md += f"{data['additional_notes']}\n\n"

    return md


def format_business_impact(impact: dict) -> str:
    """Format the 'Business Impact' section."""
    if not impact:
        return ""

    section = "## Business Impact\n\n"
    if impact.get('description'):
        section += f"{impact['description']}\n\n"

    section += "**Metrics:**\n"
    if impact.get('downtime_duration'):
        section += f"- **Downtime:** {impact['downtime_duration']}\n"
    if impact.get('affected_users'):
        section += f"- **Affected Users:** {impact['affected_users']}\n"
    if impact.get('failed_transactions'):
        section += f"- **Failed Transactions:** {impact['failed_transactions']}\n"
    if impact.get('revenue_impact'):
        section += f"- **Revenue Impact:** {impact['revenue_impact']}\n"
    section += "\n"

    return section


def format_timeline(timeline: list) -> str:
    """Format the 'Detailed Timeline' section."""
    if not timeline:
        return ""

    section = "## Detailed Timeline\n\n"
    for event in timeline:
        actor_info = f" ({event['actor']})" if event.get('actor') else ""
        section += f"- **{event['time']}:** {event['event']}{actor_info}\n"
    section += "\n"

    return section


def format_resolution_steps(steps: list) -> str:
    """Format the 'Resolution Steps' section."""
    if not steps:
        return ""

    section = "## Resolution Steps\n\n"
    for idx, step in enumerate(steps, 1):
        section += f"{idx}. {step}\n"
    section += "\n"

    return section


def format_stakeholders(stakeholders: list) -> str:
    """Format the 'Stakeholders Notified' section."""
    if not stakeholders:
        return ""

    section = "## Stakeholders Notified\n\n"
    section += ", ".join(stakeholders)
    section += "\n\n"

    return section


def format_follow_up_actions(actions: list) -> str:
    """Format the 'Follow-up Actions' section."""
    if not actions:
        return ""

    section = "## Follow-up Actions\n\n"
    for idx, action in enumerate(actions, 1):
        priority = f"[{action.get('priority', 'medium').upper()}] " if action.get('priority') else ""
        due = f" (Due: {action['due_date']})" if action.get('due_date') else ""
        section += f"{idx}. {priority}{action['action']}\n"
        section += f"   - **Owner:** {action['owner']}{due}\n"
    section += "\n"

    return section
