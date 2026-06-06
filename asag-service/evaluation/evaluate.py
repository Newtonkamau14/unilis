from __future__ import annotations
import argparse
import os
import sys
import json
import numpy as np
import torch
from dataclasses import dataclass, asdict
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from data.dataset_loader import load_dataset, AnswerInstance
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.metrics import (
    f1_score,
    cohen_kappa_score,
    mean_absolute_error,
    classification_report,
    confusion_matrix,
)
from scipy.stats import pearsonr
 
 
MAX_LEN = 128
 
 
@dataclass
class EvaluationResult:
    dataset: str
    split: str
    model_type: str             # "multi_component" or "holistic_baseline"
    n_instances: int
    pearson_r: float
    pearson_p: float
    cohen_kappa_quadratic: float
    f1_macro: float
    f1_weighted: float
    mae: float
    accuracy: float
    per_class_f1: dict
    confusion_matrix: list
 
 
def predict_bert(
    instances: list[AnswerInstance],
    model_dir: str,
    device: torch.device,
    batch_size: int = 32,
) -> list[int]:
    """Run inference with a fine-tuned BERT classifier."""
    tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
    model = DistilBertForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()
 
    all_preds = []
    for i in range(0, len(instances), batch_size):
        batch_insts = instances[i: i + batch_size]
        encodings = tokenizer(
            [inst.reference_answer for inst in batch_insts],
            [inst.student_answer for inst in batch_insts],
            max_length=MAX_LEN,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        input_ids = encodings["input_ids"].to(device)
        attention_mask = encodings["attention_mask"].to(device)
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
        preds = outputs.logits.argmax(dim=-1).cpu().tolist()
        all_preds.extend(preds)
 
    return all_preds
 
 
def holistic_baseline_predict(instances: list[AnswerInstance]) -> list[int]:
    """
    Baseline: single holistic BERT using sentence-transformers cosine similarity.
    Thresholds tuned to SemEval 3-way split.
    This is the comparison baseline from Objective 4.
    """
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        raise RuntimeError("sentence-transformers required for baseline. pip install sentence-transformers")
 
    ref_texts = [i.reference_answer for i in instances]
    stu_texts = [i.student_answer for i in instances]
 
    ref_embs = model.encode(ref_texts, normalize_embeddings=True, show_progress_bar=False)
    stu_embs = model.encode(stu_texts, normalize_embeddings=True, show_progress_bar=False)
 
    sims = np.sum(ref_embs * stu_embs, axis=1)
 
    # Threshold calibration (derived from SciEntsBank validation set)
    preds = []
    for s in sims:
        if s >= 0.75:
            preds.append(2)   # correct
        elif s >= 0.45:
            preds.append(1)   # partially correct
        else:
            preds.append(0)   # incorrect
    return preds
 
 
def compute_metrics(
    y_true: list[int],
    y_pred: list[int],
    dataset: str,
    split: str,
    model_type: str,
) -> EvaluationResult:
    """Compute all metrics from Section 3.4."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
 
    pearson_r, pearson_p = pearsonr(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred, weights="quadratic")
    f1_mac = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_wt = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    mae = mean_absolute_error(y_true, y_pred)
    acc = np.mean(y_true == y_pred)
 
    per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
    label_names = ["incorrect", "partially_correct", "correct"]
    per_class_dict = {label_names[i]: round(float(per_class[i]), 4) for i in range(len(per_class))}
 
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist()
 
    return EvaluationResult(
        dataset=dataset,
        split=split,
        model_type=model_type,
        n_instances=len(y_true),
        pearson_r=round(float(pearson_r), 4),
        pearson_p=round(float(pearson_p), 6),
        cohen_kappa_quadratic=round(float(kappa), 4),
        f1_macro=round(float(f1_mac), 4),
        f1_weighted=round(float(f1_wt), 4),
        mae=round(float(mae), 4),
        accuracy=round(float(acc), 4),
        per_class_f1=per_class_dict,
        confusion_matrix=cm,
    )
 
 
def print_report(result: EvaluationResult, comparison: EvaluationResult | None = None):
    print(f"\n{'='*60}")
    print(f"Dataset: {result.dataset} | Split: {result.split} | Model: {result.model_type}")
    print(f"{'='*60}")
    print(f"  Instances:              {result.n_instances}")
    print(f"  Pearson r:              {result.pearson_r}  (p={result.pearson_p})")
    print(f"  Cohen's Kappa (QW):     {result.cohen_kappa_quadratic}")
    print(f"  F1 Macro:               {result.f1_macro}")
    print(f"  F1 Weighted:            {result.f1_weighted}")
    print(f"  MAE:                    {result.mae}")
    print(f"  Accuracy:               {result.accuracy}")
    print(f"  Per-class F1:")
    for cls, score in result.per_class_f1.items():
        print(f"    {cls:<25} {score}")
 
    if comparison:
        print(f"\n--- vs Baseline ({comparison.model_type}) ---")
        delta_kappa = result.cohen_kappa_quadratic - comparison.cohen_kappa_quadratic
        delta_f1 = result.f1_macro - comparison.f1_macro
        delta_pearson = result.pearson_r - comparison.pearson_r
        print(f"  ΔKappa:    {delta_kappa:+.4f}  ({'better' if delta_kappa > 0 else 'worse'})")
        print(f"  ΔF1 Macro: {delta_f1:+.4f}  ({'better' if delta_f1 > 0 else 'worse'})")
        print(f"  ΔPearson:  {delta_pearson:+.4f}  ({'better' if delta_pearson > 0 else 'worse'})")
 
 
def run_evaluation(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
 
    if args.use_hf:
        from data.dataset_loader import load_huggingface_beetle
        data = load_huggingface_beetle()
        instances = data["test"]
        print(f"Loaded {len(instances)} test instances from HuggingFace Beetle dataset")
    else:
        instances = load_dataset(args.dataset, args.split, args.data_dir)
    y_true = [i.label for i in instances]
 
    results = []
    os.makedirs(args.output_dir, exist_ok=True)
 
    # --- Multi-component model (fine-tuned) ---
    print(f"\nRunning fine-tuned model from {args.model_dir} ...")
    y_pred_ft = predict_bert(instances, args.model_dir, device)
    result_ft = compute_metrics(y_true, y_pred_ft, args.dataset, args.split, "multi_component_bert")
    results.append(result_ft)
 
    # --- Holistic baseline ---
    print("Running holistic baseline ...")
    y_pred_bl = holistic_baseline_predict(instances)
    result_bl = compute_metrics(y_true, y_pred_bl, args.dataset, args.split, "holistic_baseline")
    results.append(result_bl)
 
    # --- Print reports ---
    print_report(result_ft, comparison=result_bl)
    print_report(result_bl)
 
    # --- Detailed sklearn report ---
    label_names = ["incorrect", "partially_correct", "correct"]
    print(f"\n--- Detailed classification report (fine-tuned) ---")
    print(classification_report(y_true, y_pred_ft, target_names=label_names, zero_division=0))
 
    # --- Save results to JSON ---
    out_path = os.path.join(
        args.output_dir,
        f"results_{args.dataset}_{args.split}.json"
    )
    with open(out_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nResults saved to: {out_path}")
 
    return results
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="data/datasets")
    parser.add_argument("--model_dir", default="models/semantic_bert")
    parser.add_argument("--dataset", default="scientsbank", choices=["scientsbank", "beetle"])
    parser.add_argument("--split", default="test-unseen",
                        choices=["train", "test-unseen", "test-unseen-domains", "all"])
    parser.add_argument("--output_dir", default="evaluation/results")
    parser.add_argument("--use-hf", dest="use_hf", action="store_true", default=False, help="Evaluate on HuggingFace Beetle dataset")
    args = parser.parse_args()
    run_evaluation(args)