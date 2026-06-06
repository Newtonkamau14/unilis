from __future__ import annotations
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Literal


LABEL_MAP = {
    "correct": 2,
    "partially_correct_incomplete": 1,
    "contradictory": 0,
    "irrelevant": 0,
    "non_domain": 0,
}

LABEL_STR = {2: "correct", 1: "partially_correct", 0: "incorrect"}


@dataclass
class AnswerInstance:
    question_id: str
    question_text: str
    reference_answer: str
    student_answer: str
    label: int          # 0, 1, 2
    label_str: str      # "correct" / "partially_correct" / "incorrect"
    dataset: str        # "scientsbank" or "beetle"
    split: str          # "train" / "test-unseen" / "test-unseen-domains"


def load_semeval_xml(xml_path: str, dataset_name: str, split: str) -> list[AnswerInstance]:
    """Parse a single SemEval 2013 Task 7 XML file."""
    instances = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[WARN] Could not parse {xml_path}: {e}")
        return instances

    question_text = root.findtext("questionText", default="").strip()
    reference_answer = root.findtext("referenceAnswer", default="").strip()
    question_id = root.get("id", os.path.basename(xml_path).replace(".xml", ""))

    for student_answer in root.findall(".//studentAnswer"):
        raw_label = student_answer.get("accuracy", "irrelevant").strip().lower()
        label_int = LABEL_MAP.get(raw_label, 0)
        text = (student_answer.text or "").strip()
        if not text:
            continue
        instances.append(AnswerInstance(
            question_id=question_id,
            question_text=question_text,
            reference_answer=reference_answer,
            student_answer=text,
            label=label_int,
            label_str=LABEL_STR[label_int],
            dataset=dataset_name,
            split=split,
        ))
    return instances


def load_dataset(
    dataset_name: Literal["scientsbank", "beetle"],
    split: Literal["train", "test-unseen", "test-unseen-domains", "all"],
    base_dir: str = "data/datasets",
) -> list[AnswerInstance]:
    """
    Load all instances for a given dataset and split.

    Args:
        dataset_name: "scientsbank" or "beetle"
        split:        "train", "test-unseen", "test-unseen-domains", or "all"
        base_dir:     Root directory containing dataset folders.

    Returns:
        List of AnswerInstance objects.
    """
    dataset_dir = os.path.join(base_dir, dataset_name)
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(
            f"Dataset not found at '{dataset_dir}'.\n"
            f"Download from: https://www.cs.york.ac.uk/semeval-2013/task7/\n"
            f"Expected structure: {dataset_dir}/train/*.xml"
        )

    splits = (
        ["train", "test-unseen", "test-unseen-domains"]
        if split == "all"
        else [split]
    )

    all_instances = []
    for sp in splits:
        split_dir = os.path.join(dataset_dir, sp)
        if not os.path.exists(split_dir):
            print(f"[WARN] Split directory not found: {split_dir}")
            continue
        for fname in sorted(os.listdir(split_dir)):
            if fname.endswith(".xml"):
                fpath = os.path.join(split_dir, fname)
                instances = load_semeval_xml(fpath, dataset_name, sp)
                all_instances.extend(instances)

    print(f"Loaded {len(all_instances)} instances from {dataset_name}/{split}")
    return all_instances


def load_all(base_dir: str = "data/datasets") -> dict[str, list[AnswerInstance]]:
    """Load both datasets, all splits. Returns dict keyed by dataset name."""
    result = {}
    for name in ["scientsbank", "beetle"]:
        try:
            result[name] = load_dataset(name, "all", base_dir)
        except FileNotFoundError as e:
            print(f"[SKIP] {e}")
    return result


def label_distribution(instances: list[AnswerInstance]) -> dict:
    from collections import Counter
    counts = Counter(i.label_str for i in instances)
    total = len(instances)
    return {k: {"count": v, "pct": round(v / total * 100, 1)} for k, v in counts.items()}


# =============================================================================
# HUGGINGFACE BEETLE LOADER
# =============================================================================

HF_LABEL_MAP_5WAY = {
    "correct": 2,
    "correct_but_incomplete": 1,
    "partially_correct_incomplete": 1,
    "contradictory": 0,
    "irrelevant": 0,
    "non_domain": 0,
}


def load_huggingface_beetle(split="all", test_size=0.2, seed=42):
    """
    Load Atomi/semeval_2013_task_7_beetle_5way from HuggingFace.
    ~12,000 examples, 56 questions, electricity/circuits domain.
    """
    try:
        from datasets import load_dataset as hf_load
    except ImportError:
        raise RuntimeError("Run: pip install datasets")

    import random

    print("Loading Atomi/semeval_2013_task_7_beetle_5way from HuggingFace...")
    ds = hf_load("Atomi/semeval_2013_task_7_beetle_5way")
    print(f"Available splits: {list(ds.keys())}")

    instances = []
    for split_name, dataset in ds.items():
        for row in dataset:
            question  = str(row.get("question", row.get("question_text", ""))).strip()
            reference = str(row.get("reference_answer", row.get("reference", row.get("model_answer", "")))).strip()
            student   = str(row.get("student_answer", row.get("answer", row.get("student", "")))).strip()
            raw_label = row.get("label", row.get("accuracy", row.get("score", "irrelevant")))
            qid       = str(row.get("id", row.get("question_id", "")))

            if isinstance(raw_label, int):
                label_int = min(raw_label, 2)
                label_str = {2: "correct", 1: "partially_correct", 0: "incorrect"}[label_int]
            else:
                raw_label = str(raw_label).strip().lower()
                label_int = HF_LABEL_MAP_5WAY.get(raw_label, 0)
                label_str = {2: "correct", 1: "partially_correct", 0: "incorrect"}[label_int]

            if not student or not reference:
                continue

            instances.append(AnswerInstance(
                question_id=qid,
                question_text=question,
                reference_answer=reference,
                student_answer=student,
                label=label_int,
                label_str=label_str,
                dataset="beetle_hf",
                split=split_name,
            ))

    print(f"Loaded {len(instances)} total instances")

    random.seed(seed)
    random.shuffle(instances)
    idx = int(len(instances) * (1 - test_size))
    train_instances = instances[:idx]
    test_instances  = instances[idx:]
    for i in train_instances: i.split = "train"
    for i in test_instances:  i.split = "test-unseen"

    print(f"Split -> Train: {len(train_instances)} | Test: {len(test_instances)}")
    return {"train": train_instances, "test": test_instances}
