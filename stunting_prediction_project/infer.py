import argparse
import json
import os
import re

import joblib
import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Samakan pembersihan nama kolom dengan proses training/notebook."""
    df = df.copy()
    df.columns = [re.sub(r"\s+", "_", str(c).strip()) for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="artifacts_sklearn171/best_model_RandomForest.joblib")
    parser.add_argument("--metadata", default="artifacts_sklearn171/metadata.json")
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", default="predictions.csv")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        raise FileNotFoundError(f"Model file not found: {args.model}")
    if not os.path.exists(args.metadata):
        raise FileNotFoundError(f"Metadata file not found: {args.metadata}")

    # Load model dan metadata
    model = joblib.load(args.model)
    with open(args.metadata, "r") as f:
        meta = json.load(f)

    numeric_cols = meta.get("numeric_cols", [])
    categorical_cols = meta.get("categorical_cols", [])
    feature_cols = list(numeric_cols) + list(categorical_cols)

    # Load data input
    df_raw = pd.read_csv(args.input_csv)
    df = clean_column_names(df_raw)

    # Validasi kolom
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(
            "Input CSV is missing required feature columns: " + ", ".join(missing)
        )

    X = df[feature_cols].copy()

    # Prediksi
    y_pred = model.predict(X)
    try:
        y_proba = model.predict_proba(X)[:, 1]
    except Exception:
        y_proba = None

    out = df_raw.copy()
    out["pred_stunting"] = y_pred
    if y_proba is not None:
        out["prob_stunting"] = y_proba

    out.to_csv(args.output_csv, index=False)
    print(f"Saved predictions to: {args.output_csv}")


if __name__ == "__main__":
    main()
