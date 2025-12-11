"""
Issue Review Agent - Fully Autonomous MCP-Powered Agentic Loop

This agent demonstrates MCP's true power: FULL AUTONOMY.

Unlike typical "AI wrapper" code where Python fetches data and feeds it to an LLM,
this agent discovers and uses MCP tools entirely on its own:

1. Discovers available GitHub tools via MCP list_tools()
2. Uses search/list tools to find issues with 'transcript-app' label
3. Decides which issues need attention
4. Takes actions (comment, label, close) autonomously
5. Moves to next issue or signals completion

The Python code only:
- Establishes the MCP connection
- Runs the agentic loop
- Provides logging for educational purposes

The AGENT (LLM) does everything else via MCP tool calls.

This is the key difference from REST:
- REST: Code decides what to call, when, with what parameters
- MCP + Agent: Agent discovers capabilities and decides autonomously

Usage:
    from github_issue_agent import review_issues

    # Called from /api/review-issues endpoint
    results = await review_issues()
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# =============================================================================
# Constants and Prompts
# =============================================================================

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"
TRANSCRIPT_APP_LABEL = "transcript-app"
MAX_ITERATIONS = 10  # Higher limit since agent does more work now

PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "issue_reviewer.txt").read_text().strip()
TASK_PROMPT_TEMPLATE = (PROMPTS_DIR / "issue_review_task.txt").read_text().strip()


# =============================================================================
# Agent Dependencies
# =============================================================================


@dataclass
class IssueReviewDeps:
    """Dependencies injected into Issue Review Agent.

    The agent has access to:
    - MCP session for executing discovered tools
    - Available tools list (discovered at runtime)
    - Repository info for constructing tool calls
    - Tracking state for the agentic loop
    """

    mcp_session: ClientSession
    available_tools: list[dict]  # Discovered at runtime via MCP!
    owner: str
    repo: str
    # Tracking for the agentic loop
    issues_reviewed: list[dict] = field(default_factory=list)
    is_fully_complete: bool = False  # True when agent has reviewed ALL issues


# =============================================================================
# Issue Review Agent (Fully Autonomous)
# =============================================================================


def _create_issue_review_agent() -> Agent[IssueReviewDeps, str]:
    """Create the fully autonomous Issue Review Agent.

    This agent has tools to:
    1. Execute any GitHub MCP tool (search, comment, label, close, etc.)
    2. Record when an issue has been reviewed
    3. Signal when ALL issues have been reviewed

    The agent runs in a loop, autonomously deciding what to do next.
    """
    model = OpenAIChatModel(
        os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5"),
        provider=OpenAIProvider(
            base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("LLM_API_KEY", ""),
        ),
    )

    agent: Agent[IssueReviewDeps, str] = Agent(
        model,
        deps_type=IssueReviewDeps,
        output_type=str,
        system_prompt=SYSTEM_PROMPT,
    )

    @agent.tool
    async def execute_mcp_tool(
        ctx: RunContext[IssueReviewDeps],
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """Execute any GitHub MCP tool.

        This is your primary way to interact with GitHub. Common tools include:
        - list_issues: Find issues (use labels filter for 'transcript-app')
        - get_issue: Get details of a specific issue
        - add_issue_comment: Add a comment to an issue
        - update_issue: Update issue state (open/closed)
        - add_labels_to_issue: Add labels to an issue
        - list_issue_comments: See existing comments

        Args:
            tool_name: Name of the MCP tool to execute
            arguments: Arguments for the tool (owner/repo auto-injected if missing)

        Returns:
            Result from the MCP tool
        """
        session = ctx.deps.mcp_session

        # Auto-inject owner/repo if not provided
        if "owner" not in arguments:
            arguments["owner"] = ctx.deps.owner
        if "repo" not in arguments:
            arguments["repo"] = ctx.deps.repo

        print("\n    ┌─────────────────────────────────────────────────")
        print(f"    │ [MCP TOOL] {tool_name}")
        print("    ├─────────────────────────────────────────────────")

        # Show arguments (excluding owner/repo for brevity)
        display_args = {
            k: v for k, v in arguments.items() if k not in ("owner", "repo")
        }
        if display_args:
            for key, value in display_args.items():
                val_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                print(f"    │   {key}: {val_str}")
        else:
            print("    │   (no additional arguments)")

        try:
            result = await session.call_tool(tool_name, arguments=arguments)

            # Parse result content
            result_text = "Action completed successfully"
            if result.content and isinstance(result.content, list) and result.content:
                first_content = result.content[0]
                result_text = (
                    first_content.text
                    if hasattr(first_content, "text")
                    else str(first_content)
                )

            # Truncate for display
            display_result = (
                result_text[:100] + "..." if len(result_text) > 100 else result_text
            )
            print(f"    │ [RESULT] ✓ {display_result}")
            print("    └─────────────────────────────────────────────────\n")

            return result_text

        except Exception as e:
            print(f"    │ [RESULT] ✗ FAILED: {e!s}")
            print("    └─────────────────────────────────────────────────\n")
            return f"Error executing {tool_name}: {e!s}"

    @agent.tool
    async def record_issue_reviewed(
        ctx: RunContext[IssueReviewDeps],
        issue_number: int,
        action_taken: str,
        summary: str,
    ) -> str:
        """Record that you've finished reviewing an issue.

        Call this after you've taken all necessary actions on a single issue.
        This tracks your progress but does NOT end the overall review session.

        Args:
            issue_number: The GitHub issue number you just reviewed
            action_taken: What you did (commented, labeled, closed, no_action_needed)
            summary: Brief summary of what was done

        Returns:
            Confirmation and count of issues reviewed so far
        """
        ctx.deps.issues_reviewed.append({
            "issue_number": issue_number,
            "action_taken": action_taken,
            "summary": summary,
        })

        reviewed_count = len(ctx.deps.issues_reviewed)

        print("\n    ┌─────────────────────────────────────────────────")
        print(f"    │ [ISSUE REVIEWED] #{issue_number}")
        print("    ├─────────────────────────────────────────────────")
        print(f"    │   Action: {action_taken}")
        print(f"    │   Summary: {summary[:50]}...")
        print(f"    │   Total reviewed: {reviewed_count}")
        print("    └─────────────────────────────────────────────────\n")

        return (
            f"Recorded issue #{issue_number}. "
            f"Total reviewed: {reviewed_count}. "
            "Continue reviewing or call finish_all_reviews when done."
        )

    @agent.tool
    async def finish_all_reviews(
        ctx: RunContext[IssueReviewDeps],
        final_summary: str,
    ) -> str:
        """Signal that you have finished reviewing ALL issues.

        Call this ONLY when you have:
        1. Searched for all issues with the 'transcript-app' label
        2. Reviewed each one (or determined no action needed)
        3. Are confident there are no more issues to process

        Args:
            final_summary: Summary of the entire review session

        Returns:
            Confirmation that the review session is complete
        """
        ctx.deps.is_fully_complete = True
        reviewed_count = len(ctx.deps.issues_reviewed)

        print("\n    ╔═════════════════════════════════════════════════")
        print("    ║ [ALL REVIEWS COMPLETE]")
        print("    ╠═════════════════════════════════════════════════")
        print(f"    ║ Issues reviewed: {reviewed_count}")
        print(f"    ║ Summary: {final_summary[:60]}...")
        if ctx.deps.issues_reviewed:
            print("    ║ Breakdown:")
            for issue in ctx.deps.issues_reviewed:
                print(f"    ║   #{issue['issue_number']}: {issue['action_taken']}")
        print("    ╚═════════════════════════════════════════════════\n")

        return f"Review session complete. Reviewed {reviewed_count} issue(s)."

    return agent


# Lazy initialization
_issue_review_agent: Agent[IssueReviewDeps, str] | None = None


def _get_issue_review_agent() -> Agent[IssueReviewDeps, str]:
    """Get or create the Issue Review Agent."""
    global _issue_review_agent
    if _issue_review_agent is None:
        _issue_review_agent = _create_issue_review_agent()
    return _issue_review_agent


# =============================================================================
# Agentic Loop
# =============================================================================


def _build_task_prompt(available_tools: list[dict], owner: str, repo: str) -> str:
    """Build the task prompt from template file."""
    return TASK_PROMPT_TEMPLATE.format(
        owner=owner,
        repo=repo,
        label=TRANSCRIPT_APP_LABEL,
        available_tools=json.dumps(available_tools, indent=2),
    )


def _build_continuation_prompt(reviewed_count: int) -> str:
    """Build prompt for subsequent iterations."""
    return f"""Continue your review session.

Progress so far: {reviewed_count} issue(s) reviewed.

If you've processed all issues with the '{TRANSCRIPT_APP_LABEL}' label, call `finish_all_reviews`.
Otherwise, continue finding and reviewing issues."""


async def _run_autonomous_loop(
    agent: Agent[IssueReviewDeps, str],
    deps: IssueReviewDeps,
) -> dict[str, Any]:
    """Run the fully autonomous agentic loop.

    The agent will:
    1. Search for issues via MCP
    2. Process each one
    3. Signal completion when done

    We keep calling the agent until it signals is_fully_complete.
    """
    iteration = 0
    total_tokens = {"input": 0, "output": 0}
    total_tool_calls = 0

    print("\n" + "=" * 70)
    print("[AUTONOMOUS AGENT] Starting fully autonomous issue review")
    print(f"[AUTONOMOUS AGENT] Repository: {deps.owner}/{deps.repo}")
    print(f"[AUTONOMOUS AGENT] Looking for label: '{TRANSCRIPT_APP_LABEL}'")
    print(f"[AUTONOMOUS AGENT] Max iterations: {MAX_ITERATIONS}")
    print(f"[AUTONOMOUS AGENT] Available MCP tools: {len(deps.available_tools)}")
    print("=" * 70)

    # Initial prompt from template
    prompt = _build_task_prompt(deps.available_tools, deps.owner, deps.repo)

    while not deps.is_fully_complete and iteration < MAX_ITERATIONS:
        iteration += 1
        print("\n" + "-" * 60)
        print(f"[ITERATION {iteration}/{MAX_ITERATIONS}]")
        print("-" * 60)

        if iteration > 1:
            prompt = _build_continuation_prompt(len(deps.issues_reviewed))

        print(f"[PROMPT] {prompt[:100]}...")

        try:
            print("[LLM] Sending request to model...")
            result = await agent.run(prompt, deps=deps)

            # Extract token usage if available
            if hasattr(result, "usage") and result.usage:
                usage = result.usage
                input_tokens = getattr(usage, "input_tokens", 0) or getattr(
                    usage, "prompt_tokens", 0
                )
                output_tokens = getattr(usage, "output_tokens", 0) or getattr(
                    usage, "completion_tokens", 0
                )
                total_tokens["input"] += input_tokens
                total_tokens["output"] += output_tokens
                print(
                    f"[TOKENS] This iteration: {input_tokens} in / {output_tokens} out"
                )
                print(
                    f"[TOKENS] Running total: "
                    f"{total_tokens['input']} in / {total_tokens['output']} out"
                )

            # Count tool calls
            if hasattr(result, "all_messages"):
                for msg in result.all_messages():
                    if hasattr(msg, "parts"):
                        for part in msg.parts:
                            if hasattr(part, "tool_name"):
                                total_tool_calls += 1

            # Show agent's response
            response = result.output[:200] if result.output else "(no output)"
            print(f"[RESPONSE] {response}...")

            # Check status
            if deps.is_fully_complete:
                print("[STATUS] Agent signaled ALL REVIEWS COMPLETE")
            else:
                reviewed_count = len(deps.issues_reviewed)
                print(f"[STATUS] Continuing... ({reviewed_count} issues reviewed)")

        except Exception as e:
            print(f"[ERROR] Iteration {iteration} failed: {e}")
            import traceback

            traceback.print_exc()
            continue

    # Final summary
    print("\n" + "=" * 70)
    print("[AUTONOMOUS AGENT COMPLETE]")
    print("=" * 70)

    if deps.is_fully_complete:
        print("[RESULT] Agent completed all reviews successfully")
    else:
        print(f"[RESULT] Hit max iterations ({MAX_ITERATIONS})")

    print(f"[RESULT] Total iterations: {iteration}")
    print(f"[RESULT] Total MCP tool calls: {total_tool_calls}")
    print(f"[RESULT] Issues reviewed: {len(deps.issues_reviewed)}")
    print(
        f"[RESULT] Tokens used: "
        f"{total_tokens['input']} input / {total_tokens['output']} output"
    )

    if deps.issues_reviewed:
        print("[RESULT] Issues breakdown:")
        for issue in deps.issues_reviewed:
            summary_preview = issue["summary"][:40] + "..."
            print(f"  #{issue['issue_number']}: {issue['action_taken']} - {summary_preview}")

    return {
        "success": True,
        "iterations": iteration,
        "issues_reviewed": deps.issues_reviewed,
        "total_tool_calls": total_tool_calls,
        "tokens_used": total_tokens,
        "completed": deps.is_fully_complete,
    }


# =============================================================================
# Main Entry Point
# =============================================================================


async def review_issues() -> dict[str, Any]:
    """Launch the fully autonomous issue review agent.

    This function:
    1. Connects to GitHub MCP server
    2. Discovers available tools (THIS IS MCP'S VALUE!)
    3. Launches the autonomous agent
    4. The agent finds and processes issues entirely on its own

    The key educational point: we don't fetch issues in Python code.
    The AGENT discovers and fetches them via MCP tools.

    Returns:
        dict with success status, issues reviewed, and metrics
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_ISSUES_REPO")

    if not token or not repo:
        return {
            "success": False,
            "error": "GitHub not configured (GITHUB_TOKEN or GITHUB_ISSUES_REPO missing)",
            "issues_reviewed": [],
        }

    try:
        owner, repo_name = repo.split("/")
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid GITHUB_ISSUES_REPO format: {repo}",
            "issues_reviewed": [],
        }

    print("\n" + "=" * 70)
    print("[SETUP] Connecting to GitHub MCP server...")
    print("=" * 70)

    def httpx_client_factory():
        return httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"})

    try:
        async with (
            streamablehttp_client(
                GITHUB_MCP_URL, httpx_client_factory=httpx_client_factory
            ) as (read, write, _),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            print("[SETUP] MCP session established")

            # DYNAMIC TOOL DISCOVERY - This is MCP's value!
            print("[SETUP] Discovering available tools...")
            tools_response = await session.list_tools()
            available_tools = [
                {"name": t.name, "description": t.description}
                for t in tools_response.tools
            ]

            print(f"[SETUP] Discovered {len(available_tools)} tools via MCP:")
            for tool in available_tools[:8]:
                desc = tool["description"]
                desc_preview = desc[:50] + "..." if len(desc) > 50 else desc
                print(f"  • {tool['name']}: {desc_preview}")
            if len(available_tools) > 8:
                print(f"  ... and {len(available_tools) - 8} more")

            # Create agent and dependencies
            agent = _get_issue_review_agent()
            deps = IssueReviewDeps(
                mcp_session=session,
                available_tools=available_tools,
                owner=owner,
                repo=repo_name,
            )

            # Run the autonomous agent!
            return await _run_autonomous_loop(agent, deps)

    except ExceptionGroup as eg:
        print(f"[ERROR] MCP error: {eg}")
        for i, exc in enumerate(eg.exceptions):
            print(f"[ERROR]   Sub-exception {i + 1}: {type(exc).__name__}: {exc}")
        first_exc = eg.exceptions[0] if eg.exceptions else eg
        return {
            "success": False,
            "error": f"MCP connection error: {first_exc!s}",
            "issues_reviewed": [],
        }

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "issues_reviewed": [],
        }
