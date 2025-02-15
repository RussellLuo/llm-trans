import json
from typing import AsyncIterator

from coagent.agents import ChatMessage, ModelClient
from coagent.agents.structured_agent import StructuredAgent
from coagent.core import AgentSpec, Message, new, set_stderr_logger
from coagent.runtimes import LocalRuntime
import gradio as gr


set_stderr_logger()


class Input(Message):
    input_text: str
    source_lang: str
    target_lang: str


class Translator:
    runtime = LocalRuntime()
    started: bool = False

    agent = AgentSpec(
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

    @classmethod
    async def initialize(cls, request: gr.Request, llm: str):
        if cls.started:
            return

        await cls.runtime.start()
        await cls.runtime.register(cls.agent)

        # Switch to the first LLM by default.
        await cls.switch_llm(request, llm)

        cls.started = True

    @classmethod
    async def cleanup(cls, request: gr.Request):
        await cls.runtime.stop()
        cls.started = False

    @classmethod
    async def switch_llm(cls, request: gr.Request, llm: str):
        settings = json.loads(llm)
        # print(f"Switching LLM to {settings['model']}")
        cls.agent.constructor.kwargs["client"] = ModelClient(**settings)

    @classmethod
    async def translate(
        cls, input_text: str, source_lang: str, target_lang: str
    ) -> AsyncIterator[str]:
        if not input_text:
            yield ""
            return

        if source_lang == target_lang:
            yield input_text
            return

        result = await cls.agent.run(
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
