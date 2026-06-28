# -*- coding: utf-8 -*-
"""Utilities for loading data and generating ParsBERT sentence embeddings."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from features import normalize


# ---------------------------------------------------------------------------
# Dataset and batching helpers
# ---------------------------------------------------------------------------
def load_dataset(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["records"] if isinstance(data, dict) and "records" in data else data


def batch_list(items: List[str], batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


# ---------------------------------------------------------------------------
# ParsBERT pooling and loading
# ---------------------------------------------------------------------------
def mean_pooling(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def get_device(prefer_gpu: bool = False) -> torch.device:
    if prefer_gpu and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_parsbert(model_name: str, device: torch.device):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return tokenizer, model


# ---------------------------------------------------------------------------
# Public embedding API
# ---------------------------------------------------------------------------
def compute_embeddings(
    sentences: List[str],
    model_name: str = "HooshvareLab/bert-fa-base-uncased",
    batch_size: int = 4,
    max_length: int = 96,
    prefer_gpu: bool = False,
) -> np.ndarray:
    """
    Convert Persian sentences into numeric vectors with ParsBERT.

    ParsBERT is not fine-tuned here. It is used as a frozen feature extractor,
    which keeps the project lighter and easier to run on CPU.
    """
    sentences = [normalize(s) for s in sentences]
    device = get_device(prefer_gpu)
    tokenizer, model = load_parsbert(model_name, device)
    vectors = []
    with torch.no_grad():
        for batch in tqdm(list(batch_list(sentences, batch_size)), desc="ParsBERT embeddings"):
            encoded = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
            )
            encoded = {k: v.to(device) for k, v in encoded.items()}
            output = model(**encoded)
            pooled = mean_pooling(output.last_hidden_state, encoded["attention_mask"])
            vectors.append(pooled.cpu().numpy().astype("float32"))
    return np.vstack(vectors)
