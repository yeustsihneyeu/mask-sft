from dataclasses import dataclass
from typing import Literal

from transformers import AutoTokenizer

from src.llm.prompt import system_prompt


@dataclass(slots=True)
class PreprocessResult():
    input_token_ids: list[int]
    labels: list[int]
    attention_mask: list[Literal[0,1]]

    def to_dict(self) -> dict[str, list[int]]:
        return {
            "input_ids": self.input_token_ids,
            "labels": self.labels,
            "attention_mask": self.attention_mask,
        }


@dataclass(slots=True)
class Processor():
    tokenizer: AutoTokenizer
    max_val: int = 256

    def preprocess(self, example) -> dict:
        prompt_messages = [
            {"role": "system", "content": system_prompt.render()},
            {"role": "user", "content": example["input"]},
        ]

        prompt_text = self.tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        target_text = example["target"] + self.tokenizer.eos_token

        prompt_token_ids = self.tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        target_token_ids = self.tokenizer(target_text, add_special_tokens=False)["input_ids"]

        available_prompt_length = self.max_val - len(target_token_ids)
        input_token_ids = prompt_token_ids[:available_prompt_length] + target_token_ids
        labels = [-100] * len(prompt_token_ids[:available_prompt_length]) + target_token_ids
        attention_mask = [1] * len(input_token_ids)

        pad_len = self.max_val - len(input_token_ids)
        input_token_ids += pad_len * [self.tokenizer.pad_token_id]
        labels += pad_len * [-100]
        attention_mask += pad_len * [0]

        return PreprocessResult(
            input_token_ids=input_token_ids,
            labels=labels,
            attention_mask=attention_mask
        ).to_dict()
