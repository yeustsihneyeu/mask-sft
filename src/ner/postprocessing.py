from __future__ import annotations

from src.ner.merge_spans import merge_spans
from src.ner.regex_detector import RegexDetector
from src.ner.span_normalizer import normalize_entity_spans


Entity = dict[str, int | str]


REGEX_FALLBACK_LABELS = {
    "ACCOUNT_NUMBER",
    "AMOUNT",
    "BIC",
    "CREDITCARDCVV",
    "CREDITCARDNUMBER",
    "EMAIL",
    "PHONE_NUMBER",
    "SSN",
}

LABEL_PRIORITY = {
    "EMAIL": 100,
    "SSN": 95,
    "CREDITCARDNUMBER": 90,
    "CREDITCARDCVV": 85,
    "ACCOUNT_NUMBER": 80,
    "BIC": 75,
    "PHONE_NUMBER": 70,
    "AMOUNT": 60,
    "CURRENCYSYMBOL": 55,
    "USERNAME": 50,
    "NAME": 45,
    "FIRSTNAME": 40,
    "LASTNAME": 40,
    "PREFIX": 35,
}


def _has_currency_symbol_entity_at_end(entities: list[Entity], end: int) -> bool:
    return any(
        str(entity["label"]) == "CURRENCYSYMBOL" and int(entity["end"]) == end
        for entity in entities
    )


def _priority(entity: Entity) -> tuple[int, int]:
    label = str(entity["label"])
    start = int(entity["start"])
    end = int(entity["end"])
    return (LABEL_PRIORITY.get(label, 0), end - start)


def _overlaps(left: Entity, right: Entity) -> bool:
    return int(left["start"]) < int(right["end"]) and int(right["start"]) < int(left["end"])


def _same_entity(left: Entity, right: Entity) -> bool:
    return (
        int(left["start"]) == int(right["start"])
        and int(left["end"]) == int(right["end"])
        and str(left["label"]) == str(right["label"])
    )


def add_regex_fallback_entities(
    text: str,
    entities: list[Entity],
    detector: RegexDetector | None = None,
) -> list[Entity]:
    detector = detector or RegexDetector()
    combined = list(entities)

    for regex_entity in detector.detect(text):
        if str(regex_entity["label"]) not in REGEX_FALLBACK_LABELS:
            continue

        if any(_same_entity(existing, regex_entity) for existing in combined):
            continue

        combined.append(regex_entity)

    return combined


def resolve_entity_conflicts(entities: list[Entity]) -> list[Entity]:
    selected: list[Entity] = []

    for entity in sorted(
        entities,
        key=lambda item: (
            -_priority(item)[0],
            -_priority(item)[1],
            int(item["start"]),
            int(item["end"]),
            str(item["label"]),
        ),
    ):
        if any(_overlaps(entity, existing) for existing in selected):
            continue
        selected.append(entity)

    return sorted(selected, key=lambda item: (int(item["start"]), int(item["end"]), str(item["label"])))


def absorb_leading_currency_symbols(text: str, entities: list[Entity]) -> list[Entity]:
    adjusted: list[Entity] = []

    for entity in entities:
        start = int(entity["start"])
        end = int(entity["end"])
        label = str(entity["label"])

        if (
            label == "AMOUNT"
            and start > 0
            and text[start - 1] in "$€£₹¥﷼"
            and not _has_currency_symbol_entity_at_end(entities, start)
        ):
            adjusted.append({"start": start - 1, "end": end, "label": label})
            continue

        adjusted.append(entity)

    return adjusted


def postprocess_entities(
    text: str,
    entities: list[Entity],
    detector: RegexDetector | None = None,
) -> list[Entity]:
    processed = merge_spans(entities)
    processed = normalize_entity_spans(text, processed)
    processed = add_regex_fallback_entities(text, processed, detector=detector)
    processed = normalize_entity_spans(text, processed)
    processed = resolve_entity_conflicts(processed)
    processed = absorb_leading_currency_symbols(text, processed)
    processed = merge_spans(processed)
    return processed
