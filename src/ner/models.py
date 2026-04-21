from dataclasses import dataclass
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForTokenClassification, AutoTokenizer

from src.ner.processing import id2label as default_id2label
from src.ner.processing import label2id as default_label2id
from src.ner.processing import label_list as default_label_list


@dataclass
class Model:
    name: str
    label_list: list | None = None
    id2label: dict | None = None
    label2id: dict | None = None

    def _resolve_local_snapshot_path(self) -> str | Path:
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

    def _has_model_weights(self, path: str | Path) -> bool:
        path = Path(path)
        weight_files = (
            "model.safetensors",
            "pytorch_model.bin",
            "tf_model.h5",
            "flax_model.msgpack",
        )
        return any((path / filename).exists() for filename in weight_files)

    def __post_init__(self):
        if self.label_list is None:
            self.label_list = default_label_list
        if self.id2label is None:
            self.id2label = default_id2label
        if self.label2id is None:
            self.label2id = default_label2id

        self.snapshot_path = self._resolve_local_snapshot_path()
        self.tokenizer_path = self.snapshot_path
        self.model_path = self.snapshot_path if self._has_model_weights(self.snapshot_path) else self.name
        self.tokenizer_local_only = Path(self.tokenizer_path).exists()
        self.model_local_only = Path(self.model_path).exists()
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_path,
            local_files_only=self.tokenizer_local_only,
        )
        self._model = None

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value) -> None:
        self._model = value

    @property
    def config(self):
        return self.model.config

    def get_tokenizer(self):
        return self.tokenizer

    def get_model(self):
        if self._model is None:
            self.model = AutoModelForTokenClassification.from_pretrained(
                self.model_path,
                local_files_only=self.model_local_only,
                num_labels=len(self.label_list),
                id2label=self.id2label,
                label2id=self.label2id,
            )
        return self._model

    def tokenize(self, text: str, with_offsets: bool = False):
        return self.tokenizer(
            text,
            truncation=True,
            max_length=512,
            return_offsets_mapping=with_offsets,
            return_tensors="pt",
        )

    def peft_model(self, adapter_path: str):
        if self.model is None:
            self.get_model()
        return PeftModel.from_pretrained(self.model, adapter_path)

    def predict(self, text: str) -> dict[str, object]:
        if self.model is None:
            self.get_model()

        encoding = self.tokenize(text, with_offsets=True)
        offsets = [tuple(offset) for offset in encoding.pop("offset_mapping")[0].tolist()]

        self.model.eval()
        with torch.no_grad():
            logits = self.model(**encoding).logits

        predicted_ids = logits.argmax(dim=-1)[0].tolist()
        predicted_labels = [
            self.config.id2label[int(label_id)]
            for label_id in predicted_ids
        ]

        return {
            "text": text,
            "label_ids": predicted_ids,
            "labels": predicted_labels,
            "offsets": offsets,
        }
