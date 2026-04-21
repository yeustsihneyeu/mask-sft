# mask_sft

Project for masking sensitive information in financial-support style text.

The task is to transform raw text with personal or financial details into the same text with sensitive spans replaced by placeholder tags such as `[EMAIL]`, `[ACCOUNT_NUMBER]`, `[PHONE_NUMBER]`, or `[SSN]`.

The repository compares two families of approaches on the same task:

- LLM-based masking
  - zero-shot prompting
  - few-shot prompting
  - LoRA fine-tuning of `Qwen/Qwen2.5-1.5B-Instruct`
- NER-based masking
  - regex baseline
  - fine-tuned token classification with `microsoft/deberta-v3-base`
  - post-processing and full masking pipeline on top of NER predictions

The current strongest result comes from the full NER pipeline:

`fine-tuned NER model` + `span normalization` + `regex fallback` + `overlap resolution` + `deterministic masking`

## Project Layout

- `src/` - reusable code grouped into general modules plus `llm/` and `ner/` packages
- `data/data.json` - dataset with `unmasked_text` and `masked_text`
- `data/entities.json` - NER-style dataset with raw text and entity spans
- `notebooks/` - step-by-step experiments for LLM and NER workflows
- `reports/` - generated markdown reports with metrics and prediction previews
- `model/` - saved LoRA adapter and tokenizer files for the LLM track
- `ner_model/` - saved LoRA adapter and tokenizer files for the NER track

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

## High-Level Pipelines

### LLM Pipeline

1. Load `unmasked_text` / `masked_text` pairs from `data/data.json`
2. Build prompting or supervised fine-tuning examples
3. Run baseline, few-shot, or LoRA fine-tuned generation
4. Evaluate final masked text with task-level metrics

### NER Pipeline

1. Load raw text and span annotations from `data/entities.json`
2. Tokenize text and align entity spans to BIO labels
3. Fine-tune `microsoft/deberta-v3-base` for token classification
4. Convert predicted BIO labels back into entity spans
5. Apply post-processing:
   - merge adjacent spans
   - normalize entity boundaries
   - add regex fallback entities
   - resolve span conflicts
6. Replace spans with placeholder tags
7. Evaluate final masked text with the same task-level metrics

## Notebook Workflow

The repository is organized around notebooks plus reusable modules in `src/`.

### LLM Track

1. `notebooks/01_llm_baseline.ipynb` - zero-shot evaluation
2. `notebooks/02_llm_few_shot.ipynb` - few-shot evaluation
3. `notebooks/03_llm_preprocessing.ipynb` - training example preparation
4. `notebooks/04_llm_training.ipynb` - LoRA fine-tuning
5. `notebooks/05_llm_fine_tuned_eval.ipynb` - evaluation of the fine-tuned LLM

### NER Track

1. `notebooks/06_ner_preprocessing.ipynb` - tokenization and BIO alignment
2. `notebooks/07_ner_training.ipynb` - NER fine-tuning
3. `notebooks/08_ner_regex_baseline.ipynb` - regex-only baseline
4. `notebooks/09_ner_eval.ipynb` - raw NER evaluation
5. `notebooks/10_ner_postprocessing_eval.ipynb` - NER with boundary normalization
6. `notebooks/11_ner_full_pipeline_eval.ipynb` - full NER pipeline with all post-processing techniques

## Core Modules

- `src/llm/loading.py` - loads the dataset and creates a train/test split
- `src/llm/models.py` - loads the base model and tokenizer
- `src/llm/prompt.py` - defines the system prompt and prompt template helper
- `src/llm/processing.py` - builds chat-formatted training examples and labels
- `src/llm/training.py` - configures and runs LoRA fine-tuning with `Trainer`
- `src/llm/inference.py` - wraps prompt building and generation for inference
- `src/ner/loading.py` - loads the NER dataset and creates splits
- `src/ner/processing.py` - defines entity taxonomy and BIO preprocessing
- `src/ner/models.py` - loads the token classification model and tokenizer
- `src/ner/training.py` - configures and runs LoRA fine-tuning for NER
- `src/ner/masking.py` - converts BIO predictions into entity spans and applies masking
- `src/ner/merge_spans.py` - merges adjacent or overlapping spans with the same label
- `src/ner/span_normalizer.py` - normalizes entity boundaries using rule-based logic
- `src/ner/regex_detector.py` - finds high-precision entities with regex rules
- `src/ner/postprocessing.py` - combines normalization, regex fallback, and overlap resolution
- `src/evaluating.py` - computes task-specific metrics
- `src/reporting.py` - writes markdown reports with metrics and prediction previews

## Dataset

The project uses two synchronized views of the same problem:

- `data/data.json` for full masked-text generation and evaluation
- `data/entities.json` for NER training with character-level entity spans

`data/data.json` contains `50` records, with `49` currently usable rows after filtering out empty `unmasked_text` values.

LLM-style rows contain:

- `unmasked_text` - original text with sensitive values present
- `masked_text` - target text with placeholder labels replacing sensitive spans

NER-style rows contain:

- `text` - original unmasked text
- `entities` - list of annotated spans with `start`, `end`, and `label`

## Metrics

Evaluation in `src/evaluating.py` reports:

- `exact_match`
- `masking_recall`
- `over_masking_rate`
- `text_preservation`

These metrics are used for both LLM and NER outputs, which makes the comparison fair at the final masked-text level.

## Current Results

Based on the generated reports in `reports/` for the current 10-sample evaluation slice:

| Technique | Family | Exact Match | Masking Recall | Over-Masking Rate | Text Preservation |
|---|---|---:|---:|---:|---:|
| `01_llm_baseline` | LLM zero-shot | 0.00 | 0.00 | 0.00 | 0.79 |
| `02_llm_few_shot` | LLM few-shot | 0.20 | 0.59 | 0.35 | 0.99 |
| `05_llm_fine_tuned` | LLM fine-tuned | 0.70 | 0.82 | 0.15 | 1.00 |
| `08_ner_regex_baseline` | Regex | 0.20 | 0.50 | 0.11 | 0.92 |
| `09_ner_eval` | NER model only | 0.00 | 0.97 | 0.03 | 0.93 |
| `10_ner_postprocessing_eval` | NER + post-processing | 0.70 | 0.97 | 0.00 | 1.00 |
| `11_ner_full_pipeline_eval` | NER + full pipeline | 1.00 | 1.00 | 0.00 | 1.00 |

## What Changed Across NER Iterations

The NER track improved in layers:

1. `Regex baseline` provided a deterministic but incomplete reference point.
2. `Fine-tuned NER` solved the main entity-detection problem and pushed recall high.
3. `NER + post-processing` fixed boundary issues and strongly improved exact output quality.
4. `NER + full pipeline` added regex fallback and conflict resolution, closing the final gap.

The main lesson is that raw model quality alone was not enough. The best result came from combining learned detection with deterministic post-processing.

## Recommended Default

The default recommended approach is the full NER pipeline from `notebooks/11_ner_full_pipeline_eval.ipynb` because it currently provides the strongest combined result on all contours:

- highest `exact_match`
- highest `masking_recall`
- zero `over_masking_rate`
- perfect `text_preservation` on the current evaluation slice

## Notes

- Reports are available in `reports/`, including [12_final_comparative_report.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/12_final_comparative_report.md:1).
- The LLM adapter is stored in `model/`.
- The NER adapter is stored in `ner_model/`.
- The project currently favors notebook-driven experimentation over a packaged CLI workflow.
