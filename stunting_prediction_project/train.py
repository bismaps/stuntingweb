# Train script pinned for scikit-learn==1.7.1
# Usage:
#   pip install -r requirements.txt
#   python train.py --csv stunting_wasting_dataset.csv --target Stunting
import argparse, re, json, joblib, warnings, os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

warnings.filterwarnings("ignore")


def is_id_like(c):
    import re
    return bool(re.search(r"(?:^id$|_id$|^no$|^no_|_no$|^index$|nik|nkk|uuid)", c, flags=re.I))


def to_binary_target(y_raw, positive_labels=None, negative_labels=None):
    """Convert target variable to binary format, explicitly mapping stunting vs non-stunting.

    Parameters
    ----------
    y_raw : array-like
        Original target column (e.g. 'Stunting').
    positive_labels : list of str, optional
        Labels that should be mapped to 1 (stunting).
    negative_labels : list of str, optional
        Labels that should be mapped to 0 (tidak stunting).
    """
    s = pd.Series(y_raw).astype(str).str.strip().str.lower()

    # Default mapping khusus untuk konteks stunting anak
    if positive_labels is None:
        positive_labels = [
            "stunted", "severely stunted", "sangat pendek", "pendek", "stunting",
        ]
    if negative_labels is None:
        negative_labels = [
            "normal", "tall", "tinggi", "risk of overweight", "overweight", "obese",
        ]

    mapping: dict[str, int] = {}
    for v in positive_labels:
        mapping[v] = 1
    for v in negative_labels:
        mapping[v] = 0

    # Map exact match dulu
    y = s.map(mapping)

    # Jika masih ada label lain, jatuhkan ke label mayoritas (anggap non-stunting = 0)
    if y.isna().any():
        remaining = s[y.isna()]
        if not remaining.empty:
            le = LabelEncoder().fit(remaining)
            lab = le.transform(remaining)
            lab_series = pd.Series(lab, index=remaining.index)
            maj = lab_series.value_counts().idxmax()
            maj_label = le.inverse_transform([maj])[0]
            maj_label = str(maj_label).strip().lower()
            mapping[maj_label] = 0
            y = s.map(mapping)

    # Fallback terakhir: kalau tetap tidak biner, paksa dengan majority baseline
    y_series = pd.Series(y, index=s.index)
    if y_series.isna().any() or len(y_series.dropna().unique()) > 2:
        lab = LabelEncoder().fit_transform(s)
        lab_series = pd.Series(lab, index=s.index)
        maj = lab_series.value_counts().idxmax()
        y_series = (lab_series != maj).astype(int)

    return y_series.astype(int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--outdir", default="artifacts_sklearn171")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.csv)
    df.columns = [re.sub(r"\\s+", "_", str(c).strip()) for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    df = df.dropna(axis=1, how="all")

    id_cols = [c for c in df.columns if is_id_like(c)]
    X = df.drop(columns=[args.target] + id_cols, errors="ignore")
    y = to_binary_target(df[args.target]).astype(int)

    num_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    cat_cols = [c for c in X.columns if c not in num_cols]

    num_trans = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler(with_mean=False)),
    ])
    cat_trans = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    prep = ColumnTransformer(
        [("num", num_trans, num_cols), ("cat", cat_trans, cat_cols)],
        remainder="drop",
        sparse_threshold=0.3,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=171
    )

    models = {
        "LogisticRegression": Pipeline([
            ("prep", prep),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]),
        "RandomForest": Pipeline([
            ("prep", prep),
            ("clf", RandomForestClassifier(
                n_estimators=150,
                class_weight="balanced_subsample",
                random_state=171,
                n_jobs=-1,
            )),
        ]),
    }

    results = []
    reports = {}
    cms = {}
    trained = {}
    best_name = None
    best_f1 = -1

    for name, mdl in models.items():
        mdl.fit(X_train, y_train)
        y_pred = mdl.predict(X_test)
        try:
            y_proba = mdl.predict_proba(X_test)[:, 1]
            auc_val = roc_auc_score(y_test, y_proba)
        except Exception:
            y_proba = None
            auc_val = float("nan")
        row = {
            "model": name,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision_macro": precision_score(
                y_test, y_pred, average="macro", zero_division=0
            ),
            "recall_macro": recall_score(
                y_test, y_pred, average="macro", zero_division=0
            ),
            "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
            "roc_auc": auc_val,
        }
        results.append(row)
        reports[name] = classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        )
        cms[name] = confusion_matrix(y_test, y_pred).tolist()
        trained[name] = mdl
        if row["f1_macro"] > best_f1:
            best_f1 = row["f1_macro"]
            best_name = name

    model_path = os.path.join(args.outdir, f"best_model_{best_name}.joblib")
    joblib.dump(trained[best_name], model_path)

    meta = {
        "sklearn_version": "1.7.1",
        "csv_path": args.csv,
        "target_col": args.target,
        "dropped_id_cols": id_cols,
        "numeric_cols": num_cols,
        "categorical_cols": cat_cols,
        "results": results,
    }
    with open(os.path.join(args.outdir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(json.dumps({"model_path": model_path, "outdir": args.outdir}, indent=2))


if __name__ == "__main__":
    main()
