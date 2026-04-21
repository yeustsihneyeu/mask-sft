from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Iterable


def _extract_final_answer(prediction: str) -> str:
    marker = "Output:"
    if marker not in prediction:
        return prediction.strip()

    return prediction.rsplit(marker, maxsplit=1)[-1].strip()


def _format_metric(key: str, value: float | int) -> str:
    if key == "samples":
        return str(value)

    if isinstance(value, float):
        return f"{value:.2f} ({value * 100:.2f}%)"

    return str(value)


def write_baseline_report(
    *,
    model_name: str,
    metrics: dict[str, float | int],
    predictions: Iterable[dict[str, str]],
    output_path: str | Path,
    preview_size: int,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    preview = list(predictions)[:preview_size]
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Report",
        "",
        f"- Generated at: {generated_at}",
        f"- Model: `{model_name}`",
        f"- Test samples: {metrics['samples']}",
        "",
        "## Metrics",
        "",
    ]

    for key, value in metrics.items():
        lines.append(f"- {key}: {_format_metric(key, value)}")

    lines.extend(
        [
            "",
            "## Preview",
            "",
        ]
    )

    if not preview:
        lines.append("No prediction samples were provided.")
    else:
        for index, row in enumerate(preview, start=1):
            raw_prediction = row["prediction"].strip()
            extracted_prediction = _extract_final_answer(raw_prediction)
            lines.extend(
                [
                    f"### Sample {index}",
                    "",
                    "**Source Text (Input)**",
                    "",
                    "```text",
                    row["input"],
                    "```",
                    "",
                    "**Model Raw Output**",
                    "",
                    "```text",
                    raw_prediction,
                    "```",
                    "",
                    "**Extracted Final Answer (Output)**",
                    "",
                    "```text",
                    extracted_prediction,
                    "```",
                    "",
                    "**Reference Masked Text (Target)**",
                    "",
                    "```text",
                    row["target"],
                    "```",
                    "",
                ]
            )

    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output
