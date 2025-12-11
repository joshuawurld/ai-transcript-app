"""CalendarTool - creates .ics calendar files for action items."""

import json
import os
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from github_integration import write_issue

from .base import Tool


class CalendarTool(Tool):
    """Creates .ics calendar files with action items from meetings."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "create_calendar_reminder"

    @property
    def description(self) -> str:
        return """Create a calendar reminder with comprehensive meeting details from transcript.

Use this tool ONLY for regular meetings like:
- Standups, planning sessions, retrospectives
- Status updates and check-ins
- Brainstorming or review meetings
- Client calls and interviews

DO NOT use this tool if the transcript is about:
- Production incidents or outages (use generate_incident_report instead)
- Architecture or strategic decisions (use create_decision_record instead)

Only ONE tool should be used per transcript.

Extract and organize:
- Meeting type and summary
- Key discussion points and decisions
- Action items with owners and deadlines
- Blockers or impediments (if any)
- Urgent issues that need attention (if any)

Creates a .ics calendar file with all meeting context for easy reference."""

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "meeting_title": {
                    "type": "string",
                    "description": "Title or topic of the meeting",
                },
                "meeting_type": {
                    "type": "string",
                    "enum": ["standup", "planning", "brainstorm", "review", "client_call", "interview", "status_update", "retrospective", "other"],
                    "description": "Type of meeting",
                },
                "meeting_summary": {
                    "type": "string",
                    "description": "2-3 sentence summary of what was discussed",
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Important points or decisions from the meeting",
                },
                "action_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "The action item or task",
                            },
                            "owner": {
                                "type": "string",
                                "description": "Person responsible",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Priority level",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "When it's due (e.g., 'end of week', 'Dec 10')",
                            },
                        },
                        "required": ["task", "owner"],
                    },
                    "description": "Action items from the meeting",
                },
                "blockers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "blocker": {"type": "string"},
                            "affected_person": {"type": "string"},
                        },
                    },
                    "description": "Blockers or impediments mentioned (empty if none)",
                },
                "urgent_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issue": {"type": "string"},
                            "severity": {"type": "string", "enum": ["critical", "high", "medium"]},
                        },
                    },
                    "description": "Critical or urgent issues (empty if none)",
                },
                "reminder_date": {
                    "type": "string",
                    "description": "Calendar reminder date in YYYY-MM-DD format. If transcript mentions specific deadlines, set reminder 1-2 days before the earliest deadline. If no specific dates mentioned, use one week from today as default.",
                },
            },
            "required": ["meeting_title", "meeting_type", "meeting_summary", "key_points", "action_items", "reminder_date"],
        }

    async def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool - generate valid ICS file from LLM-provided JSON."""
        print(f"\n[calendar] Processing '{tool_input['meeting_title']}' ({tool_input['meeting_type']})")
        print(f"[calendar] {len(tool_input.get('action_items', []))} action items, reminder on {tool_input['reminder_date']}")

        try:
            reminder_time = self._parse_reminder_date(tool_input["reminder_date"])
            end_time = reminder_time + timedelta(minutes=30)

            summary = f"Meeting Reminder: {tool_input['meeting_title']}"
            description = json.dumps(tool_input, indent=2)

            ics_content = self._create_ics_content(
                summary=summary,
                description=description,
                start_time=reminder_time,
                end_time=end_time,
            )

            filename = self._generate_filename(tool_input["meeting_title"])

            print(f"[calendar] ✓ Generated {filename}")

            result = {
                "status": "success",
                "type": "calendar",
                "content": ics_content,
                "filename": filename,
                "reminder_time": reminder_time.isoformat(),
                "data": tool_input,
            }

            # Create a single GitHub issue with all meeting details (if configured)
            github_result = await write_issue("meeting_summary", tool_input)
            if github_result:
                result["github_issue"] = github_result

            return result

        except Exception as e:
            print(f"[calendar] ✗ Error: {e}")
            return {"status": "error", "message": str(e), "data": tool_input}

    def _parse_reminder_date(self, date_str: str) -> datetime:
        """Parse YYYY-MM-DD date string, fallback to 7 days from now."""
        try:
            if len(date_str) == 10 and date_str.count('-') == 2:
                year, month, day = date_str.split('-')
                return datetime(int(year), int(month), int(day), hour=9, minute=0, second=0)
        except (ValueError, AttributeError):
            pass

        fallback = datetime.now() + timedelta(days=7)
        return fallback.replace(hour=9, minute=0, second=0, microsecond=0)

    def _create_ics_content(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str = None,
    ) -> str:
        """Generate .ics file content (RFC 5545 iCalendar format)."""
        if timezone is None:
            timezone = os.getenv("CALENDAR_TIMEZONE", "America/Los_Angeles")

        uid = str(uuid4())
        now = datetime.now()

        dtstart = start_time.strftime("%Y%m%dT%H%M%S")
        dtend = end_time.strftime("%Y%m%dT%H%M%S")
        dtstamp = now.strftime("%Y%m%dT%H%M%S")

        escaped_description = description.replace("\n", "\\n")

        return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Transcript App//Action Items Reminder//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VTIMEZONE
TZID:{timezone}
END:VTIMEZONE
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;TZID={timezone}:{dtstart}
DTEND;TZID={timezone}:{dtend}
SUMMARY:{summary}
DESCRIPTION:{escaped_description}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT10M
ACTION:DISPLAY
DESCRIPTION:Reminder: {summary}
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Reminder: {summary}
END:VALARM
END:VEVENT
END:VCALENDAR"""

    def _generate_filename(self, meeting_title: str) -> str:
        """Generate a filename for the .ics file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c for c in meeting_title if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_title = safe_title.replace(" ", "_")[:50]
        filename = f"{timestamp}_{safe_title}.ics"
        return filename
