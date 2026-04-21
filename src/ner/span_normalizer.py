from __future__ import annotations

import re


Entity = dict[str, int | str]


EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d(). \-]{6,}\d|\(\d{3}\)\s*\d{3}-\d{4})")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b\d{13,19}\b")
CVV_PATTERN = re.compile(r"\b\d{3,4}\b")
AMOUNT_PATTERN = re.compile(r"\b\d+(?:,\d{3})*(?:\.\d{2})?\b")
PREFIX_PATTERN = re.compile(r"\b(?:Mr|Mrs|Ms|Miss|Dr)\.?(?=\s|$)")
BIC_PATTERN = re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b")
USERNAME_PATTERN = re.compile(r"\b[a-zA-Z0-9]+(?:[._-][a-zA-Z0-9]+)*\b")
TITLE_TOKEN_PATTERN = re.compile(r"\b[A-Z][A-Za-z]+(?:[-'][A-Za-z]+)*\b")
PREFIX_WITH_SURNAME_PATTERN = re.compile(
    r"\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+[A-Z][A-Za-z]+(?:[-'][A-Za-z]+)*(?=[,\s]|$)"
)


def _to_entity(start: int, end: int, label: str) -> Entity:
    return {
        "start": start,
        "end": end,
        "label": label,
    }


def _overlap_size(start: int, end: int, match_start: int, match_end: int) -> int:
    return max(0, min(end, match_end) - max(start, match_start))


def _best_overlapping_match(pattern: re.Pattern[str], text: str, entity: Entity) -> tuple[int, int] | None:
    start = int(entity["start"])
    end = int(entity["end"])

    best: tuple[int, int] | None = None
    best_score = 0

    for match in pattern.finditer(text):
        match_start, match_end = match.span()
        score = _overlap_size(start, end, match_start, match_end)

        if score == 0:
            continue

        if score > best_score:
            best = (match_start, match_end)
            best_score = score
            continue

        if score == best_score and best is not None:
            current_len = match_end - match_start
            best_len = best[1] - best[0]
            if current_len > best_len:
                best = (match_start, match_end)

    return best


def _best_nearby_match(
    pattern: re.Pattern[str],
    text: str,
    entity: Entity,
    max_distance: int = 4,
) -> tuple[int, int] | None:
    start = int(entity["start"])
    end = int(entity["end"])

    best: tuple[int, int] | None = None
    best_distance: int | None = None

    for match in pattern.finditer(text):
        match_start, match_end = match.span()

        if match_end < start:
            distance = start - match_end
        elif match_start > end:
            distance = match_start - end
        else:
            distance = 0

        if distance > max_distance:
            continue

        if best is None or distance < best_distance:
            best = (match_start, match_end)
            best_distance = distance

    return best


def _expand_digit_run(text: str, start: int, end: int) -> tuple[int, int]:
    left = start
    right = end

    while left > 0 and text[left - 1].isdigit():
        left -= 1

    while right < len(text) and text[right].isdigit():
        right += 1

    return left, right


def _find_pattern_spans(pattern: re.Pattern[str], text: str) -> list[tuple[int, int]]:
    return [match.span() for match in pattern.finditer(text)]


def _find_best_token_span(
    text: str,
    entity: Entity,
    pattern: re.Pattern[str],
    max_distance: int = 4,
) -> tuple[int, int] | None:
    start = int(entity["start"])
    end = int(entity["end"])
    spans = _find_pattern_spans(pattern, text)

    overlapping = [
        (match_start, match_end)
        for match_start, match_end in spans
        if _overlap_size(start, end, match_start, match_end) > 0
    ]
    if overlapping:
        return max(
            overlapping,
            key=lambda span: (
                _overlap_size(start, end, span[0], span[1]),
                span[1] - span[0],
            ),
        )

    best: tuple[int, int] | None = None
    best_distance: int | None = None
    for match_start, match_end in spans:
        if match_end < start:
            distance = start - match_end
        else:
            distance = match_start - end

        if distance < 0 or distance > max_distance:
            continue

        if best is None or distance < best_distance:
            best = (match_start, match_end)
            best_distance = distance

    return best


def _normalize_with_token_pattern(
    text: str,
    entity: Entity,
    pattern: re.Pattern[str],
    max_distance: int = 4,
) -> Entity:
    match_span = _find_best_token_span(text, entity, pattern, max_distance=max_distance)
    if match_span is None:
        return entity

    return _to_entity(match_span[0], match_span[1], str(entity["label"]))


def _spans_are_adjacent_words(text: str, left_end: int, right_start: int) -> bool:
    gap = text[left_end:right_start]
    return bool(gap) and gap.isspace()


def _best_title_token_index(
    text: str,
    entity: Entity,
    tokens: list[tuple[int, int]],
    max_distance: int = 4,
) -> int | None:
    start = int(entity["start"])
    end = int(entity["end"])

    overlapping_indices = [
        index
        for index, (token_start, token_end) in enumerate(tokens)
        if _overlap_size(start, end, token_start, token_end) > 0
    ]
    if overlapping_indices:
        return max(
            overlapping_indices,
            key=lambda index: (
                _overlap_size(start, end, tokens[index][0], tokens[index][1]),
                tokens[index][1] - tokens[index][0],
            ),
        )

    best_index: int | None = None
    best_distance: int | None = None
    for index, (token_start, token_end) in enumerate(tokens):
        if token_end < start:
            distance = start - token_end
        else:
            distance = token_start - end

        if distance < 0 or distance > max_distance:
            continue

        if best_index is None or distance < best_distance:
            best_index = index
            best_distance = distance

    return best_index


def _normalize_name_like_phrase(text: str, entity: Entity) -> Entity:
    tokens = _find_pattern_spans(TITLE_TOKEN_PATTERN, text)
    if not tokens:
        return entity

    index = _best_title_token_index(text, entity, tokens, max_distance=3)
    if index is None:
        return entity

    first = index
    last = index

    start = int(entity["start"])
    end = int(entity["end"])
    overlapping_indices = [
        token_index
        for token_index, (token_start, token_end) in enumerate(tokens)
        if _overlap_size(start, end, token_start, token_end) > 0
    ]
    if overlapping_indices:
        first = min(overlapping_indices)
        last = max(overlapping_indices)

    if last + 1 < len(tokens) and _spans_are_adjacent_words(text, tokens[last][1], tokens[last + 1][0]):
        last += 1
    elif first - 1 >= 0 and _spans_are_adjacent_words(text, tokens[first - 1][1], tokens[first][0]):
        first -= 1

    return _to_entity(tokens[first][0], tokens[last][1], str(entity["label"]))


def _normalize_account_name(text: str, entity: Entity) -> Entity:
    tokens = _find_pattern_spans(TITLE_TOKEN_PATTERN, text)
    if not tokens:
        return entity

    index = _best_title_token_index(text, entity, tokens, max_distance=3)
    if index is None:
        return entity

    first = index
    last = index
    while first - 1 >= 0 and _spans_are_adjacent_words(text, tokens[first - 1][1], tokens[first][0]):
        first -= 1
    while last + 1 < len(tokens) and _spans_are_adjacent_words(text, tokens[last][1], tokens[last + 1][0]):
        last += 1

    return _to_entity(tokens[first][0], tokens[last][1], str(entity["label"]))


def _normalize_prefix(text: str, entity: Entity) -> Entity:
    match_span = _best_overlapping_match(PREFIX_PATTERN, text, entity)
    if match_span is None:
        match_span = _best_nearby_match(PREFIX_PATTERN, text, entity, max_distance=4)
    if match_span is None:
        return entity

    start, end = match_span

    full_match = PREFIX_WITH_SURNAME_PATTERN.match(text[start:])
    if full_match is not None:
        end = start + full_match.end()

    return _to_entity(start, end, str(entity["label"]))


def _normalize_phone_number(text: str, entity: Entity) -> Entity:
    match_span = _best_overlapping_match(PHONE_PATTERN, text, entity)
    if match_span is None:
        return entity

    start, end = match_span

    while start < end and text[start].isspace():
        start += 1

    while end > start and text[end - 1].isspace():
        end -= 1

    if start > 0 and text[start - 1] == "(" and ")" in text[start:end]:
        start -= 1

    return _to_entity(start, end, str(entity["label"]))


def _normalize_account_like_number(text: str, entity: Entity) -> Entity:
    start = int(entity["start"])
    end = int(entity["end"])
    left, right = _expand_digit_run(text, start, end)
    return _to_entity(left, right, str(entity["label"]))


def _normalize_amount(text: str, entity: Entity) -> Entity:
    start = int(entity["start"])
    end = int(entity["end"])
    left = start
    right = end

    while left < len(text) and not text[left].isdigit() and left < right:
        left += 1

    while right > 0 and not text[right - 1].isdigit() and right > left:
        right -= 1

    while left > 0 and text[left - 1] in "0123456789,.":
        left -= 1

    while right < len(text) and text[right] in "0123456789,.":
        right += 1

    if left < right and any(char.isdigit() for char in text[left:right]):
        return _to_entity(left, right, str(entity["label"]))

    match_span = _best_overlapping_match(AMOUNT_PATTERN, text, entity)
    if match_span is None:
        match_span = _best_nearby_match(AMOUNT_PATTERN, text, entity, max_distance=4)
    if match_span is not None:
        return _to_entity(match_span[0], match_span[1], str(entity["label"]))

    return entity


def _normalize_bic(text: str, entity: Entity) -> Entity:
    match_span = _best_overlapping_match(BIC_PATTERN, text, entity)
    if match_span is None:
        match_span = _best_nearby_match(BIC_PATTERN, text, entity, max_distance=4)
    if match_span is None:
        return entity

    return _to_entity(match_span[0], match_span[1], str(entity["label"]))


def _normalize_with_pattern(text: str, entity: Entity, pattern: re.Pattern[str]) -> Entity:
    match_span = _best_overlapping_match(pattern, text, entity)
    if match_span is None:
        return entity

    return _to_entity(match_span[0], match_span[1], str(entity["label"]))


def normalize_entity_span(text: str, entity: Entity) -> Entity:
    label = str(entity["label"])

    if label == "EMAIL":
        return _normalize_with_pattern(text, entity, EMAIL_PATTERN)

    if label == "PHONE_NUMBER":
        return _normalize_phone_number(text, entity)

    if label in {"ACCOUNT_NUMBER", "CREDITCARDNUMBER"}:
        return _normalize_account_like_number(text, entity)

    if label == "SSN":
        return _normalize_with_pattern(text, entity, SSN_PATTERN)

    if label == "CREDITCARDCVV":
        return _normalize_with_pattern(text, entity, CVV_PATTERN)

    if label == "AMOUNT":
        return _normalize_amount(text, entity)

    if label == "PREFIX":
        return _normalize_prefix(text, entity)

    if label == "BIC":
        return _normalize_bic(text, entity)

    if label == "USERNAME":
        return _normalize_with_token_pattern(text, entity, USERNAME_PATTERN, max_distance=3)

    if label in {"FIRSTNAME", "LASTNAME"}:
        return _normalize_with_token_pattern(text, entity, TITLE_TOKEN_PATTERN, max_distance=2)

    if label == "NAME":
        return _normalize_name_like_phrase(text, entity)

    if label == "ACCOUNTNAME":
        return _normalize_account_name(text, entity)

    return _to_entity(int(entity["start"]), int(entity["end"]), label)


def normalize_entity_spans(text: str, entities: list[Entity]) -> list[Entity]:
    return [normalize_entity_span(text, entity) for entity in entities]
