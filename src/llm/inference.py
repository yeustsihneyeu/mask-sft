from dataclasses import dataclass

from src.llm.models import Model
from src.llm.prompt import system_prompt


@dataclass(slots=True)
class InferenceRunner:
    model: Model

    def build_prompt(self, text: str) -> str:
        prompt_messages = [
            {"role": "system", "content": system_prompt.render()},
            {"role": "user", "content": text},
        ]
        return self.model.tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def predict(self, text: str) -> str:
        prompt = self.build_prompt(text)
        return self.model.generate(prompt)
