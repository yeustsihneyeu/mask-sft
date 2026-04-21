from __future__ import annotations

Entity = dict[str, int | str]


def normalize_entities(entities: list[Entity]) -> list[Entity]:
    normalized: list[Entity] = []

    for entity in entities:
        start = int(entity["start"])
        end = int(entity["end"])
        label = str(entity["label"])

        if end <= start:
            continue

        normalized.append(
            {
                "start": start,
                "end": end,
                "label": label,
            }
        )

    return sorted(normalized, key=lambda item: (int(item["start"]), int(item["end"]), str(item["label"])))


def should_merge(left: Entity, right: Entity) -> bool:
    if str(left["label"]) != str(right["label"]):
        return False

    left_end = int(left["end"])
    right_start = int(right["start"])

    return right_start <= left_end


def merge_pair(left: Entity, right: Entity) -> Entity:
    return {
        "start": min(int(left["start"]), int(right["start"])),
        "end": max(int(left["end"]), int(right["end"])),
        "label": str(left["label"]),
    }


def merge_spans(entities: list[Entity]) -> list[Entity]:
    normalized = normalize_entities(entities)

    if not normalized:
        return []

    merged: list[Entity] = [normalized[0]]

    for entity in normalized[1:]:
        current = merged[-1]

        if should_merge(current, entity):
            merged[-1] = merge_pair(current, entity)
            continue

        merged.append(entity)

    return merged
