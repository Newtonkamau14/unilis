from __future__ import annotations
import os
import numpy as np
import torch
from .bert_encoder import BERTEncoder
 
 
FINETUNED_MODEL_DIR = "models/semantic_bert"
# Weighted score: incorrect=0, partial=0.5, correct=1.0
LABEL_WEIGHTS = torch.tensor([0.0, 0.5, 1.0])
 
 
class SemanticScorer:
    def __init__(self, encoder: BERTEncoder, model_dir: str = FINETUNED_MODEL_DIR):
        self.encoder = encoder
        self._ft_model = None
        self._ft_tokenizer = None
        self._use_finetuned = False
        self._try_load_finetuned(model_dir)
 
    def _try_load_finetuned(self, model_dir: str):
        """Load fine-tuned model if it exists."""
        config_path = os.path.join(model_dir, "config.json")
        if not os.path.exists(config_path):
            print(f"[SemanticScorer] Fine-tuned model not found at '{model_dir}'. "
                  f"Using cosine similarity fallback.\n"
                  f"  → Run: python -m training.train_semantic to train.")
            return
        try:
            from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
            self._ft_tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
            self._ft_model = DistilBertForSequenceClassification.from_pretrained(model_dir)
            self._ft_model.eval()
            self._use_finetuned = True
            print(f"[SemanticScorer] Loaded fine-tuned model from '{model_dir}'")
        except Exception as e:
            print(f"[SemanticScorer] Could not load fine-tuned model: {e}. Using fallback.")
 
    def score(self, reference_answer: str, student_answer: str) -> dict:
        if self._use_finetuned:
            return self._score_finetuned(reference_answer, student_answer)
        return self._score_cosine(reference_answer, student_answer)
 
    def _score_finetuned(self, reference_answer: str, student_answer: str) -> dict:
        """Score using fine-tuned BERT classification model."""
        encoding = self._ft_tokenizer(
            reference_answer,
            student_answer,
            max_length=256,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        encoding.pop("token_type_ids", None)
        with torch.no_grad():
            outputs = self._ft_model(**encoding)
        probs = torch.softmax(outputs.logits.squeeze(0), dim=0)
        score = float(torch.dot(probs, LABEL_WEIGHTS).item())
        label_names = ["incorrect", "partially_correct", "correct"]
        predicted_label = label_names[probs.argmax().item()]
        explanation = (
            f"Fine-tuned BERT: {predicted_label} "
            f"(P(correct)={probs[2]:.2f}, P(partial)={probs[1]:.2f}, P(incorrect)={probs[0]:.2f})"
        )
        return {"score": round(score, 4), "similarity_explanation": explanation}
 
    def _score_cosine(self, reference_answer: str, student_answer: str) -> dict:
        """Fallback: cosine similarity of sentence embeddings."""
        ref_vec = self.encoder.get_sentence_embedding(reference_answer)
        stu_vec = self.encoder.get_sentence_embedding(student_answer)
        similarity = float(np.dot(ref_vec, stu_vec))
        similarity = max(0.0, min(1.0, similarity))
        explanation = self._explain(similarity) + " [cosine fallback — train model for better accuracy]"
        return {"score": round(similarity, 4), "similarity_explanation": explanation}
 
    @staticmethod
    def _explain(score: float) -> str:
        if score >= 0.90:
            return "Excellent semantic match."
        elif score >= 0.75:
            return "Good semantic match — most key ideas present."
        elif score >= 0.55:
            return "Partial semantic match — some ideas present but incomplete."
        elif score >= 0.35:
            return "Weak semantic match — touches topic but misses core meaning."
        else:
            return "Poor semantic match — answer does not align with expected meaning."
 


