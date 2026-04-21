from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import re
from typing import Iterable


MASK_PATTERN = re.compile(r"\[[^\[\]]+\]")


@dataclass(slots=True)
class Evaluator:
    predictions: list[str]
    references: list[str]
    sample_ids: list[str] | None = None
    _validated: bool = field(init=False, repr=False, default=False)

    def __post_init__(self) -> None:
        self.predictions = [self._normalize_text(text) for text in self.predictions]
        self.references = [self._normalize_text(text) for text in self.references]

        if len(self.predictions) != len(self.references):
            raise ValueError("predictions and references must have the same length")

        if self.sample_ids is not None and len(self.sample_ids) != len(self.references):
            raise ValueError("sample_ids must have the same length as references")

        self._validated = True

    @classmethod
    def from_records(
        cls,
        records: Iterable[dict],
        prediction_key: str = "prediction",
        reference_key: str = "masked_text",
        sample_id_key: str | None = None,
    ) -> "Evaluator":
        predictions: list[str] = []
        references: list[str] = []
        sample_ids: list[str] | None = [] if sample_id_key else None

        for index, record in enumerate(records):
            if prediction_key not in record:
                raise KeyError(f"Missing '{prediction_key}' in record at index {index}")
            if reference_key not in record:
                raise KeyError(f"Missing '{reference_key}' in record at index {index}")

            predictions.append(record[prediction_key])
            references.append(record[reference_key])

            if sample_ids is not None:
                sample_ids.append(str(record.get(sample_id_key, index)))

        return cls(predictions=predictions, references=references, sample_ids=sample_ids)

    def _normalize_text(self, text: str | None) -> str:
        return "" if text is None else str(text).strip()

    def _extract_masks(self, text: str) -> list[str]:
        return MASK_PATTERN.findall(text)

    def _remove_masks(self, text: str) -> str:
        without_masks = MASK_PATTERN.sub("", text)
        return " ".join(without_masks.split())

    def _text_preservation(self) -> float:
        scores: list[float] = []

        for prediction, reference in zip(self.predictions, self.references):
            prediction_text = self._remove_masks(prediction)
            reference_text = self._remove_masks(reference)

            if not prediction_text and not reference_text:
                scores.append(1.0)
                continue

            scores.append(SequenceMatcher(None, prediction_text, reference_text).ratio())

        return sum(scores) / len(scores) if scores else 0.0

    def _over_masking(self) -> float:
        extra_mask_count = 0
        predicted_mask_count = 0

        for prediction, reference in zip(self.predictions, self.references):
            predicted_masks = Counter(self._extract_masks(prediction))
            reference_masks = Counter(self._extract_masks(reference))

            predicted_mask_count += sum(predicted_masks.values())
            extra_mask_count += sum((predicted_masks - reference_masks).values())

        if predicted_mask_count == 0:
            return 0.0

        return extra_mask_count / predicted_mask_count

    def _masking_recall(self) -> float:
        matched_mask_count = 0
        reference_mask_count = 0

        for prediction, reference in zip(self.predictions, self.references):
            predicted_masks = Counter(self._extract_masks(prediction))
            reference_masks = Counter(self._extract_masks(reference))

            reference_mask_count += sum(reference_masks.values())
            matched_mask_count += sum((predicted_masks & reference_masks).values())

        if reference_mask_count == 0:
            return 1.0

        return matched_mask_count / reference_mask_count

    def _exact_match(self) -> float:
        if not self.references:
            return 0.0

        exact_matches = sum(
            prediction == reference
            for prediction, reference in zip(self.predictions, self.references)
        )
        return exact_matches / len(self.references)

    def evaluate(self) -> dict[str, float | int]:
        if not self._validated:
            raise RuntimeError("Evaluator is not initialized correctly")

        return {
            "samples": len(self.references),
            "exact_match": self._exact_match(),
            "masking_recall": self._masking_recall(),
            "over_masking_rate": self._over_masking(),
            "text_preservation": self._text_preservation(),
        }
