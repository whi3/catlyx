"""Load the trusted locally built maternal artifact and return a shadow prediction."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from ml.train_maternal import DEFAULT_ARTIFACT, FEATURES


def predict_maternal(
    measurements: dict,
    *,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict:
    missing = [name for name in FEATURES if measurements.get(name) is None]
    if missing:
        raise ValueError(f"Missing maternal model features: {', '.join(missing)}")

    # joblib uses pickle internally. Only load artifacts produced and controlled
    # by this application's training workflow, never user-supplied files.
    artifact = joblib.load(artifact_path)
    if artifact.get("feature_names") != FEATURES:
        raise ValueError("Maternal model artifact feature schema does not match this API.")
    frame = pd.DataFrame(
        [{name: float(measurements[name]) for name in FEATURES}], columns=FEATURES
    )
    model = artifact["model"]
    prediction = str(model.predict(frame)[0])
    probabilities = model.predict_proba(frame)[0]
    validation = artifact.get("validation", {})
    class_metrics = validation.get("classification_report", {})
    mid_risk_metrics = class_metrics.get("mid risk", {})
    return {
        "model_version": artifact["model_version"],
        "risk_label": artifact["class_display"].get(prediction, prediction),
        "risk_label_source": "uci-863-supervised-baseline",
        "probabilities": {
            str(label): float(probability)
            for label, probability in zip(model.classes_, probabilities)
        },
        "validation_metrics": {
            "method": validation.get("method"),
            "grouped_macro_f1": validation.get("macro_f1"),
            "grouped_balanced_accuracy": validation.get("balanced_accuracy"),
            "mid_risk_recall": mid_risk_metrics.get("recall"),
        },
        "caution": (
            "Experimental prediction only. Review the worker assessment and clinical "
            "guidance; this model has not been clinically validated."
        ),
        "decision_support_only": True,
        "clinical_validation_status": "not_clinically_validated",
    }
