"""
download_datasets.py
---------------------
Helps download and set up SciEntsBank and Beetle datasets.

The SemEval 2013 Task 7 datasets are publicly available.
This script downloads from the official mirrors and extracts
into the expected directory structure.

Usage:
  python data/download_datasets.py
"""

import os
import sys
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "datasets")

SOURCES = {
    "semeval2013-task7": {
        "url": "https://raw.githubusercontent.com/gnikolov-r/semeval-2013-task7-data/main/dataset.zip",
        "fallback_instructions": """
The SciEntsBank and Beetle datasets (SemEval 2013 Task 7) can be obtained from:

1. Official page: https://www.cs.york.ac.uk/semeval-2013/task7/index.php%3Fid=data.html
2. GitHub mirror: https://github.com/gnikolov-r/semeval-2013-task7-data
3. Direct contact: semeval-2013-task7@googlegroups.com

Expected folder structure after extraction:
  data/datasets/
  ├── scientsbank/
  │   ├── train/          ← XML files
  │   ├── test-unseen/
  │   └── test-unseen-domains/
  └── beetle/
      ├── train/
      ├── test-unseen/
      └── test-unseen-domains/

Each XML file follows the SemEval format:
  <question id="...">
    <questionText>...</questionText>
    <referenceAnswer>...</referenceAnswer>
    <studentAnswers>
      <studentAnswer id="..." accuracy="correct">...</studentAnswer>
      ...
    </studentAnswers>
  </question>
"""
    }
}


def check_datasets_present() -> dict[str, bool]:
    results = {}
    for name in ["scientsbank", "beetle"]:
        train_dir = os.path.join(BASE_DIR, name, "train")
        present = os.path.exists(train_dir) and len(os.listdir(train_dir)) > 0
        results[name] = present
        status = "FOUND" if present else "MISSING"
        print(f"  {name}: {status}")
    return results


def create_sample_xml(question_id: str, question: str, reference: str, answers: list[tuple]) -> str:
    """Generate a sample XML file in SemEval format for testing."""
    student_answers_xml = "\n    ".join(
        f'<studentAnswer id="{question_id}_{i}" accuracy="{label}">{text}</studentAnswer>'
        for i, (text, label) in enumerate(answers)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<question id="{question_id}">
  <questionText>{question}</questionText>
  <referenceAnswer>{reference}</referenceAnswer>
  <studentAnswers>
    {student_answers_xml}
  </studentAnswers>
</question>"""


def create_sample_dataset():
    """
    Create a small sample dataset for testing the pipeline
    when the real datasets haven't been downloaded yet.
    """
    sample_data = {
        "scientsbank": [
            {
                "id": "sb_q1",
                "question": "What is photosynthesis?",
                "reference": "Photosynthesis is the process by which green plants use sunlight, water and carbon dioxide to produce glucose and oxygen.",
                "answers": [
                    ("Photosynthesis is when plants use sunlight, water and CO2 to make glucose and release oxygen.", "correct"),
                    ("Plants use sunlight to make food.", "partially_correct_incomplete"),
                    ("Plants breathe in oxygen and release carbon dioxide.", "contradictory"),
                    ("The mitochondria produces ATP through cellular respiration.", "irrelevant"),
                ]
            },
            {
                "id": "sb_q2",
                "question": "What is the role of mitochondria in a cell?",
                "reference": "Mitochondria are organelles that produce ATP through cellular respiration, providing energy for the cell.",
                "answers": [
                    ("Mitochondria produce energy in the form of ATP through cellular respiration.", "correct"),
                    ("Mitochondria make energy for the cell.", "partially_correct_incomplete"),
                    ("Mitochondria are the powerhouse and produce ATP via respiration using oxygen.", "correct"),
                    ("Mitochondria help the cell reproduce.", "irrelevant"),
                ]
            },
        ],
        "beetle": [
            {
                "id": "bt_q1",
                "question": "What happens when you connect a battery to a bulb using a wire?",
                "reference": "When a battery is connected to a bulb using a wire, it creates a complete circuit allowing current to flow, which causes the bulb to light up.",
                "answers": [
                    ("The circuit is complete so current flows from the battery through the wire to the bulb making it light up.", "correct"),
                    ("The bulb lights up because electricity flows.", "partially_correct_incomplete"),
                    ("Nothing happens because the battery needs two wires.", "contradictory"),
                    ("The battery gets hot.", "irrelevant"),
                ]
            },
        ]
    }

    print("\nCreating sample dataset for testing...")
    for dataset_name, questions in sample_data.items():
        for split in ["train", "test-unseen"]:
            split_dir = os.path.join(BASE_DIR, dataset_name, split)
            os.makedirs(split_dir, exist_ok=True)
            for q in questions:
                xml_content = create_sample_xml(
                    q["id"], q["question"], q["reference"], q["answers"]
                )
                fname = os.path.join(split_dir, f"{q['id']}.xml")
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(xml_content)
        print(f"  Created sample {dataset_name} dataset")

    print(f"\nSample dataset created at: {BASE_DIR}")
    print("NOTE: This is a tiny sample for testing only.")
    print("For real evaluation, download the full SemEval 2013 Task 7 datasets.")
    print(SOURCES["semeval2013-task7"]["fallback_instructions"])


if __name__ == "__main__":
    print("=== ASAG Dataset Setup ===\n")
    print("Checking for existing datasets:")
    status = check_datasets_present()

    if all(status.values()):
        print("\nAll datasets found. No action needed.")
        sys.exit(0)

    print("\nOptions:")
    print("  1. Create a small sample dataset for testing (no download needed)")
    print("  2. Show download instructions for the full SemEval 2013 datasets")
    choice = input("\nEnter choice [1/2]: ").strip()

    if choice == "1":
        create_sample_dataset()
    else:
        print(SOURCES["semeval2013-task7"]["fallback_instructions"])
