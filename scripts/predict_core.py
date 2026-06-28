# -*- coding: utf-8 -*-
"""Core prediction pipeline used by both the GUI server and quick checks."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np

from features import normalize, extract_features, FEATURE_KEYS, score_label, simple_explanation
from parsbert_utils import compute_embeddings


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------
def read_sentences_from_text(text: str) -> List[str]:
    sentences: List[str] = []
    for raw in str(text or "").splitlines():
        raw = normalize(raw)
        if not raw:
            continue
        parts = re.split(r"(?<=[.؟!؛])\s+", raw)
        for part in parts:
            part = normalize(part)
            if part:
                sentences.append(part)
    return sentences


def read_sentences(path: Path) -> List[str]:
    return read_sentences_from_text(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Model wrapper
# ---------------------------------------------------------------------------
class LiteraryPredictor:
    def __init__(self, model_path: Path):
        pack = joblib.load(model_path)
        self.base_model = pack["base_model"]
        self.max_length = int(pack["max_length"])
        self.scaler = pack["scaler"]
        self.model = pack["model"]

    def predict(self, sentences: List[str], batch_size: int = 4, prefer_gpu: bool = False) -> List[Dict]:
        if not sentences:
            return []

        embeddings = compute_embeddings(
            sentences,
            model_name=self.base_model,
            batch_size=batch_size,
            max_length=self.max_length,
            prefer_gpu=prefer_gpu,
        )

        feature_dicts = [extract_features(sentence) for sentence in sentences]
        numeric_features = np.array(
            [[features.get(key, 0.0) for key in FEATURE_KEYS] for features in feature_dicts],
            dtype="float32",
        )
        x = np.hstack([embeddings, numeric_features]).astype("float32")
        predictions = np.clip(self.model.predict(self.scaler.transform(x)), 1, 10)

        rows = []
        for index, (sentence, prediction, features) in enumerate(zip(sentences, predictions, feature_dicts), start=1):
            score = int(round(float(prediction)))
            rows.append({
                "id": index,
                "sentence": sentence,
                "predicted_score_float": round(float(prediction), 3),
                "predicted_score": score,
                "label": score_label(score),
                "explanation": simple_explanation(score, features),
            })
        return rows
