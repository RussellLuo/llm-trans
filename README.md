# 🌐 LLM Translate

Your personal Language Translator powered by LLMs.

<p align="center">
<img src="screenshot.png" height="400">
</p>


## Installation

```bash
pip install llm-trans
```


## Quick Start

Copy [settings.yaml](./settings.yaml) to your local directory, and run LLM Translate:

```bash
export OPENAI_API_KEY="your-openai-key"
llm-trans ./settings.yaml
```

> You can also add your own LLM by changing the settings as below:
>
> ```yaml
> llms:
> ...
> - title: Your LLM
>   model: your-model
>   api_base: your-api-base
>   api_version: your-api-version
>   api_key: your-api-key # plain key string, or environment variable: ${YOUR_API_KEY}
> ```


## Why?

LLM Translate is like traditional translation tools (e.g. [Google Translate][1]) but is powered by LLMs:

- LLMs are very good at language translation and are still evolving rapidly.
- Any local or online LLMs are supported.

> [!NOTE]
> **Disclaimer**
>
> LLM Translate is not a production-level project, nor is it intended (or able) to replace existing translation tools such as Google Translate and DeepL.
>
> It's just a little toy built with [Coagent][2], [Gradio][3] and LLM (at your disposal), for those who find LLM translations useful at times, but don't want to repeatedly write system prompts every time.
>
> Besides language translation, LLM Translate offers a UI similar to Google Translate, and it also has the capability of language detection (also based on LLM).
>
> Finally, if you don't want to use LLM for translation, but are interested in developing LLM applications, you can treat it as a small code example (just ~300 lines in total).


[1]: https://translate.google.com/
[2]: https://github.com/OpenCSGs/coagent
[3]: https://www.gradio.app/