"""
train_semantic.py
------------------
Fine-tunes a BERT model for semantic scoring using SciEntsBank + Beetle.

Approach (Objective 3):
  - Task: 3-class classification (correct / partially_correct / incorrect)
  - Input: [CLS] reference_answer [SEP] student_answer [SEP]
  - Model: bert-base-uncased fine-tuned with a classification head
  - Loss: CrossEntropyLoss
  - Saved to: models/semantic_bert/

This produces the fine-tuned model used by SemanticScorer in production.
The sentence embedding from the fine-tuned [CLS] token is significantly
more calibrated for grading than the generic pretrained model.

Usage:
  python -m training.train_semantic \
    --data_dir data/datasets \
    --output_dir models/semantic_bert \
    --epochs 5 \
    --batch_size 16
"""

from __future__ import annotations
import argparse
import os
import random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from sklearn.model_selection import train_test_split

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.dataset_loader import load_all, AnswerInstance


SEED = 42
NUM_LABELS = 3
MAX_LEN = 128


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class AnswerDataset(Dataset):
    def __init__(self, instances: list[AnswerInstance], tokenizer: BertTokenizer, max_len: int):
        self.instances = instances
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.instances)

    def __getitem__(self, idx):
        inst = self.instances[idx]
        # Encode: [CLS] reference [SEP] student [SEP]
        encoding = self.tokenizer(
            inst.reference_answer,
            inst.student_answer,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(inst.label, dtype=torch.long),
        }


def train(args):
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 1. Load data
    print("\n--- Loading datasets ---")
    all_data = load_all(args.data_dir)
    instances = []
    for name, insts in all_data.items():
        train_insts = [i for i in insts if i.split == "train"]
        instances.extend(train_insts)
        print(f"  {name}: {len(train_insts)} training instances")

    if not instances:
        raise RuntimeError(
            "No training data found. Download SciEntsBank and Beetle datasets first.\n"
            "See data/dataset_loader.py for download instructions."
        )

    from collections import Counter
    labels = [i.label for i in instances]
    min_class_count = min(Counter(labels).values())
    use_stratify = min_class_count >= 2 and len(instances) >= 20

    train_instances, val_instances = train_test_split(
        instances, test_size=0.15, random_state=SEED,
        stratify=labels if use_stratify else None
    )
    print(f"\nTrain: {len(train_instances)} | Val: {len(val_instances)}")
    if not use_stratify:
        print("  [NOTE] Sample dataset too small for stratified split — using random split.")
        print("  [NOTE] Download full SemEval datasets for meaningful results.")

    # 2. Tokenizer + model
    print(f"\n--- Loading model: {args.base_model} ---")
    tokenizer = DistilBertTokenizer.from_pretrained(args.base_model)
    model = DistilBertForSequenceClassification.from_pretrained(
        args.base_model, num_labels=NUM_LABELS
    )
    model.to(device)

    # 3. Dataloaders
    train_dataset = AnswerDataset(train_instances, tokenizer, MAX_LEN)
    val_dataset = AnswerDataset(val_instances, tokenizer, MAX_LEN)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # 4. Optimizer + scheduler
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps,
    )

    # 5. Training loop
    best_val_acc = 0.0
    os.makedirs(args.output_dir, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
                preds = outputs.logits.argmax(dim=-1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        val_acc = correct / total
        print(f"Epoch {epoch}/{args.epochs} | Loss: {avg_loss:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            model.save_pretrained(args.output_dir, safe_serialization=False)
            tokenizer.save_pretrained(args.output_dir)
            print(f"  ✓ Saved best model (val_acc={val_acc:.4f}) to {args.output_dir}")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.4f}")
    print(f"Fine-tuned model saved to: {args.output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune BERT for semantic grading")
    parser.add_argument("--data_dir", default="data/datasets")
    parser.add_argument("--output_dir", default="models/semantic_bert")
    parser.add_argument("--base_model", default="distilbert-base-uncased")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    args = parser.parse_args()
    train(args)