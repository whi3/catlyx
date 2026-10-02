# Maternal Risk Classifier: Initial Model Card

## Model

- **Version:** `maternal-rf-c9b2b0ecb5c2`
- **Algorithm:** Random forest classifier
- **Task:** Predict the dataset's `RiskLevel` class from six maternal measurements
- **Status:** Research prototype; not clinically validated

## Training data

The first artifact used UCI dataset 863, *Maternal Health Risk*, licensed CC BY 4.0. The fetched snapshot had 1,014 rows, 416 unique measurement profiles, and 35 profiles with conflicting risk labels. The UCI page currently lists 1,013 instances, so reconcile this one-row metadata/snapshot discrepancy before describing the data count in the final report. Dataset citation: Ahmed, M. (2020), https://doi.org/10.24432/C5DP5D.

Features and units: age (years), systolic and diastolic blood pressure (mmHg), blood sugar (mmol/L), body temperature (°F), and heart rate (beats/minute). Target classes are Low, Mid, and High Risk.

## Evaluation

Evaluation used five-fold `StratifiedGroupKFold`, grouping identical feature profiles so exact duplicate rows could not appear in both train and validation folds.

| Metric | Result |
| --- | ---: |
| Accuracy | 0.654 |
| Macro F1 | 0.635 |
| Balanced accuracy | 0.652 |

| Class | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Low Risk | 0.636 | 0.825 | 0.718 |
| Mid Risk | 0.543 | 0.318 | 0.402 |
| High Risk | 0.762 | 0.813 | 0.786 |

The low Mid Risk recall is a major limitation: the grouped validation confused 176 of 336 Mid Risk records with Low Risk. The model must not be used as an autonomous triage decision.

## Intended use and limits

This prototype supports a student project exploring maternal risk classification and comparison with a frontline worker's independent, pre-prediction label. It does not establish clinical risk, predict a verified health outcome, or provide treatment advice. Labels in the source dataset are the target being learned; performance on that target is not proof of clinical accuracy. The source population was in Bangladesh, and no Ghanaian external validation has been performed.

Worker labels are captured separately from model predictions and outcomes. Add them to training only after review, de-identification, and a new versioned evaluation. NLP is outside this model version.