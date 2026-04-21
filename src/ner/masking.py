from __future__ import annotations

Entity = dict[str, int | str]


def labels_to_entities(labels: list[str], offsets: list[tuple[int, int]]) -> list[Entity]:
    entities: list[Entity] = []
    current: Entity | None = None

    for label, (start, end) in zip(labels, offsets):
        if start == end == 0:
            continue

        if label == "O":
            if current is not None:
                entities.append(current)
                current = None
            continue

        prefix, entity_label = label.split("-", 1)

        if prefix == "B":
            if current is not None:
                entities.append(current)
            current = {"start": start, "end": end, "label": entity_label}
            continue

        if current is None or current["label"] != entity_label:
            if current is not None:
                entities.append(current)
            current = {"start": start, "end": end, "label": entity_label}
            continue

        current["end"] = end

    if current is not None:
        entities.append(current)

    return entities


def apply_masking(text: str, entities: list[Entity]) -> str:
    masked_text = text

    for entity in sorted(entities, key=lambda item: int(item["start"]), reverse=True):
        start = int(entity["start"])
        end = int(entity["end"])
        label = str(entity["label"])
        masked_text = masked_text[:start] + f"[{label}]" + masked_text[end:]

    return masked_text
