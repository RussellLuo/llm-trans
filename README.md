# LLM Translate

Your personal Language Translator powered by LLMs.


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