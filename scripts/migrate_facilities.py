"""Dry-run-first migration for legacy records that lack facility_id.

The supplied CSV maps patient IDs to facilities. Linked referrals, follow-ups,
risk assessments, and notifications inherit their patient's facility. Run with
--apply only after reviewing the dry-run totals and taking a Firestore backup.
"""

import argparse
import csv
import logging
from collections import Counter
from pathlib import Path

from core.firebase import db

LINKED_COLLECTIONS = ("referrals", "followups", "risk_assessments", "notifications")
logger = logging.getLogger("facility_migration")


def load_mapping(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        if not {"patient_id", "facility_id"}.issubset(rows.fieldnames or []):
            raise ValueError("CSV must contain patient_id and facility_id columns.")
        mapping = {}
        for row in rows:
            patient_id = (row.get("patient_id") or "").strip()
            facility_id = (row.get("facility_id") or "").strip()
            if not patient_id or not facility_id:
                raise ValueError("CSV rows must have non-empty patient_id and facility_id.")
            mapping[patient_id] = facility_id
    return mapping


def migrate(mapping: dict[str, str], *, apply: bool = False) -> dict[str, dict[str, int]]:
    if db is None:
        raise RuntimeError("Firebase is not configured; set credentials/project settings first.")

    totals: dict[str, Counter] = {}
    patient_facilities: dict[str, str] = {}
    patients = db.collection("patients")
    for snapshot in patients.stream():
        data = snapshot.to_dict() or {}
        patient_id = data.get("patient_id") or snapshot.id
        facility_id = data.get("facility_id") or mapping.get(patient_id)
        if not facility_id:
            totals.setdefault("patients", Counter())["unmapped"] += 1
            continue
        patient_facilities[patient_id] = facility_id
        if data.get("facility_id"):
            totals.setdefault("patients", Counter())["already_assigned"] += 1
        else:
            totals.setdefault("patients", Counter())["would_update"] += 1
            if apply:
                snapshot.reference.update({"facility_id": facility_id})

    for collection_name in LINKED_COLLECTIONS:
        counts = totals.setdefault(collection_name, Counter())
        for snapshot in db.collection(collection_name).stream():
            data = snapshot.to_dict() or {}
            if data.get("facility_id"):
                counts["already_assigned"] += 1
                continue
            facility_id = patient_facilities.get(data.get("patient_id"))
            if not facility_id:
                counts["unmapped"] += 1
                continue
            counts["would_update"] += 1
            if apply:
                snapshot.reference.update({"facility_id": facility_id})

    user_facilities = {}
    for snapshot in db.collection("users").stream():
        profile = snapshot.to_dict() or {}
        if profile.get("facility_id"):
            user_facilities[snapshot.id] = profile["facility_id"]
    audit_counts = totals.setdefault("audit_logs", Counter())
    for snapshot in db.collection("audit_logs").stream():
        data = snapshot.to_dict() or {}
        if data.get("facility_id"):
            audit_counts["already_assigned"] += 1
            continue
        facility_id = user_facilities.get(data.get("user_id"))
        if not facility_id:
            audit_counts["unmapped"] += 1
            continue
        audit_counts["would_update"] += 1
        if apply:
            snapshot.reference.update({"facility_id": facility_id})

    return {name: dict(counts) for name, counts in totals.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", required=True, type=Path, help="CSV mapping patient_id,facility_id")
    parser.add_argument("--apply", action="store_true", help="Write updates; default is a dry run")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    summary = migrate(load_mapping(args.mapping), apply=args.apply)
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"{mode}: facility migration summary")
    for collection_name, counts in sorted(summary.items()):
        print(f"{collection_name}: {counts}")
    if not args.apply:
        print("No records were changed. Review totals and take a backup before rerunning with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
