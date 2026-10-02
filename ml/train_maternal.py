"""Train and evaluate a maternal risk baseline on UCI dataset 863.

Run with: python -m ml.train_maternal
The first run fetches/caches the dataset; later runs use the cached CSV.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "raw" / "maternal_health_risk_uci_863.csv"
DEFAULT_ARTIFACT = ROOT / "artifacts" / "maternal_risk_uci_rf.joblib"
DEFAULT_REPORT = ROOT / "artifacts" / "maternal_risk_uci_rf.metrics.json"
UCI_CITATION = "Ahmed, M. (2020). Maternal Health Risk [Dataset]. UCI ML Repository. https://doi.org/10.24432/C5DP5D"
FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
CLASS_ORDER = ["low risk", "mid risk", "high risk"]
CLASS_DISPLAY = {"low risk": "Low Risk", "mid risk": "Mid Risk", "high risk": "High Risk"}


def fetch_dataset() -> pd.DataFrame:
    from ucimlrepo import fetch_ucirepo

    dataset = fetch_ucirepo(id=863)
    features = dataset.data.features.copy()
    target = dataset.data.targets
    if target is None or target.shape[1] != 1:
        raise ValueError("Expected exactly one target column from UCI dataset 863.")
    frame = features.copy()
    frame["RiskLevel"] = target.iloc[:, 0].values
    return frame


def load_dataset(path: Path, *, refresh: bool = False) -> pd.DataFrame:
    if refresh or not path.exists():
        frame = fetch_dataset()
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        path.with_suffix(".citation.txt").write_text(
            f"Source: {UCI_CITATION}\nLicense: CC BY 4.0\n",
            encoding="utf-8",
        )
        return frame
    return pd.read_csv(path)


def prepare_dataset(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    normalized = {str(column).strip().lower(): column for column in frame.columns}
    expected = {
        "age": "Age",
        "systolicbp": "SystolicBP",
        "diastolicbp": "DiastolicBP",
        "bs": "BS",
        "bodytemp": "BodyTemp",
        "heartrate": "HeartRate",
        "risklevel": "RiskLevel",
    }
    missing = sorted(set(expected) - set(normalized))
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {missing}")

    cleaned = pd.DataFrame({
        destination: pd.to_numeric(frame[normalized[source]], errors="coerce")
        for source, destination in expected.items()
        if destination != "RiskLevel"
    })
    labels = (
        frame[normalized["risklevel"]]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"moderate risk": "mid risk"})
    )
    unknown = sorted(set(labels) - set(CLASS_ORDER))
    if unknown:
        raise ValueError(f"Unexpected risk labels: {unknown}")
    if cleaned.isna().any().any() or labels.isna().any():
        # Imputation is kept in the pipeline for future training data; the UCI
        # snapshot itself is expected to have complete values.
        if labels.isna().any():
            raise ValueError("Target labels contain missing values.")
    return cleaned[FEATURES], labels


def make_pipeline() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=500,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        )),
    ])


def evaluate_grouped_cv(features: pd.DataFrame, labels: pd.Series) -> dict:
    # Repeated identical feature vectors must stay in the same fold. A random
    # row split can otherwise put copies in both train and validation sets.
    groups = pd.util.hash_pandas_object(features, index=False).astype(str)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    predictions = pd.Series(index=labels.index, dtype="object")
    fold_sizes = []
    for train_indices, test_indices in splitter.split(features, labels, groups):
        estimator = make_pipeline()
        estimator.fit(features.iloc[train_indices], labels.iloc[train_indices])
        predictions.iloc[test_indices] = estimator.predict(features.iloc[test_indices])
        fold_sizes.append({"train": len(train_indices), "validation": len(test_indices)})

    if predictions.isna().any():
        raise RuntimeError("Grouped cross-validation did not produce a prediction for every row.")
    y_true = labels.to_numpy()
    y_pred = predictions.to_numpy()
    report = classification_report(
        y_true,
        y_pred,
        labels=CLASS_ORDER,
        output_dict=True,
        zero_division=0,
    )
    return {
        "method": "5-fold StratifiedGroupKFold grouped by exact feature profile",
        "macro_f1": float(f1_score(y_true, y_pred, labels=CLASS_ORDER, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=CLASS_ORDER).tolist(),
        "class_order": CLASS_ORDER,
        "fold_sizes": fold_sizes,
    }


def train(
    data_path: Path,
    artifact_path: Path,
    report_path: Path,
    *,
    refresh: bool = False,
    worker_labels_path: Path | None = None,
) -> dict:
    uci_raw = load_dataset(data_path, refresh=refresh)
    uci_features, uci_labels = prepare_dataset(uci_raw)
    features = uci_features
    labels = uci_labels
    worker_rows = 0
    if worker_labels_path is not None:
        worker_raw = pd.read_csv(worker_labels_path)
        sensitive_columns = {"patient_id", "user_id", "uid", "phone", "phone_number", "name", "facility_id"}
        if any(
            token in str(column).strip().lower()
            for column in worker_raw.columns
            for token in sensitive_columns
        ):
            raise ValueError("Worker-label CSV must not contain patient, worker, or facility identifiers.")
        worker_features, worker_labels = prepare_dataset(worker_raw)
        worker_rows = len(worker_features)
        features = pd.concat([features, worker_features], ignore_index=True)
        labels = pd.concat([labels, worker_labels], ignore_index=True)
    groups = pd.util.hash_pandas_object(features, index=False)
    group_labels = pd.DataFrame({"group": groups, "label": labels}).groupby("group")["label"].nunique()
    contradictory_profiles = int((group_labels > 1).sum())

    evaluation = evaluate_grouped_cv(features, labels)
    fitted_model = make_pipeline().fit(features, labels)
    fingerprint_frame = features.copy()
    fingerprint_frame["RiskLevel"] = labels.to_numpy()
    data_fingerprint = hashlib.sha256(
        pd.util.hash_pandas_object(fingerprint_frame, index=False).values.tobytes()
    ).hexdigest()
    model_version = f"maternal-rf-{data_fingerprint[:12]}"
    artifact = {
        "model": fitted_model,
        "model_version": model_version,
        "feature_names": FEATURES,
        "class_order": CLASS_ORDER,
        "class_display": CLASS_DISPLAY,
        "dataset": {
            "name": "Maternal Health Risk",
            "uci_id": 863,
            "citation": UCI_CITATION,
            "license": "CC BY 4.0",
            "source_population": "Bangladesh hospitals, community clinics, and rural maternal care",
            "row_count": int(len(uci_features)),
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_rows_total": int(len(features)),
        "reviewed_worker_label_rows": worker_rows,
        "training_sources": {
            "uci_rows": int(len(uci_features)),
            "reviewed_worker_label_rows": worker_rows,
        },
        "training_data_fingerprint": data_fingerprint,
        "validation": evaluation,
        "clinical_validation_status": "not_clinically_validated",
        "decision_support_only": True,
    }
    metrics = {
        "model_version": artifact["model_version"],
        "dataset": artifact["dataset"],
        "reviewed_worker_label_rows": worker_rows,
        "training_rows_total": int(len(features)),
        "training_sources": {
            "uci_rows": int(len(uci_features)),
            "reviewed_worker_label_rows": worker_rows,
        },
        "training_data_fingerprint": data_fingerprint,
        "features": FEATURES,
        "units": {
            "Age": "years",
            "SystolicBP": "mmHg",
            "DiastolicBP": "mmHg",
            "BS": "mmol/L",
            "BodyTemp": "degrees Fahrenheit",
            "HeartRate": "beats per minute",
        },
        "class_counts": {str(key): int(value) for key, value in labels.value_counts().items()},
        "exact_feature_profiles": int(groups.nunique()),
        "contradictory_label_profiles": contradictory_profiles,
        "validation": evaluation,
        "clinical_validation_status": "not_clinically_validated",
        "decision_support_only": True,
    }

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_path)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Local CSV cache path")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--refresh", action="store_true", help="Fetch the current UCI copy again")
    parser.add_argument(
        "--worker-labels",
        type=Path,
        help=(
            "Optional reviewed CSV using Age,SystolicBP,DiastolicBP,BS,BodyTemp,HeartRate,RiskLevel; "
            "do not include patient identifiers."
        ),
    )
    args = parser.parse_args()
    metrics = train(
        args.data,
        args.artifact,
        args.report,
        refresh=args.refresh,
        worker_labels_path=args.worker_labels,
    )
    print(json.dumps(metrics, indent=2))
    print(f"\nSaved model: {args.artifact}")
    print(f"Saved metrics: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())