# ASAG Service — Automated Short Answer Grading
## BERT-based Multi-Component Interpretable Grading System

---

## Project Structure

```
asag-service/
├── main.py                        ← FastAPI server
├── requirements.txt
├── data/
│   ├── dataset_loader.py          ← SciEntsBank + Beetle XML parser
│   ├── download_datasets.py       ← Dataset setup helper
│   └── keyword_store.py           ← Domain keyword lists
├── models/
│   ├── schemas.py                 ← Pydantic request/response models
│   └── semantic_bert/             ← Fine-tuned model saved here after training
├── modules/
│   ├── grader.py                  ← Central orchestrator
│   ├── bert_encoder.py            ← Embeddings wrapper
│   ├── preprocessor.py            ← Stop word removal + tokenizer
│   ├── term_extractor.py          ← POS tagging (spaCy)
│   ├── terminology_scorer.py      ← Token-level cosine similarity
│   ├── semantic_scorer.py         ← Fine-tuned BERT / cosine fallback
│   ├── score_aggregator.py        ← Weighted final score
│   ├── mcq_grader.py              ← MCQ exact match
│   └── feedback_generator.py     ← Human-readable feedback
├── training/
│   └── train_semantic.py          ← Fine-tuning pipeline
└── evaluation/
    └── evaluate.py                ← Pearson, Kappa, F1, MAE + baseline comparison
```

---

## Step 1 — Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Step 2 — Get the datasets

### Option A: Sample dataset (no download, for testing only)
```bash
python data/download_datasets.py
# Choose option 1
```

### Option B: Full SemEval 2013 Task 7 datasets (required for real evaluation)

1. Download from: https://www.cs.york.ac.uk/semeval-2013/task7/
2. Extract so the structure looks like:
```
data/datasets/
├── scientsbank/
│   ├── train/          ← .xml files
│   ├── test-unseen/
│   └── test-unseen-domains/
└── beetle/
    ├── train/
    ├── test-unseen/
    └── test-unseen-domains/
```

---

## Step 3 — Fine-tune the BERT model

```bash
# Default: bert-base-uncased, 5 epochs, batch size 16
python -m training.train_semantic

# Or with custom settings
python -m training.train_semantic \
  --base_model bert-base-uncased \
  --data_dir data/datasets \
  --output_dir models/semantic_bert \
  --epochs 5 \
  --batch_size 16 \
  --lr 2e-5
```

Saved to `models/semantic_bert/`. The semantic scorer loads it automatically on next startup.

---

## Step 4 — Evaluate (Objective 4)

```bash
# SciEntsBank test-unseen split
python -m evaluation.evaluate \
  --dataset scientsbank \
  --split test-unseen \
  --model_dir models/semantic_bert \
  --output_dir evaluation/results

# Beetle test-unseen split
python -m evaluation.evaluate \
  --dataset beetle \
  --split test-unseen \
  --model_dir models/semantic_bert \
  --output_dir evaluation/results
```

Outputs:
- Pearson r, Cohen's Kappa (QW), F1 macro/weighted, MAE, accuracy
- Per-class F1 (correct / partially_correct / incorrect)
- Confusion matrix
- Baseline comparison (holistic cosine vs fine-tuned multi-component)
- JSON results saved to `evaluation/results/`

---

## Step 5 — Run the API

```bash
python -m uvicorn main:app --reload --port 8000
```

Interactive docs: http://127.0.0.1:8000/docs

---

## API Usage

### Short answer
```json
POST /grade
{
  "question_context": "Explain the role of mitochondria.",
  "reference_answer": "Mitochondria produce ATP through cellular respiration.",
  "student_answer": "Mitochondria generate energy for the cell.",
  "question_type": "short_answer"
}
```

### MCQ
```json
POST /grade
{
  "question_context": "Which organelle produces ATP?",
  "reference_answer": "B",
  "student_answer": "B",
  "question_type": "multiple_choice",
  "mcq_options": ["A. Nucleus", "B. Mitochondria", "C. Ribosome", "D. Vacuole"]
}
```

---

## Metrics Reference (Section 3.4)

| Metric | What it measures |
|---|---|
| Pearson r | Correlation between system scores and human scores |
| Cohen's Kappa (QW) | Inter-rater agreement, penalises distant disagreements |
| F1 macro | Per-class average F1 (treats all classes equally) |
| F1 weighted | F1 weighted by class frequency |
| MAE | Average score deviation from human score |
| Baseline Δ | Improvement of multi-component over holistic BERT |
