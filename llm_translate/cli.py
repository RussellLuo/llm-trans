import argparse

from coagent.core import set_stderr_logger

from .app import App, load_settings
from .translator import Translator


def main():
    parser = argparse.ArgumentParser(
        description="Your personal Language Translator powered by LLMs."
    )
    parser.add_argument(
        "settings", type=str, help="The path to the settings file (in YAML)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="The port number. (Defaults to %(default)r)",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="INFO",
        help="The logging level. (Defaults to %(default)r)",
    )
    args = parser.parse_args()

    set_stderr_logger(args.level)

    llms, languages = load_settings(args.settings)
    translator = Translator(languages)
    app = App(llms, languages)
    app.build(translator)
    app.run(server_port=args.port, quiet=True, inbrowser=True)


if __name__ == "__main__":
    main()
