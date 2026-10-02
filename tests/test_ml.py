import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("sklearn")

from ml.train_maternal import prepare_dataset


def test_prepare_dataset_normalizes_risk_labels_and_feature_columns():
    frame = pd.DataFrame({
        "Age": [24, 31, 19],
        "SystolicBP": [120, 140, 110],
        "DiastolicBP": [80, 90, 70],
        "BS": [6.2, 9.1, 5.8],
        "BodyTemp": [98, 101, 97],
        "HeartRate": [78, 92, 72],
        "RiskLevel": ["low risk", "Mid Risk", "moderate risk"],
    })

    features, labels = prepare_dataset(frame)

    assert list(features.columns) == [
        "Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"
    ]
    assert labels.tolist() == ["low risk", "mid risk", "mid risk"]


def test_prepare_dataset_rejects_unrecognized_labels():
    frame = pd.DataFrame({
        "Age": [24],
        "SystolicBP": [120],
        "DiastolicBP": [80],
        "BS": [6.2],
        "BodyTemp": [98],
        "HeartRate": [78],
        "RiskLevel": ["unknown"],
    })

    with pytest.raises(ValueError, match="Unexpected risk labels"):
        prepare_dataset(frame)
