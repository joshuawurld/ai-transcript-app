"""
Exercise 2: Creating and Running a PydanticAI Agent
===================================================

In this exercise, you'll learn what an Agent is and how to use one.
By the end, you'll understand:

- What an Agent is (and isn't)
- How instructions shape the LLM's behavior
- How to run an agent and get results
- When you need an agent vs a simple LLM call

Difficulty: Beginner
Time: ~30 minutes

Run: uv run python exercises/02_basic_agent.py

📚 DOCUMENTATION LINKS:
- PydanticAI Agents: https://ai.pydantic.dev/agents/
- Running Agents: https://ai.pydantic.dev/agents/#running-agents
- Agent Results: https://ai.pydantic.dev/results/

⚠️  IMPORTANT: When asking AI assistants for help, ALWAYS include the doc URL!
    Libraries evolve over time, and AI models may have outdated information.
"""

# =============================================================================
# CONCEPT: What is an Agent?
# =============================================================================
#
# An Agent is PydanticAI's way of packaging everything needed to interact
# with an LLM:
#
#   - Model: Which LLM to use (GPT-4, Claude, etc.)
#   - Instructions: How the LLM should behave (like a system prompt)
#   - Tools: Functions the LLM can call (covered in Exercise 3)
#   - Dependencies: Runtime data to pass in (covered in Exercise 4)
#   - Output type: What format the response should be in
#
# Think of an Agent as a reusable "LLM configuration" that you can call
# multiple times with different inputs.
#
# 🤖 Ask your AI assistant:
#    "Read https://ai.pydantic.dev/agents/ and summarize the main
#     components of a PydanticAI Agent"
# =============================================================================

import json

from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

# =============================================================================
# CONCEPT: TestModel - For Learning Without API Costs
# =============================================================================
#
# TestModel is a FAKE LLM that doesn't call any API. It returns instant,
# predictable responses. This is perfect for:
#
#   - Learning PydanticAI without spending money
#   - Writing tests for your agent code
#   - Debugging agent logic
#
# To see how to connect to a real LLM, check out backend/agent.py
# It uses OpenRouter with the OpenAI-compatible API format.
#
# 📚 Docs: https://ai.pydantic.dev/models/
# =============================================================================


# =============================================================================
# CONCEPT: Understanding Agent[None, str]
# =============================================================================
#
# The type hint Agent[None, str] tells you two things:
#
#   Agent[DepsType, OutputType]
#         ↑          ↑
#         |          └── What the agent returns (str = plain text)
#         └── What dependencies it needs (None = no dependencies)
#
# This typing helps your IDE provide autocomplete and catch errors.
# We'll cover dependencies in Exercise 4 - for now, None means "no deps".
#
# =============================================================================


def create_simple_agent() -> Agent[None, str]:
    """Create a basic agent with instructions."""

    # Use TestModel for learning - no API calls!
    model = TestModel()

    # Create the agent
    agent: Agent[None, str] = Agent(
        model,
        instructions=(
            "You are a helpful assistant. Be concise and friendly in your responses."
        ),
    )

    return agent


# =============================================================================
# CONCEPT: What are "instructions"?
# =============================================================================
#
# Instructions are like a system prompt - they tell the LLM how to behave
# for ALL interactions with this agent.
#
# Good instructions are:
#   - Clear about the agent's role: "You are a customer support agent"
#   - Specific about behavior: "Always ask clarifying questions"
#   - Relevant to the task: "Focus on technical Python questions"
#
# The LLM sees these instructions before every user message.
#
# =============================================================================


def demo_running_agent():
    """Show how to run an agent and get results."""
    print("=" * 60)
    print("DEMO: Running an Agent")
    print("=" * 60)

    agent = create_simple_agent()

    # run_sync() sends a message and waits for the response
    result = agent.run_sync("Hello!")

    print("\nInput: 'Hello!'")
    print(f"Output: {result.output}")
    print(f"Output type: {type(result.output).__name__}")


def demo_custom_response():
    """Show how TestModel can return specific text for testing."""
    print("\n" + "=" * 60)
    print("DEMO: Custom Test Responses")
    print("=" * 60)

    # Configure TestModel to return specific text
    model = TestModel(custom_output_text="I'm a test response!")

    agent: Agent[None, str] = Agent(
        model,
        instructions="You are helpful.",
    )

    result = agent.run_sync("Say something")
    print(f"\nWith custom_output_text: {result.output}")
    print("\n💡 This is useful for testing specific scenarios!")


def demo_multiple_runs():
    """Show that each run is independent."""
    print("\n" + "=" * 60)
    print("DEMO: Multiple Independent Runs")
    print("=" * 60)

    agent = create_simple_agent()

    # Each run is independent - no memory between calls
    prompts = ["First message", "Second message", "Third message"]

    for prompt in prompts:
        result = agent.run_sync(prompt)
        print(f"\nInput: '{prompt}'")
        print(f"Output: {result.output}")

    print("\n💡 By default, each run starts fresh - no conversation memory!")
    print("   (You can pass message_history to continue conversations)")


# =============================================================================
# CONCEPT: When Do You Actually Need an Agent?
# =============================================================================
#
# PydanticAI Agents are powerful, but they're not always necessary.
#
# ✅ USE AN AGENT WHEN:
#   - You need tools (functions the LLM can call)
#   - You need structured output (Pydantic model responses)
#   - You need dependency injection (runtime context)
#   - You want automatic retries on validation errors
#   - You're building something reusable
#
# ❌ CONSIDER SIMPLER APPROACHES WHEN:
#   - You just need a one-off LLM call
#   - The output is simple text
#   - You don't need tools or structured data
#   - Token cost is a major concern
#
# Simple alternative (no framework):
#
#   from openai import OpenAI
#   client = OpenAI()
#   response = client.chat.completions.create(
#       model="gpt-4o",
#       messages=[{"role": "user", "content": "Hello!"}]
#   )
#   print(response.choices[0].message.content)
#
# Know when each approach makes sense!
#
# =============================================================================


def demo_agent_overhead():
    """Illustrate that agents add structure (which may or may not be needed)."""
    print("\n" + "=" * 60)
    print("DEMO: Agent Structure vs Simple Calls")
    print("=" * 60)

    print("\n📦 With PydanticAI Agent:")
    print("   - Structured Agent object")
    print("   - Type safety with Agent[DepsType, OutputType]")
    print("   - Built-in retry logic")
    print("   - Tool registration system")
    print("   - Result object with metadata")

    print("\n📝 With direct API call:")
    print("   - Just a function call")
    print("   - String in, string out")
    print("   - You handle errors yourself")
    print("   - Simpler, less overhead")

    print("\n💡 Neither is 'better' - choose based on your needs!")


# =============================================================================
# CONCEPT: The Retry Loop - Why Validators Matter for AI
# =============================================================================
#
# One of the most POWERFUL features of PydanticAI is automatic retries
# when validation fails. Here's what happens:
#
#   1. You ask the agent to return structured data (output_type=SomeModel)
#   2. The LLM generates data
#   3. Pydantic validates it
#   4. If validation FAILS:
#      a. PydanticAI catches the ValidationError
#      b. Sends the error message BACK to the LLM
#      c. The LLM gets a chance to CORRECT its mistake
#      d. Repeat until valid (or max retries reached)
#
# This is WHY your validator error messages matter - the LLM reads them!
#
#   ❌ Bad:  raise ValueError("Invalid")
#   ✅ Good: raise ValueError("hours must be positive, got -5. Use a positive number.")
#
# The demo below shows this ACTUALLY HAPPENING with a mock LLM.
#
# 📚 Docs: https://ai.pydantic.dev/agents/#retries
# =============================================================================


# =============================================================================
# CONCEPT: What is "final_result"? (How Structured Output Works Internally)
# =============================================================================
#
# When you set output_type on an agent, PydanticAI doesn't just tell the LLM
# "return this JSON structure." It actually creates a HIDDEN TOOL called
# "final_result" that the LLM calls to return structured data.
#
#   agent = Agent(model, output_type=MyModel)  # Under the hood...
#   # PydanticAI creates: tool "final_result" with MyModel as input schema
#
# This is why the retry demo below uses tool_name="final_result":
#
#   ToolCallPart(
#       tool_name="final_result",  # <-- This is the hidden tool!
#       args=json.dumps({"task": "...", "hours": -5}),
#       ...
#   )
#
# The flow looks like this:
#
#   1. Agent has output_type=ValidatedTask
#   2. LLM sees "final_result" tool with ValidatedTask schema
#   3. LLM calls final_result(task="...", hours=-5)
#   4. PydanticAI validates using ValidatedTask model
#   5. Validation fails → error sent back to LLM
#   6. LLM retries with final_result(task="...", hours=2)
#   7. Validation passes → result.output is a ValidatedTask instance
#
# This is an implementation detail, but understanding it helps you:
#   - Understand why the mock model returns ToolCallPart
#   - Debug when structured output isn't working
#   - Understand the relationship between tools and output_type
#
# =============================================================================


# --- Pydantic model with validation ---
class ValidatedTask(BaseModel):
    """A task with strict validation - hours MUST be positive."""

    task: str = Field(description="The task description")
    hours: float = Field(description="Estimated hours to complete")

    @field_validator("hours")
    @classmethod
    def hours_must_be_positive(cls, v):
        if v <= 0:
            # This message is sent to the LLM on retry!
            raise ValueError(
                f"hours must be positive (you provided {v}). "
                f"Please use a positive number like 0.5, 1, 2, or 4."
            )
        return v


# --- State tracker for the demo ---
_retry_demo_calls = 0


async def _retry_demo_model(
    _messages: list[ModelMessage], _info: AgentInfo
) -> ModelResponse:
    """A mock LLM that returns INVALID data first, then VALID data on retry.

    This simulates what happens with a real LLM when validation fails.
    """
    global _retry_demo_calls
    _retry_demo_calls += 1

    print(f"\n  📤 LLM Response #{_retry_demo_calls}")

    if _retry_demo_calls == 1:
        # FIRST RESPONSE: Return invalid data (negative hours)
        print("     → Returning: hours = -5 (INVALID)")
        print("       This will FAIL Pydantic validation!")
        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="final_result",
                    args=json.dumps(
                        {
                            "task": "Fix the authentication bug",
                            "hours": -5,  # Invalid! Validator will reject this.
                        }
                    ),
                    tool_call_id="call_1",
                )
            ]
        )
    # RETRY RESPONSE: The LLM "saw" the error and corrected itself
    print("     → Returning: hours = 2 (VALID)")
    print("       The LLM 'read' the error and fixed it!")
    return ModelResponse(
        parts=[
            ToolCallPart(
                tool_name="final_result",
                args=json.dumps(
                    {"task": "Fix the authentication bug", "hours": 2}  # Valid!
                ),
                tool_call_id="call_2",
            )
        ]
    )


def demo_retry_loop():
    """
    🔄 WATCH THE RETRY LOOP IN ACTION!

    This is the most important demo - it shows WHY validators matter for AI.
    The mock LLM intentionally returns invalid data first, and you can see
    PydanticAI catch the error, send it back, and get corrected data.
    """
    global _retry_demo_calls
    _retry_demo_calls = 0  # Reset state

    print("\n" + "=" * 60)
    print("🔄 DEMO: Watching the Retry Loop in Action")
    print("=" * 60)

    print(
        """
This demo shows the COMPLETE validation retry loop:

  1. We ask the agent to extract a task (with hours estimate)
  2. The mock LLM returns hours = -5 (INVALID!)
  3. Pydantic validation FAILS with our helpful error message
  4. PydanticAI sends the error BACK to the LLM
  5. The LLM "reads" the error and returns hours = 2 (VALID!)
  6. Validation passes - success!

Watch the output below to see each step happen...
"""
    )

    # Create agent with our mock model
    mock_model = FunctionModel(_retry_demo_model)

    agent: Agent[None, ValidatedTask] = Agent(
        mock_model,
        output_type=ValidatedTask,
        retries=3,  # Allow up to 3 retries
    )

    print("-" * 60)
    print("Running agent.run_sync()...")
    print("-" * 60)

    result = agent.run_sync("Extract: Fix the auth bug, about 2 hours work")

    print("\n" + "-" * 60)
    print("✅ SUCCESS!")
    print("-" * 60)
    print("\nFinal validated output:")
    print(f"  task: {result.output.task}")
    print(f"  hours: {result.output.hours}")
    print(f"\nTotal LLM calls: {_retry_demo_calls}")

    print(
        """
💡 KEY TAKEAWAYS:
   - The validator's error message was sent to the LLM
   - The LLM used that feedback to correct its output
   - Your error messages should be HELPFUL (tell the LLM how to fix it)
   - This "retry loop" makes validators powerful for AI applications!

   This is what we explained in Exercise 1 - now you've SEEN it happen!
"""
    )


if __name__ == "__main__":
    demo_running_agent()
    demo_custom_response()
    demo_multiple_runs()
    demo_agent_overhead()
    demo_retry_loop()  # 🔄 The most important demo - shows validation retry!

    print("\n" + "=" * 60)
    print("DEMOS COMPLETE - Now try the exercises below!")
    print("=" * 60)


# =============================================================================
# =============================================================================
#
#   YOUR TURN: EXERCISES
#
# =============================================================================
# =============================================================================


# =============================================================================
# EXERCISE 1: Create an agent with a specific personality
# =============================================================================
#
# Create an agent with custom instructions that give it a personality.
#
# STEP 1: Write the function
#
#   def create_pirate_agent() -> Agent[None, str]:
#       """An agent that talks like a pirate."""
#       model = TestModel(
#           custom_output_text="Ahoy! What treasure be ye seekin'?"
#       )
#
#       agent: Agent[None, str] = Agent(
#           model,
#           instructions="_____",  # Write pirate personality instructions!
#       )
#       return agent
#
# STEP 2: Test it
#
#   agent = create_pirate_agent()
#   result = agent.run_sync("Hello!")
#   print(result.output)
#
# STEP 3: Try different personalities
#   - A formal British butler
#   - An excited sports commentator
#   - A patient teacher
#
# 💡 HINTS:
#   - Instructions shape ALL responses from this agent
#   - Be specific: "Always say 'Arrr!'" vs "Talk like a pirate"
#   - custom_output_text simulates what a real LLM might say
#
# 🤖 Ask your AI assistant:
#   - "Read https://ai.pydantic.dev/agents/ and show me how instructions
#      affect agent behavior"
# =============================================================================


# =============================================================================
# EXERCISE 2: Examine the result object
# =============================================================================
#
# The result from agent.run_sync() isn't just a string - it's a rich object
# with useful information.
#
# STEP 1: Run an agent and explore the result
#
#   agent = create_simple_agent()
#   result = agent.run_sync("Tell me something")
#
#   print(f"Output: {result.output}")
#   print(f"Type: {type(result)}")
#
#   # What methods/attributes does result have?
#   print([attr for attr in dir(result) if not attr.startswith('_')])
#
# STEP 2: Look at the message history
#
#   for i, msg in enumerate(result.all_messages()):
#       print(f"\nMessage {i}: {type(msg).__name__}")
#
# STEP 3: Answer these questions
#
#   Q1: What type is the result object?
#   A1: _____
#
#   Q2: What does result.all_messages() return?
#   A2: _____
#
#   Q3: Why might you need access to the message history?
#   A3: _____  (Hint: think about tool calls in Exercise 3)
#
# STEP 4: Check token usage (important for cost awareness!)
#
#   print(f"Usage: {result.usage()}")
#   # Returns: Usage(requests=1, request_tokens=X, response_tokens=Y, total_tokens=Z)
#
#   Remember from Exercise 1: retries cost tokens! If the retry demo
#   runs twice, you'd see request_tokens doubled compared to a single run.
#
# 🤖 Ask your AI assistant:
#   - "Read https://ai.pydantic.dev/results/ and explain what's in
#      an AgentRunResult"
# =============================================================================


# =============================================================================
# EXERCISE 3: Think about when to use agents (thought exercise)
# =============================================================================
#
# For each scenario, decide: Agent or simple API call?
#
# SCENARIO A: Chat with customer support context
#   - Need to remember conversation history
#   - May need to look up order information (tool)
#   - Should respond in a specific format
#
#   Your answer: _____
#   Why: _____
#
#
# SCENARIO B: Summarize a document
#   - One-off task
#   - Just need a text summary back
#   - No tools or special formatting needed
#
#   Your answer: _____
#   Why: _____
#
#
# SCENARIO C: Extract structured data from emails
#   - Need specific fields (sender, subject, action items)
#   - Should validate the extracted data
#   - Will process many emails
#
#   Your answer: _____
#   Why: _____
#
#
# SCENARIO D: Generate a creative story
#   - Just need text output
#   - No validation needed
#   - Simple prompt in, story out
#
#   Your answer: _____
#   Why: _____
#
#
# 💡 KEY INSIGHT:
#   Agents shine when you need structure, tools, or validation.
#   For simple text-in-text-out tasks, direct API calls may be simpler.
#
# =============================================================================


# =============================================================================
# EXERCISE 4: Async vs Sync
# =============================================================================
#
# PydanticAI supports both synchronous and asynchronous execution:
#
#   # Synchronous (blocking)
#   result = agent.run_sync("Hello")
#
#   # Asynchronous (non-blocking)
#   result = await agent.run("Hello")
#
# STEP 1: Try the async version
#
#   import asyncio
#
#   async def main():
#       agent = create_simple_agent()
#       result = await agent.run("Hello async!")
#       print(result.output)
#
#   asyncio.run(main())
#
# STEP 2: Think about when you'd use each
#
#   Q: When would async be beneficial?
#   A: _____  (Hint: web servers, processing multiple requests)
#
#   Q: When is sync simpler?
#   A: _____  (Hint: scripts, notebooks, simple programs)
#
# 📚 Docs: https://ai.pydantic.dev/agents/#running-agents
# =============================================================================


# =============================================================================
# BONUS: Continue a conversation
# =============================================================================
#
# By default, each run_sync() call is independent. To continue a conversation,
# pass the message history from the previous result:
#
#   # First message
#   result1 = agent.run_sync("My name is Alice")
#
#   # Continue the conversation
#   result2 = agent.run_sync(
#       "What's my name?",
#       message_history=result1.all_messages()
#   )
#
# Try it! The agent should remember information from earlier messages.
#
# 🤖 Ask your AI assistant:
#   - "Read https://ai.pydantic.dev/agents/#agent-run and explain how
#      message_history enables multi-turn conversations"
# =============================================================================
