from dataclasses import dataclass
from pathlib import Path

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class Model:
    name: str

    def _resolve_local_model_path(self) -> str | Path:
        if Path(self.name).exists():
            return self.name

        cache_root = Path.home() / ".cache" / "huggingface" / "hub"
        repo_dir = cache_root / f"models--{self.name.replace('/', '--')}"
        ref_path = repo_dir / "refs" / "main"

        if ref_path.exists():
            snapshot_id = ref_path.read_text(encoding="utf-8").strip()
            snapshot_path = repo_dir / "snapshots" / snapshot_id
            if snapshot_path.exists():
                return snapshot_path

        return self.name

    def __post_init__(self):
        model_path = self._resolve_local_model_path()
        local_only = Path(model_path).exists()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=local_only)
        self._model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=local_only)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value) -> None:
        self._model = value

    def generate(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=128)
        prompt_length = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][prompt_length:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    def tokenize(self, text: str):
        return self.tokenizer(text, return_tensors="pt")

    def peft_model(self, adapter_path: str):
        return PeftModel.from_pretrained(self.model, adapter_path)
