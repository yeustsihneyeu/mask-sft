from dataclasses import dataclass
from pathlib import Path

from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import Trainer, TrainingArguments, default_data_collator

from src.llm.models import Model


@dataclass(slots=True)
class TrainingProcess():
    model: Model
    train_ds: Dataset
    val_ds: Dataset
    output_dir: str
    r: int = 8

    def _lora_config(self):
        return LoraConfig(
            r=self.r,
            target_modules="all-linear",
            task_type=TaskType.CAUSAL_LM,
            lora_alpha=16,
            lora_dropout=0.05
        )

    def _peft_model(self):
        peft_config = self._lora_config()
        return get_peft_model(model=self.model.model, peft_config=peft_config)

    def _training_args(self):
        return TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            num_train_epochs=10,
            learning_rate=5e-4,
            logging_steps=1,
            eval_strategy="epoch",
            save_strategy="no",
            report_to="none",
        )

    def _trainer(self):
        return Trainer(
            model=self._peft_model(),
            args=self._training_args(),
            train_dataset=self.train_ds,
            eval_dataset=self.val_ds,
            data_collator=default_data_collator,
        )

    def train_save(self):
        trainer = self._trainer()
        trainer.train()
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(output_path)
        self.model.tokenizer.save_pretrained(output_path)
