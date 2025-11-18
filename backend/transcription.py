#!/usr/bin/env python3
"""
OpenAI API-compatible transcription service.
Works with OpenRouter, Ollama, OpenAI, LM Studio, and other providers.
"""

from pathlib import Path

from faster_whisper import WhisperModel
from openai import OpenAI

from agent import Agent
from tools import ToolRegistry, CalendarTool, IncidentTool, DecisionRecordTool

PROMPT_FILE = Path(__file__).parent / "system_prompt.txt"
SYSTEM_PROMPT = PROMPT_FILE.read_text().strip()


class TranscriptionService:
    """Transcription service using Whisper + LLM with agentic workflow."""

    def __init__(
        self, whisper_model: str, llm_base_url: str, llm_api_key: str, llm_model: str
    ):
        print(f"🔄 Loading Whisper model '{whisper_model}'...")
        self.whisper = WhisperModel(whisper_model, device="auto", compute_type="int8")
        print(f"✅ Whisper model '{whisper_model}' loaded!")

        print(f"🔄 Connecting to LLM at {llm_base_url}...")
        print(f"    Using model: {llm_model}")

        self.llm_client = OpenAI(base_url=llm_base_url, api_key=llm_api_key)
        self.llm_model = llm_model

        try:
            if "openrouter.ai" not in llm_base_url:
                self.llm_client.models.list()
            print(f"✅ Connected to LLM API!")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to LLM: {e}")
            print(f"   Make sure your LLM server is running at {llm_base_url}")

        # Set up the agent with tools
        self._setup_agent()

    def transcribe(self, audio_file):
        print("🔄 Transcribing...")

        segments, _info = self.whisper.transcribe(
            audio_file, beam_size=5, language="en", condition_on_previous_text=False
        )

        text = " ".join([segment.text for segment in segments]).strip()
        print(f"📝 Raw: {text}")
        return text

    def _setup_agent(self):
        """Initialize the agent with the meeting processing tool."""
        print("\n🔧 Setting up agent...")

        tool_registry = ToolRegistry()
        tool_registry.register(CalendarTool())
        tool_registry.register(IncidentTool())
        tool_registry.register(DecisionRecordTool())

        self.agent = Agent(
            llm_client=self.llm_client, model=self.llm_model, tool_registry=tool_registry
        )

        print("✅ Agent ready!\n")

    def get_default_system_prompt(self):
        """Get the default system prompt for text cleaning."""
        return SYSTEM_PROMPT

    def process_with_agent(self, text: str) -> dict:
        """Process transcript using agentic workflow."""
        return self.agent.process_transcript(text)

    def clean_with_llm(self, text, system_prompt=None):
        if not text:
            return ""

        prompt_to_use = system_prompt if system_prompt else SYSTEM_PROMPT

        print("🤖 Cleaning with LLM...")

        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": prompt_to_use},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            cleaned = response.choices[0].message.content.strip()
            print(f"✨ Cleaned: {cleaned}")
            return cleaned

        except Exception as e:
            print(f"⚠️  LLM error: {e}")
            return text

    def transcribe_file(self, audio_file_path: str, use_llm: bool = True) -> dict:
        raw_text = self.transcribe(audio_file_path)

        result = {"raw_text": raw_text}

        if use_llm and raw_text:
            cleaned_text = self.clean_with_llm(raw_text)
            result["cleaned_text"] = cleaned_text
        else:
            result["cleaned_text"] = raw_text

        return result
