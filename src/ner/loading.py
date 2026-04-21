import json
from dataclasses import dataclass
from pathlib import Path

from datasets import Dataset


@dataclass(slots=True)
class Loader:
    path: Path
    test_k: float = 0.2
    seed: int = 42

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    def _resolve_path(self) -> Path:
        if self.path.is_dir() or str(self.path) in {"", "."}:
            return self.path / "data" / "entities.json"
        return self.path

    def load(self) -> Dataset:
        path = self._resolve_path()
        rows = json.loads(path.read_text(encoding="utf-8"))
        return Dataset.from_list(rows)

    def train_test_split(self, dataset: Dataset | None = None):
        dataset = dataset if dataset is not None else self.load()
        split = dataset.train_test_split(test_size=self.test_k, seed=self.seed)
        return split["train"], split["test"]

    def load_test_dataset(self) -> Dataset:
        _, test_dataset = self.train_test_split()
        return test_dataset
