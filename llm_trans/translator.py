import json
from typing import AsyncIterator

from coagent.agents import ChatAgent, ChatMessage, ModelClient
from coagent.agents.structured_agent import StructuredAgent
from coagent.core import AgentSpec, Message, new
from coagent.runtimes import LocalRuntime
import gradio as gr


class Input(Message):
    input_text: str
    source_lang: str
    target_lang: str


class Translator:
    def __init__(self, languages: list[str]) -> None:
        self.runtime = LocalRuntime()
        self.started: bool = False
        self.candidate_languages = [lang for _, lang in languages[1:]]  # Exclude "auto"

        langs = "\n".join([f"- {lang}" for lang in self.candidate_languages])
        self.detection_agent = AgentSpec(
            "detector",
            new(
                ChatAgent,
                system=f"""\
You are a language detector who is dedicated to detect the language of the given text.

Your output must be one of the following languages (and nothing else):
{langs}
""",
            ),
        )

        self.translation_agent = AgentSpec(
            "translator",
            new(
                StructuredAgent,
                input_type=Input,
                system="""
    {%- if source_lang == "auto" -%}
    You are a professional translator who is dedicated to translate the given text to {{ target_lang }}.
    {%- else -%}
    You are a professional translator who is dedicated to translate the given text from {{ source_lang }} to {{ target_lang }}.
    {%- endif -%}
    """,
                messages=[
                    ChatMessage(
                        role="user",
                        content="{{ input_text }}",
                    )
                ],
            ),
        )

    async def initialize(self, request: gr.Request, llm: str):
        if self.started:
            return

        await self.runtime.start()
        await self.runtime.register(self.detection_agent)
        await self.runtime.register(self.translation_agent)

        # Switch to the first LLM by default.
        await self.switch_llm(request, llm)

        self.started = True

    async def cleanup(self, request: gr.Request):
        await self.runtime.stop()
        self.started = False

    async def switch_llm(self, request: gr.Request, llm: str):
        settings = json.loads(llm)
        # print(f"Switching LLM to {settings['model']}")

        client = ModelClient(**settings)
        self.detection_agent.constructor.kwargs["client"] = client
        self.translation_agent.constructor.kwargs["client"] = client

    async def detect(self, input_text: str) -> str:
        if not input_text:
            return "auto"

        # print(f'Detecting language for "{input_text}"')
        result = await self.detection_agent.run(
            ChatMessage(role="user", content=input_text).encode(),
        )
        msg = ChatMessage.decode(result)
        detected = msg.content

        if detected.startswith("Failed to chat with"):
            raise gr.Error(detected)

        # print(f"Detected language: {detected}")
        if detected in self.candidate_languages:
            return detected
        else:
            return "auto"  # Fallback to "auto"

    async def translate(
        self, input_text: str, source_lang: str, target_lang: str
    ) -> AsyncIterator[str]:
        if not input_text:
            yield ""
            return

        if source_lang == target_lang:
            yield input_text
            return

        result = await self.translation_agent.run(
            Input(
                input_text=input_text, source_lang=source_lang, target_lang=target_lang
            ).encode(),
            stream=True,
        )

        complete_content = ""
        async for chunk in result:
            msg = ChatMessage.decode(chunk)
            complete_content += msg.content
            yield complete_content
