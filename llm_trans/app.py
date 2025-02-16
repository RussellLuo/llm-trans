import json
import os

import gradio as gr
import yaml

from .translator import Translator


css = """
.form {
  padding: 0px;
  border: none;
}
textarea::placeholder {
  color: rgb(100,100,100)
}
textarea[placeholder="Translation"] {
  background-color: rgb(248,249,250);
}
"""

# See https://github.com/gradio-app/gradio/issues/6101.
shortcut_js = """
<script>
document.addEventListener("keydown", function(e) {
  if (e.key == "Enter" && (e.ctrlKey || e.shiftKey || e.metaKey)) {
    document.getElementById("translate_btn").click();
  }
})
</script>
"""


def load_settings(filename: str) -> tuple[list, list]:
    with open(filename, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    llm_settings = settings.get("llms")
    if not llm_settings:
        raise gr.Error("No LLMs found in settings.yaml", duration=5)

    language_settings = settings.get("languages")
    if not language_settings:
        raise gr.Error("No languges found in settings.yaml", duration=5)

    llms = []
    for llm in llm_settings:
        title = llm.pop("title", "")
        api_key = llm.get("api_key")
        if api_key.startswith("${") and api_key.endswith("}"):
            # Replace the environment variable with its value.
            var = api_key[2:-1]
            value = os.getenv(var, "")
            llm["api_key"] = value
        llms.append((title, json.dumps(llm)))

    languages = [
        ("Auto Detect", "auto"),
    ]
    for lang in language_settings:
        languages.append((lang["title"], lang["language"]))

    return llms, languages


class App:
    def __init__(self, llms: list, languages: list) -> None:
        self.LLMS: list = llms
        self.LANGUAGES: list = languages
        self.demo: gr.Blocks | None = None

    def build(self, translator: Translator) -> None:
        with gr.Blocks(title="LLM Translate", css=css, head=shortcut_js) as demo:
            self.demo = demo

            with gr.Sidebar():
                with gr.Tab("Settings"):
                    llm = gr.Dropdown(
                        label="LLM",
                        choices=self.LLMS,
                        value=self.LLMS[0][1],
                    )
                    llm.select(
                        fn=translator.switch_llm,
                        inputs=llm,
                    )

            gr.Markdown("# 🌐 LLM Translate")

            with gr.Row():
                with gr.Column():
                    source_lang = gr.Dropdown(
                        choices=self.LANGUAGES,
                        value="auto",
                        show_label=False,
                    )
                    input_text = gr.Textbox(
                        label="",
                        placeholder="Enter text",
                        lines=10,
                        max_lines=50,
                        autofocus=True,
                    )
                with gr.Column():
                    target_lang = gr.Dropdown(
                        choices=self.LANGUAGES[1:],  # Exclude "auto" option
                        value=self.LANGUAGES[1][1],  # The first language after "auto"
                        show_label=False,
                    )
                    output_text = gr.Textbox(
                        label="",
                        placeholder="Translation",
                        lines=10,
                        max_lines=50,
                        interactive=False,
                        show_copy_button=True,
                    )

            input_text.input(
                fn=translator.detect,
                inputs=[input_text],
                outputs=source_lang,
                show_progress="hidden",
            )

            translate_btn = gr.Button(
                "Translate (Enter + Ctrl/Shift/Cmd)",
                variant="primary",
                elem_id="translate_btn",
            )
            translate_btn.click(
                fn=translator.translate,
                inputs=[input_text, source_lang, target_lang],
                outputs=output_text,
                show_progress="minimal",
            )

            # Initialize app when page loads
            demo.load(translator.initialize, inputs=llm)
            # Clean up app when page is closed
            demo.unload(translator.cleanup)

    def run(
        self, server_port: int = 7860, quiet: bool = False, inbrowser: bool = True
    ) -> None:
        self.demo.launch(server_port=server_port, quiet=quiet, inbrowser=inbrowser)
