# mask_sft

Small supervised fine-tuning project for masking sensitive information in financial-support style text.

The project compares three approaches on the same task:

- baseline zero-shot prompting
- few-shot prompting
- LoRA fine-tuning of `Qwen/Qwen2.5-1.5B-Instruct`

The goal is to transform raw text with personal or financial details into the same text with sensitive spans replaced by placeholder tags such as `[EMAIL]`, `[ACCOUNT_NUMBER]`, or `[PHONE_NUMBER]`.

## Project Layout

- `src/` - reusable code grouped into general modules plus `llm/` and `ner/` packages
- `data/data.json` - dataset with `unmasked_text` and `masked_text`
- `notebooks/` - step-by-step experiments for baseline, few-shot, preprocessing, training, and final evaluation
- `reports/` - generated markdown reports with metrics and prediction previews
- `model/` - saved LoRA adapter and tokenizer files

## Environment

Install the current dependencies:

```bash
pip install -r requirements.txt
```

Current `requirements.txt` includes:

- `transformers`
- `datasets`
- `peft`
- `torch`
- `mlx_lm`
- `pandas`
- `numpy`
- `ipykernel`

## Workflow

The repository is currently organized around notebooks plus reusable modules in `src/`.

Suggested order:

1. `notebooks/01_baseline.ipynb` - run a baseline zero-shot evaluation
2. `notebooks/02_few_shot.ipynb` - evaluate a few-shot prompting setup
3. `notebooks/03_preprocessing.ipynb` - inspect tokenization and training examples
4. `notebooks/04_training.ipynb` - fine-tune the base model with LoRA
5. `notebooks/05_fine_tuned_eval.ipynb` - evaluate the fine-tuned adapter and compare results

## Core Modules

- `src/llm/loading.py` - loads the dataset and creates a train/test split
- `src/llm/models.py` - loads the base model and tokenizer
- `src/llm/prompt.py` - defines the system prompt and prompt template helper
- `src/llm/processing.py` - builds chat-formatted training examples and labels
- `src/llm/training.py` - configures and runs LoRA fine-tuning with `Trainer`
- `src/llm/inference.py` - wraps prompt building and generation for inference
- `src/evaluating.py` - computes task-specific metrics
- `src/reporting.py` - writes markdown reports with metrics and prediction previews

## Dataset

The dataset contains `50` records in `data/data.json`, with `49` currently usable rows after filtering out empty `unmasked_text` values.

Each row contains:

- `unmasked_text` - original text with sensitive values present
- `masked_text` - target text with placeholder labels replacing sensitive spans

## Metrics

Evaluation in `src/evaluating.py` reports:

- `exact_match`
- `masking_recall`
- `over_masking_rate`
- `text_preservation`

This is useful for the task because plain exact match alone does not show whether the model preserved the original wording while masking the right spans.

## Current Results

Based on the generated reports in `reports/` for a 10-sample test slice:

| Approach | Exact Match | Masking Recall | Over-Masking Rate | Text Preservation |
|---|---:|---:|---:|---:|
| Baseline | 0.00 | 0.00 | 0.00 | 0.83 |
| Few-shot | 0.30 | 0.62 | 0.30 | 0.98 |
| Fine-tuned | 0.70 | 0.91 | 0.11 | 1.00 |

The fine-tuned model is the strongest variant in the current comparison and is the default candidate for further iteration.

## Notes

- Reports are available in `reports/01_baseline.md`, `reports/02_few_shot.md`, `reports/05_fine_tuned.md`, and `reports/06_final_comparison.md`.
- The saved adapter is stored in `model/`.
- The project currently favors notebook-driven experimentation over a packaged CLI workflow.
