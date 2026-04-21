from collections.abc import Mapping


class Prompt:
    def __init__(self, version: str, variables: dict[str, str], prompt_text: str):
        self.version = version
        self.variables = variables
        self.prompt_text = prompt_text

    def render(
        self,
        variables: Mapping[str, str] | None = None,
        **kwargs: str,
    ) -> str:
        values = {**self.variables, **(dict(variables) if variables else {}), **kwargs}
        return self.prompt_text.format(**values).strip()


system_prompt = Prompt(
    version="1",
    variables={},
    prompt_text="""
You mask personal information in text.
Keep all non-sensitive text unchanged.
Do not paraphrase.
Return only the masked text.
"""
)
