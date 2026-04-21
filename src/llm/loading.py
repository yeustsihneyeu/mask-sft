import json
from pathlib import Path
import re

from datasets import Dataset


class Loader:

    def __init__(self, path: Path, test_k: float = 0.2, seed: int = 42):
        self.path = Path(path)
        self.test_k = test_k
        self.seed = seed

    def _resolve_path(self) -> Path:
        if self.path.is_dir() or str(self.path) in {"", "."}:
            return self.path / "data" / "data.json"
        return self.path

    def load(self) -> Dataset:
        path = self._resolve_path()
        raw_text = path.read_text(encoding="utf-8")
        repaired_text = re.sub(r"(\})(\s*\{)", r"\1,\2", raw_text)
        rows = json.loads(repaired_text)

        examples = [
            {
                "input": row["unmasked_text"],
                "target": row["masked_text"],
            }
            for row in rows
            if row.get("unmasked_text")
        ]
        return Dataset.from_list(examples)

    def train_test_split(self, dataset: Dataset | None = None):
        dataset = dataset if dataset is not None else self.load()
        split = dataset.train_test_split(test_size=self.test_k, seed=self.seed)
        return split["train"], split["test"]

    def load_test_dataset(self) -> Dataset:
        _, test_dataset = self.train_test_split()
        return test_dataset
