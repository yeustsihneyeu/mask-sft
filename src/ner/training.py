from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
    EarlyStoppingCallback,
)

from src.ner.models import Model
from seqeval.metrics import f1_score, precision_score, recall_score



@dataclass(slots=True)
class TrainingProcess():
    model: Model
    train_ds: Dataset
    val_ds: Dataset
    output_dir: str
    r: int = 8
    early_stopping_patience: int = 3
    _peft_model_instance: object | None = field(init=False, default=None, repr=False)

    def _target_modules(self) -> list[str]:
        if self.model.model is None:
            self.model.get_model()

        linear_suffixes = {name.split(".")[-1] for name, module in self.model.model.named_modules() if module.__class__.__name__ == "Linear"}
        candidates = [
            ["query_proj", "key_proj", "value_proj"],
            ["query", "key", "value"],
        ]

        for modules in candidates:
            if all(module_name in linear_suffixes for module_name in modules):
                return modules

        raise ValueError(
            f"Could not infer LoRA target modules from linear layers: {sorted(linear_suffixes)}"
        )

    def _lora_config(self):
        return LoraConfig(
            r=self.r,
            target_modules=self._target_modules(),
            task_type=TaskType.TOKEN_CLS,
            lora_alpha=16,
            lora_dropout=0.1
        )

    def _peft_model(self):
        if self._peft_model_instance is not None:
            return self._peft_model_instance

        if self.model.model is None:
            self.model.get_model()

        # If the model in memory is already PEFT-wrapped from a previous notebook run,
        # reuse it instead of trying to wrap the same object again.
        if getattr(self.model.model, "peft_config", None) is not None:
            self._peft_model_instance = self.model.model
            return self._peft_model_instance

        peft_config = self._lora_config()
        self._peft_model_instance = get_peft_model(
            model=self.model.model,
            peft_config=peft_config,
        )
        return self._peft_model_instance

    def _training_args(self):
        return TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=20,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_ratio=0.1,
            gradient_accumulation_steps=4,
            max_grad_norm=1.0,
            save_total_limit=2,
            logging_strategy="steps",
            logging_steps=1,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            report_to="none",
            fp16=False,           # MPS не поддерживает fp16
            bf16=False,
        )


    def compute_metrics(self, eval_pred):
        predictions, labels = eval_pred
        predicted_ids = predictions.argmax(axis=2)

        true_predictions = []
        true_labels = []

        for pred_row, label_row in zip(predicted_ids, labels):
            pred_labels = []
            gold_labels = []

            for pred_id, gold_id in zip(pred_row, label_row):
                if gold_id == -100:
                    continue
                pred_labels.append(self.model.config.id2label[int(pred_id)])
                gold_labels.append(self.model.config.id2label[int(gold_id)])

            true_predictions.append(pred_labels)
            true_labels.append(gold_labels)


        return {
            "f1": f1_score(true_labels, true_predictions),
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
        }


    def _trainer(self):
        return Trainer(
            model=self._peft_model(),
            args=self._training_args(),
            train_dataset=self.train_ds,
            eval_dataset=self.val_ds,
            data_collator=DataCollatorForTokenClassification(self.model.tokenizer),
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=self.early_stopping_patience)],
        )


    def train_save(self):
        trainer = self._trainer()
        trainer.train()
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(output_path)
        self.model.tokenizer.save_pretrained(output_path)
