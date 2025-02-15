import argparse

from coagent.core import set_stderr_logger
from .app import App


def main():
    parser = argparse.ArgumentParser(
        description="Your personal Language Translator powered by LLMs."
    )
    parser.add_argument(
        "settings", type=str, help="The path to the settings file (in YAML)."
    )
    parser.add_argument(
        "--port", type=int, help="The port number (optional).", default=7860
    )
    args = parser.parse_args()

    set_stderr_logger()

    app = App(args.settings)
    app.build()
    app.run(server_port=args.port, quiet=True, inbrowser=True)


if __name__ == "__main__":
    main()
