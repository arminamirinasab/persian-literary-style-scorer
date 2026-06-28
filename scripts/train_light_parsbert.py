# -*- coding: utf-8 -*-
"""
Train a lightweight Persian literary scoring model based on ParsBERT embeddings.

The training pipeline keeps ParsBERT frozen, combines its sentence embeddings
with transparent linguistic features, and trains a small regression model for
scores from 1 to 10.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Runtime bootstrap
# ---------------------------------------------------------------------------
def rerun_with_venv_python():
    repo_root = Path(__file__).resolve().parent.parent
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    current_python = Path(sys.executable).resolve()
    if venv_python.exists() and current_python != venv_python.resolve():
        command = [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]]
        raise SystemExit(subprocess.call(command, cwd=repo_root))


rerun_with_venv_python()

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

from features import extract_features, FEATURE_KEYS
from parsbert_utils import compute_embeddings, load_dataset


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
def rows_to_frame(rows):
    df = pd.DataFrame(rows)
    if "split" not in df.columns:
        # Use a simple fallback split when the dataset has no explicit split.
        n = len(df)
        df["split"] = "train"
        df.loc[int(n * .8):int(n * .9), "split"] = "val"
        df.loc[int(n * .9):, "split"] = "test"
    return df


# ---------------------------------------------------------------------------
# Feature matrix construction
# ---------------------------------------------------------------------------
def make_numeric_features(sentences):
    feats = [extract_features(s) for s in sentences]
    return np.array([[f.get(k, 0.0) for k in FEATURE_KEYS] for f in feats], dtype="float32"), feats


# ---------------------------------------------------------------------------
# Evaluation metrics
# ---------------------------------------------------------------------------
def evaluate(y_true, y_pred):
    y_pred_clip = np.clip(y_pred, 1, 10)
    rounded_pred = np.rint(y_pred_clip).astype(int)
    rounded_true = np.rint(y_true).astype(int)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred_clip)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred_clip))),
        "exact_accuracy_rounded": float(np.mean(rounded_pred == rounded_true)),
        "within_1_accuracy": float(np.mean(np.abs(rounded_pred - rounded_true) <= 1)),
    }


# ---------------------------------------------------------------------------
# CLI training flow
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Train lightweight ParsBERT-based Persian literary scorer")
    ap.add_argument("--data", default="data/persian_literary_5000.json", help="JSON dataset path")
    ap.add_argument("--base_model", default="HooshvareLab/bert-fa-base-uncased", help="ParsBERT model name on Hugging Face")
    ap.add_argument("--output_model", default="models/literary_parsbert_light.joblib")
    ap.add_argument("--output_report", default="outputs/train_report.json")
    ap.add_argument("--embedding_cache", default="outputs/parsbert_embeddings_cache.npz")
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--max_length", type=int, default=96)
    ap.add_argument("--max_samples", type=int, default=0, help="For quick test. 0 means use all data.")
    ap.add_argument("--prefer_gpu", action="store_true", help="Use CUDA if available")
    args = ap.parse_args()

    rows = load_dataset(Path(args.data))
    if args.max_samples and args.max_samples > 0:
        rows = rows[:args.max_samples]
    df = rows_to_frame(rows)
    df = df[["id", "sentence", "score", "split"]].dropna().copy()
    df["score"] = df["score"].astype(float)

    sentences = df["sentence"].astype(str).tolist()
    y = df["score"].to_numpy(dtype="float32")

    cache_path = Path(args.embedding_cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    use_cache = False
    if cache_path.exists():
        try:
            cache = np.load(cache_path, allow_pickle=True)
            if int(cache["count"]) == len(sentences) and str(cache["base_model"]) == args.base_model and int(cache["max_length"]) == args.max_length:
                embeddings = cache["embeddings"]
                use_cache = True
                print(f"Loaded cached embeddings: {cache_path}")
        except Exception:
            use_cache = False

    if not use_cache:
        print("Computing ParsBERT embeddings. First run may download the model and can take time on CPU.")
        embeddings = compute_embeddings(
            sentences,
            model_name=args.base_model,
            batch_size=args.batch_size,
            max_length=args.max_length,
            prefer_gpu=args.prefer_gpu,
        )
        np.savez_compressed(cache_path, embeddings=embeddings, count=len(sentences), base_model=args.base_model, max_length=args.max_length)
        print(f"Saved embeddings cache: {cache_path}")

    numeric_features, _ = make_numeric_features(sentences)
    X = np.hstack([embeddings, numeric_features]).astype("float32")

    train_mask = df["split"].eq("train").to_numpy()
    val_mask = df["split"].eq("val").to_numpy()
    test_mask = df["split"].eq("test").to_numpy()

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X[train_mask])
    X_val = scaler.transform(X[val_mask]) if val_mask.any() else np.empty((0, X.shape[1]))
    X_test = scaler.transform(X[test_mask]) if test_mask.any() else np.empty((0, X.shape[1]))

    # Ridge regression is lightweight, CPU-friendly, and easy to explain.
    model = RidgeCV(alphas=[0.1, 1.0, 3.0, 10.0, 30.0])
    model.fit(X_train, y[train_mask])

    report = {
        "project": "Persian Literary Scoring",
        "data_file": args.data,
        "base_model": args.base_model,
        "method": "ParsBERT embeddings + simple regression model",
        "samples": {
            "train": int(train_mask.sum()),
            "validation": int(val_mask.sum()),
            "test": int(test_mask.sum()),
        },
        "metrics": {
            "validation": evaluate(y[val_mask], model.predict(X_val)) if val_mask.any() else {},
            "test": evaluate(y[test_mask], model.predict(X_test)) if test_mask.any() else {},
        },
        "selected_alpha": float(model.alpha_),
    }

    out_model = Path(args.output_model)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "base_model": args.base_model,
        "max_length": args.max_length,
        "feature_keys": FEATURE_KEYS,
        "scaler": scaler,
        "model": model,
        "report": report,
    }, out_model)

    out_report = Path(args.output_report)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Saved model: {out_model}")
    print(f"Saved report: {out_report}")


if __name__ == "__main__":
    main()
