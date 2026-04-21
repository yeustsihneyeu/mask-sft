# Final Comparative Report

- Generated at: 2026-04-21
- Scope: comparative summary of all evaluated masking techniques
- Test samples: 10

## Compared Techniques

1. `01_llm_baseline` -> `Qwen/Qwen2.5-1.5B-Instruct`
2. `02_llm_few_shot` -> `Qwen/Qwen2.5-1.5B-Instruct (few-shot)`
3. `05_llm_fine_tuned` -> `Qwen/Qwen2.5-1.5B-Instruct (fine-tuned)`
4. `08_ner_regex_baseline` -> `Regex NER Baseline`
5. `09_ner_eval` -> `microsoft/deberta-v3-base (fine-tuned NER)`
6. `10_ner_postprocessing_eval` -> `microsoft/deberta-v3-base (fine-tuned NER + post-processing)`
7. `11_ner_full_pipeline_eval` -> `microsoft/deberta-v3-base (fine-tuned NER + full post-processing pipeline)`

## Unified Metrics

| Technique | Family | Exact Match | Masking Recall | Over-masking Rate | Text Preservation |
|---|---|---:|---:|---:|---:|
| `01_llm_baseline` | LLM zero-shot | 0.00 | 0.00 | 0.00 | 0.79 |
| `02_llm_few_shot` | LLM few-shot | 0.20 | 0.59 | 0.35 | 0.99 |
| `05_llm_fine_tuned` | LLM fine-tuned | 0.70 | 0.82 | 0.15 | 1.00 |
| `08_ner_regex_baseline` | Regex | 0.20 | 0.50 | 0.11 | 0.92 |
| `09_ner_eval` | NER model only | 0.00 | 0.97 | 0.03 | 0.93 |
| `10_ner_postprocessing_eval` | NER + span post-processing | 0.70 | 0.97 | 0.00 | 1.00 |
| `11_ner_full_pipeline_eval` | NER + full pipeline | 1.00 | 1.00 | 0.00 | 1.00 |

## Comparison By Contour

### 1. Exact Match

`Exact Match` is the most important contour for the final product because it measures whether the produced masked text exactly matches the reference.

| Rank | Technique | Exact Match |
|---|---|---:|
| 1 | `11_ner_full_pipeline_eval` | 1.00 |
| 2 | `05_llm_fine_tuned` | 0.70 |
| 2 | `10_ner_postprocessing_eval` | 0.70 |
| 4 | `02_llm_few_shot` | 0.20 |
| 4 | `08_ner_regex_baseline` | 0.20 |
| 6 | `01_llm_baseline` | 0.00 |
| 6 | `09_ner_eval` | 0.00 |

Interpretation:
- Raw NER without post-processing finds entities well, but does not produce the final text format accurately enough.
- Fine-tuned LLM and NER with basic post-processing reach the same `0.70`, but for different reasons: the LLM is better at direct text rendering, while NER is better at structured detection.
- Full NER pipeline is the only technique that reaches stable exact output on all evaluated samples.

### 2. Masking Recall

`Masking Recall` shows how many required masks were actually produced.

| Rank | Technique | Masking Recall |
|---|---|---:|
| 1 | `11_ner_full_pipeline_eval` | 1.00 |
| 2 | `09_ner_eval` | 0.97 |
| 2 | `10_ner_postprocessing_eval` | 0.97 |
| 4 | `05_llm_fine_tuned` | 0.82 |
| 5 | `02_llm_few_shot` | 0.59 |
| 6 | `08_ner_regex_baseline` | 0.50 |
| 7 | `01_llm_baseline` | 0.00 |

Interpretation:
- NER-based approaches dominate this contour because token classification is structurally better suited for boundary-level PII detection.
- Regex alone is useful but incomplete.
- LLM approaches improve with supervision, but still underperform strong NER on structured recall.

### 3. Over-masking Rate

`Over-masking Rate` shows how often the system masked something extra that should have remained visible. Lower is better.

| Rank | Technique | Over-masking Rate |
|---|---|---:|
| 1 | `01_llm_baseline` | 0.00 |
| 1 | `10_ner_postprocessing_eval` | 0.00 |
| 1 | `11_ner_full_pipeline_eval` | 0.00 |
| 4 | `09_ner_eval` | 0.03 |
| 5 | `08_ner_regex_baseline` | 0.11 |
| 6 | `05_llm_fine_tuned` | 0.15 |
| 7 | `02_llm_few_shot` | 0.35 |

Interpretation:
- `01_llm_baseline` has zero over-masking only because it barely masks anything at all, so this is not a meaningful win.
- The real strong result is the NER pipeline: it reaches near-perfect or perfect recall while keeping over-masking at zero.
- Few-shot prompting is the weakest option on this contour because it produces unstable, loosely controlled masking behavior.

### 4. Text Preservation

`Text Preservation` measures how much non-sensitive text remains unchanged. Higher is better.

| Rank | Technique | Text Preservation |
|---|---|---:|
| 1 | `05_llm_fine_tuned` | 1.00 |
| 1 | `10_ner_postprocessing_eval` | 1.00 |
| 1 | `11_ner_full_pipeline_eval` | 1.00 |
| 4 | `02_llm_few_shot` | 0.99 |
| 5 | `09_ner_eval` | 0.93 |
| 6 | `08_ner_regex_baseline` | 0.92 |
| 7 | `01_llm_baseline` | 0.79 |

Interpretation:
- Fine-tuned LLM and post-processed NER both preserve neutral text very well.
- Raw NER loses preservation because imprecise entity boundaries leave fragments in place or cut spans incorrectly.
- Full NER pipeline fixes that problem while keeping structured detection advantages.

## Evolution Inside Each Family

### LLM Track

| Step | Exact Match | Masking Recall | Over-masking | Text Preservation |
|---|---:|---:|---:|---:|
| Baseline | 0.00 | 0.00 | 0.00 | 0.79 |
| Few-shot | 0.20 | 0.59 | 0.35 | 0.99 |
| Fine-tuned | 0.70 | 0.82 | 0.15 | 1.00 |

Takeaway:
- Prompting alone is not enough for stable masking.
- Fine-tuning helps substantially, especially on exact output rendering.
- Even after fine-tuning, LLM masking still lags behind the best NER pipeline on recall and over-masking control.

### NER Track

| Step | Exact Match | Masking Recall | Over-masking | Text Preservation |
|---|---:|---:|---:|---:|
| Regex baseline | 0.20 | 0.50 | 0.11 | 0.92 |
| Fine-tuned NER | 0.00 | 0.97 | 0.03 | 0.93 |
| NER + post-processing | 0.70 | 0.97 | 0.00 | 1.00 |
| NER + full pipeline | 1.00 | 1.00 | 0.00 | 1.00 |

Takeaway:
- The NER model already solves the hard detection problem.
- The main bottleneck was not entity recall but converting predictions into the exact target masking format.
- Post-processing contributes more than raw model improvements at the final stage.
- Adding regex fallback and conflict resolution closes the remaining gap.

## Overall Ranking

### Best Overall for Production

1. `11_ner_full_pipeline_eval`
2. `10_ner_postprocessing_eval`
3. `05_llm_fine_tuned`
4. `09_ner_eval`
5. `08_ner_regex_baseline`
6. `02_llm_few_shot`
7. `01_llm_baseline`

Rationale:
- `11_ner_full_pipeline_eval` is the strongest on every meaningful contour simultaneously.
- `10_ner_postprocessing_eval` is already production-viable, but still misses edge cases solved by regex fallback and conflict handling.
- `05_llm_fine_tuned` is a strong baseline if a single generative model is preferred, but it is less controllable than the NER pipeline.

## Final Conclusion

The comparative result is unambiguous: the best masking quality is achieved not by prompt-based generation and not by raw NER alone, but by a layered NER pipeline.

The decisive pattern across all contours is:
- model-only NER solves detection
- post-processing solves formatting and boundary cleanup
- regex fallback closes deterministic gaps
- conflict resolution removes masking artifacts

In other words, the winning strategy is not a single technique but a composition:

`fine-tuned NER model` + `span normalization` + `regex fallback` + `overlap resolution` + `deterministic masking`

## Source Reports

- [01_llm_baseline.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/01_llm_baseline.md:1)
- [02_llm_few_shot.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/02_llm_few_shot.md:1)
- [05_llm_fine_tuned.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/05_llm_fine_tuned.md:1)
- [08_ner_regex_baseline.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/08_ner_regex_baseline.md:1)
- [09_ner_eval.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/09_ner_eval.md:1)
- [10_ner_postprocessing_eval.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/10_ner_postprocessing_eval.md:1)
- [11_ner_full_pipeline_eval.md](/Users/ayeustsihneyeu/PythonProjects/mask_sft/reports/11_ner_full_pipeline_eval.md:1)
