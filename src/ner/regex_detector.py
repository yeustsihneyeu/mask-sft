from __future__ import annotations

import re
from dataclasses import dataclass, field


Entity = dict[str, int | str]


@dataclass(frozen=True, slots=True)
class RegexRule:
    label: str
    pattern: re.Pattern[str]


@dataclass(slots=True)
class RegexDetector:
    rules: list[RegexRule] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rules:
            self.rules = self.default_rules()

    @staticmethod
    def default_rules() -> list[RegexRule]:
        return [
            RegexRule(
                label="EMAIL",
                pattern=re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b"),
            ),
            RegexRule(
                label="PHONE_NUMBER",
                pattern=re.compile(r"(?:(?<=\s)|^)(?:\+?\d[\d(). \-]{6,}\d)(?=\b)"),
            ),
            RegexRule(
                label="SSN",
                pattern=re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            ),
            RegexRule(
                label="IP",
                pattern=re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            ),
            RegexRule(
                label="MAC",
                pattern=re.compile(r"\b[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}\b"),
            ),
            RegexRule(
                label="IBAN",
                pattern=re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
            ),
            RegexRule(
                label="BIC",
                pattern=re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"),
            ),
            RegexRule(
                label="PHONEIMEI",
                pattern=re.compile(r"\b\d{2}-\d{6}-\d{6}-\d\b"),
            ),
            RegexRule(
                label="CREDITCARDNUMBER",
                pattern=re.compile(r"\b\d{13,19}\b"),
            ),
            RegexRule(
                label="CREDITCARDCVV",
                pattern=re.compile(r"(?:(?<=CVV )|(?<=security code )|(?<=code ))\d{3,4}\b", re.IGNORECASE),
            ),
            RegexRule(
                label="DATE",
                pattern=re.compile(
                    r"\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|[A-Z][a-z]+ \d{1,2}, \d{4})\b"
                ),
            ),
            RegexRule(
                label="CURRENCYCODE",
                pattern=re.compile(r"\b(?:USD|EUR|GBP|JPY|SAR|PLN|CAD|AUD|CHF|NOK|SEK|DKK)\b"),
            ),
            RegexRule(
                label="CURRENCYSYMBOL",
                pattern=re.compile(r"[$€£₹¥﷼]"),
            ),
            RegexRule(
                label="AMOUNT",
                pattern=re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b|\b\d+(?:\.\d{2})\b"),
            ),
            RegexRule(
                label="ACCOUNT_NUMBER",
                pattern=re.compile(r"(?:(?<=account number is )|(?<=account number )|(?<=account ))\d{6,20}\b", re.IGNORECASE),
            ),
            RegexRule(
                label="APPLICATION_NUMBER",
                pattern=re.compile(r"\b(?:APP|CASE|LOAN)-\d{4}-\d{4,6}\b|\b(?:LOAN|CASE)-\d{5}\b"),
            ),
        ]

    def detect(self, text: str) -> list[Entity]:
        matches: list[Entity] = []

        for rule in self.rules:
            for match in rule.pattern.finditer(text):
                matches.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "label": rule.label,
                    }
                )

        return self._deduplicate(matches)

    def _deduplicate(self, entities: list[Entity]) -> list[Entity]:
        # Prefer longer spans first, then earlier spans.
        sorted_entities = sorted(
            entities,
            key=lambda entity: (
                -(int(entity["end"]) - int(entity["start"])),
                int(entity["start"]),
                str(entity["label"]),
            ),
        )

        selected: list[Entity] = []
        for entity in sorted_entities:
            start = int(entity["start"])
            end = int(entity["end"])

            if any(start < int(existing["end"]) and end > int(existing["start"]) for existing in selected):
                continue

            selected.append(entity)

        return sorted(selected, key=lambda entity: (int(entity["start"]), int(entity["end"])))
