# Production readiness runbook


## Risk decision support

Risk assessment endpoints return `503` until `RISK_RULES_CLINICALLY_APPROVED=true` is set. The current thresholds and escalation behavior require written approval from the Ghana clinical governance team, with an approver, date, reviewed rule version, and review evidence recorded before enabling this setting. This repository does not grant that clinical approval.


## Existing Firestore records

1. Take and verify a Firestore export/backup.
2. Build a CSV containing `patient_id,facility_id` for every legacy patient whose facility is known from an authoritative source.
3. Configure Firebase credentials and project ID for the intended project.
4. Run `python -m scripts.migrate_facilities --mapping facility_mapping.csv` and review the per-collection totals.
5. Correct the mapping and repeat the dry run until all records that should be visible to staff are accounted for. Unmapped records are deliberately skipped.
6. Run `python -m scripts.migrate_facilities --mapping facility_mapping.csv --apply` during a controlled maintenance window, then verify counts and access in the deployed environment.

The migration never overwrites a non-empty `facility_id`. It assigns patient facilities from the CSV, derives referrals/follow-ups/assessments/notifications from their linked patient, and derives audit log facilities from the actor's provisioned user profile. Staff user profiles must already have correct roles and facility assignments. Anonymous or otherwise unmapped audit entries remain admin-visible and are reported as unmapped.

## Firebase configuration

Review `firestore.rules` and `firestore.indexes.json` against the deployed app, then run `firebase deploy --only firestore:rules,firestore:indexes --project YOUR_PROJECT_ID`. The rules deny direct client access because the API uses Firebase Admin credentials. Verify the deployment in the Firebase console and run an authenticated API smoke check.


## Notifications

Set up an HTTPS SMS provider before setting `SMS_ENABLED=true`. FCM device tokens are registered by authenticated staff at `POST /api/v1/devices/token`; referral creation sends a push to registered supervisors at the same facility. Configure one scheduled worker instance to run `python -m scripts.retry_notifications` at a short interval. Do not run overlapping workers; the outbox worker is currently designed for a single active instance. Monitor pending and terminally failed notification counts and provider delivery receipts.


## Release checks

- Run `pytest -q` in the project virtual environment.
- Verify Firebase indexes and rules are deployed in the target project.
- Verify backup/restore, authentication, facility isolation, and audit retention in staging.
- Keep risk decision support disabled until clinical approval is documented.
