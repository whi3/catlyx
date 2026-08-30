# 🚀 CatalystCare Build Guide - Step-by-Step Task Instructions

> **Your Complete Roadmap to Building an Offline-First Health Decision Support System**

---

## 📋 Table of Contents

- [Phase 1: Backend Foundation](#phase-1-backend-foundation)
- [Phase 2: Patient Management](#phase-2-patient-management)
- [Phase 3: Health Assessment & Risk Engine](#phase-3-health-assessment--risk-engine)
- [Phase 4: Referral Management](#phase-4-referral-management)
- [Phase 5: Follow-up Tracking](#phase-5-follow-up-tracking)
- [Phase 6: SMS Notifications](#phase-6-sms-notifications)
- [Phase 7: Offline Architecture](#phase-7-offline-architecture)
- [Phase 8: Security & Authentication](#phase-8-security--authentication)
- [Phase 9: Dashboard & Analytics](#phase-9-dashboard--analytics)
- [Phase 10: Testing & Deployment](#phase-10-testing--deployment)

---

## Phase 1: Backend Foundation

**Goal**: Set up the FastAPI project structure and Firebase integration.

### Task 1.1: Project Setup
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment
- [ ] Initialize git repository
- [ ] Create project directory structure

### Task 1.2: Dependencies
- [ ] Update `requirements.txt` with all dependencies (already done ✓)
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify installations: `pip list`

### Task 1.3: Environment Configuration
- [ ] Create `.env` file with:
  - `APP_NAME=CatalystCare API`
  - `APP_VERSION=1.0.0`
  - `DEBUG=True` (for development)
  - `SMS_ENABLED=False` (initially)
  - `FIREBASE_CREDENTIALS=serviceAccountKey.json`
- [ ] Create `.gitignore` (already exists ✓)
- [ ] Ensure `.env` is in `.gitignore`

### Task 1.4: Firebase Setup
- [ ] Download Firebase service account key from Firebase Console
- [ ] Save as `serviceAccountKey.json` in project root
- [ ] **CRITICAL**: Add to `.gitignore` (never commit credentials)
- [ ] Initialize Firebase in `core/firebase.py` (already done ✓)
- [ ] Test Firebase connection with test script

### Task 1.5: FastAPI Application
- [ ] `main.py` imports and initializes FastAPI app (already done ✓)
- [ ] Create root endpoint `GET /` returning welcome message (already done ✓)
- [ ] Test startup: `uvicorn main:app --reload`
- [ ] Verify API docs at `http://localhost:8000/docs`

### Task 1.6: API Router Structure
- [ ] Create `api/router.py` to aggregate all route modules (already done ✓)
- [ ] Import all sub-routers from `api/routes/`
- [ ] Expose main `api_router` with prefix `/api/v1`

### Task 1.7: Health Check Endpoint
- [ ] Create `api/routes/health.py` with `GET /health/` (already done ✓)
- [ ] Return system status and timestamp
- [ ] Use for monitoring and startup verification

**Checkpoint**: Application starts without errors and `/docs` shows API structure.

---

## Phase 2: Patient Management

**Goal**: Implement core patient registration and CRUD operations.

### Task 2.1: Patient Schema
- [ ] Create base `Patient` schema in `schemas/patient.py` (already done ✓)
- [ ] Include fields: `id`, `name`, `phone`, `created_at`, `updated_at`
- [ ] Add validation rules and required fields

### Task 2.2: Mother Schema
- [ ] Create `Mother` schema in `schemas/mother.py` (already done ✓)
- [ ] Extend Patient with mother-specific fields:
  - `date_of_birth`, `gestational_age`, `parity`, `pregnancy_status`
- [ ] Add risk flag fields

### Task 2.3: Child Schema
- [ ] Create `Child` schema in `schemas/child.py` (already done ✓)
- [ ] Extend Patient with child-specific fields:
  - `date_of_birth`, `weight`, `height`, `mother_id`
- [ ] Add age calculation methods

### Task 2.4: Patient Service Layer
- [ ] Create `services/patient_service.py` (already done ✓)
- [ ] Implement functions:
  - `register_mother()` - Create and save mother record
  - `register_child()` - Create and save child record
  - `get_patient_by_id()` - Retrieve patient from Firestore
  - `update_patient()` - Update patient information
  - `list_patients()` - Get all patients with pagination

### Task 2.5: Patient Endpoints
- [ ] Create `api/routes/patient.py` with endpoints (already done ✓):
  - `POST /api/v1/patients/mothers` - Register mother
  - `POST /api/v1/patients/children` - Register child
  - `GET /api/v1/patients/` - List all patients
  - `GET /api/v1/patients/{patient_id}` - Get patient details
  - `PUT /api/v1/patients/{patient_id}` - Update patient
- [ ] Add request/response validation
- [ ] Implement error handling

### Task 2.6: Firestore Integration
- [ ] Create Firestore collections: `patients`
- [ ] Implement document ID generation (UUID)
- [ ] Add timestamp fields (`created_at`, `updated_at`)
- [ ] Test write operations to Firestore

### Task 2.7: Patient Retrieval
- [ ] Implement query by ID
- [ ] Implement query by phone number
- [ ] Add filtering capabilities
- [ ] Test read operations from Firestore

### Task 2.8: Patient Updates
- [ ] Implement partial updates (PATCH semantics)
- [ ] Validate update payloads
- [ ] Update `updated_at` timestamp
- [ ] Maintain audit trail

**Checkpoint**: Can register mothers/children, retrieve, and update records via API.

---

## Phase 3: Health Assessment & Risk Engine

**Goal**: Implement structured assessments and AI-powered risk evaluation.

### Task 3.1: Assessment Schema
- [ ] Create `schemas/assessment.py` (already done ✓)
- [ ] Include fields:
  - `patient_id`, `assessment_type`, `date`, `observations`, `notes`
  - `vital_signs` (if applicable)
  - `clinical_findings`

### Task 3.2: Risk Schemas
- [ ] Create `schemas/risk.py` base risk schema (already done ✓)
- [ ] Create `schemas/mother_risk.py` for maternal risk (already done ✓)
- [ ] Create `schemas/child_risk.py` for child risk (already done ✓)
- [ ] Include fields: `risk_level`, `risk_score`, `factors`, `recommendations`

### Task 3.3: Risk Assessment Service
- [ ] Create `services/risk_service.py` (already done ✓)
- [ ] Implement risk classification logic
- [ ] Support multiple risk levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- [ ] Return risk score and contributing factors

### Task 3.4: Risk Engine - Base
- [ ] Create `ai/engine.py` with base risk assessment logic (already done ✓)
- [ ] Define assessment criteria
- [ ] Implement scoring algorithms
- [ ] Document decision rules

### Task 3.5: Risk Engine - Maternal
- [ ] Create `ai/mother_engine.py` for maternal-specific logic (already done ✓)
- [ ] Assess pregnancy complications:
  - Preeclampsia risk, gestational diabetes, bleeding
  - Infections, premature rupture of membranes
- [ ] Return specific recommendations for each risk

### Task 3.6: Risk Engine - Child
- [ ] Create `ai/child_engine.py` for child-specific logic (already done ✓)
- [ ] Assess common under-5 conditions:
  - Malnutrition, acute respiratory infection, diarrhea
  - Fever, immunization status, developmental milestones
- [ ] Return growth tracking and intervention recommendations

### Task 3.7: Assessment Service Layer
- [ ] Create `services/assessment_service.py` (already done ✓)
- [ ] Implement:
  - `create_assessment()` - Save assessment to Firestore
  - `run_risk_assessment()` - Execute risk engine
  - `get_assessment_history()` - Retrieve past assessments
  - `get_patient_risk_summary()` - Current risk status

### Task 3.8: Assessment Endpoints
- [ ] Create `api/routes/risk.py` with endpoints (already done ✓):
  - `POST /api/v1/risk-assessment/` - Create and analyze assessment
  - `GET /api/v1/patients/{patient_id}/risk` - Get current risk
  - `GET /api/v1/patients/{patient_id}/assessments` - Get assessment history
- [ ] Return comprehensive risk analysis
- [ ] Include actionable recommendations

**Checkpoint**: System can assess patients and generate risk classifications.

---

## Phase 4: Referral Management

**Goal**: Implement referral creation, tracking, and status management.

### Task 4.1: Referral Schema
- [ ] Create `schemas/referral.py` (already done ✓)
- [ ] Include fields:
  - `id`, `patient_id`, `assessment_id`, `referral_reason`
  - `destination_facility`, `referral_date`, `status`
  - `urgent`, `notes`, `created_by`

### Task 4.2: Referral Service Layer
- [ ] Create `services/referral_service.py` (already done ✓)
- [ ] Implement:
  - `create_referral()` - Initiate referral from assessment
  - `get_referral_by_id()` - Retrieve referral details
  - `update_referral_status()` - Track referral progress
  - `get_pending_referrals()` - List incomplete referrals

### Task 4.3: Referral Endpoints
- [ ] Create `api/routes/referral.py` with endpoints (already done ✓):
  - `POST /api/v1/referrals/` - Create referral
  - `GET /api/v1/referrals/{referral_id}` - Get referral details
  - `PUT /api/v1/referrals/{referral_id}/status` - Update status
  - `GET /api/v1/referrals/pending` - List pending referrals
- [ ] Validate referral workflows
- [ ] Add audit logging

### Task 4.4: Referral Status Tracking
- [ ] Define status workflow: `CREATED` → `SENT` → `RECEIVED` → `COMPLETED`
- [ ] Implement status transitions with validation
- [ ] Track status change timestamps and user
- [ ] Prevent invalid transitions

### Task 4.5: Referral History
- [ ] Store complete referral lifecycle
- [ ] Query historical referrals by patient
- [ ] Generate referral reports
- [ ] Track facility-level metrics

### Task 4.6: Firestore Referral Collection
- [ ] Create `referrals` collection
- [ ] Index on `patient_id`, `status`, `referral_date`
- [ ] Set up automatic timestamp management
- [ ] Test querying by various filters

**Checkpoint**: Can create referrals from risk assessments and track their status.

---

## Phase 5: Follow-up Tracking

**Goal**: Implement follow-up scheduling and outcome recording.

### Task 5.1: Follow-up Schema
- [ ] Create `schemas/followup.py` (already done via assessment_service)
- [ ] Include fields:
  - `id`, `referral_id`, `patient_id`, `scheduled_date`
  - `status`, `outcome`, `notes`, `completed_date`

### Task 5.2: Follow-up Service Layer
- [ ] Create `services/followup.py` (if not part of referral_service)
- [ ] Implement:
  - `schedule_followup()` - Set follow-up date
  - `get_pending_followups()` - List due follow-ups
  - `get_overdue_followups()` - Identify missed follow-ups
  - `record_followup_outcome()` - Log follow-up results

### Task 5.3: Follow-up Endpoints
- [ ] Create endpoints:
  - `POST /api/v1/referrals/{referral_id}/followup` - Schedule follow-up
  - `GET /api/v1/followups/pending` - Pending follow-ups
  - `GET /api/v1/followups/overdue` - Overdue follow-ups
  - `PUT /api/v1/followups/{followup_id}` - Record outcome
- [ ] Filter by worker, patient, facility
- [ ] Add pagination for large datasets

### Task 5.4: Follow-up Notifications
- [ ] Generate alerts for overdue follow-ups
- [ ] Track follow-up completion rates
- [ ] Generate follow-up reminders

### Task 5.5: Follow-up History
- [ ] Maintain complete follow-up record
- [ ] Query outcome patterns
- [ ] Generate follow-up reports

**Checkpoint**: Can schedule follow-ups and record outcomes on referrals.

---

## Phase 6: SMS Notifications

**Goal**: Implement SMS alerts for referral and follow-up events.

### Task 6.1: Notification Schema
- [ ] Create `schemas/notification.py` (already done ✓)
- [ ] Include: `type`, `recipient`, `message`, `status`, `sent_at`

### Task 6.2: SMS Service Layer
- [ ] Create `services/sms_service.py` (already done ✓)
- [ ] Implement SMS sending with error handling
- [ ] Support retry logic for failed sends
- [ ] Log all SMS transactions

### Task 6.3: SMS Message Templates
- [ ] Create `utils/sms_messages.py` (already done ✓)
- [ ] Define templates for:
  - Referral creation notification
  - Follow-up reminders
  - Overdue alerts
- [ ] Support message personalization

### Task 6.4: Notification Service
- [ ] Create `services/notification_service.py` (already done ✓)
- [ ] Trigger notifications on key events:
  - High-risk assessment
  - Referral created
  - Follow-up due
  - Follow-up overdue
- [ ] Queue notifications for batch sending

### Task 6.5: SMS Configuration
- [ ] Update `.env` with SMS provider details:
  - `SMS_ENABLED=True` (when ready)
  - `SMS_PROVIDER_URL`
  - `SMS_API_KEY`
  - `SMS_SENDER_ID`
- [ ] Implement provider abstraction for switching

### Task 6.6: SMS Testing
- [ ] Test with development SMS service (e.g., Twilio sandbox)
- [ ] Verify message formatting
- [ ] Test retry mechanisms
- [ ] Monitor SMS costs

**Checkpoint**: SMS notifications send successfully on key events.

---

## Phase 7: Offline Architecture

**Goal**: Support offline operation and cloud synchronization.

### Task 7.1: Offline Data Schema
- [ ] Define offline database schema (mobile responsibility)
- [ ] Match Firestore structure for sync compatibility
- [ ] Include sync metadata fields: `synced`, `sync_timestamp`, `conflict_state`

### Task 7.2: Sync Service - Backend
- [ ] Create `services/sync_service.py` (already done ✓)
- [ ] Implement `sync_offline_records()` endpoint
- [ ] Handle batch inserts and updates
- [ ] Detect and resolve conflicts

### Task 7.3: Sync Endpoints
- [ ] Create `api/routes/sync.py` endpoints (already done ✓):
  - `POST /api/v1/sync/patients` - Sync patient updates
  - `POST /api/v1/sync/assessments` - Sync assessments
  - `POST /api/v1/sync/referrals` - Sync referral changes
- [ ] Accept batch operations
- [ ] Return sync status and conflicts

### Task 7.4: Conflict Resolution
- [ ] Implement conflict detection:
  - Timestamp-based resolution
  - Last-write-wins strategy
  - Manual conflict flags
- [ ] Provide conflict metadata to client
- [ ] Allow user-guided resolution

### Task 7.5: Firestore Sync Rules
- [ ] Design sync-friendly Firestore structure
- [ ] Implement idempotent operations
- [ ] Add version/revision fields
- [ ] Support partial updates

### Task 7.6: Mobile Offline Support (React Native)
- [ ] Design local database schema (mobile task)
- [ ] Implement sync queue for pending changes
- [ ] Add connectivity detection
- [ ] Implement automatic sync on reconnection

**Checkpoint**: Backend can accept and merge offline changes; mobile app queues changes locally.

---

## Phase 8: Security & Authentication

**Goal**: Implement robust authentication and authorization.

### Task 8.1: Firebase Authentication Setup
- [ ] Configure Firebase Authentication in Firebase Console
- [ ] Enable auth providers (Email/Password or Phone)
- [ ] Create test user accounts
- [ ] Document authentication flow

### Task 8.2: Authentication Service
- [ ] Create `services/auth_service.py` (already done ✓)
- [ ] Implement token verification
- [ ] Validate Firebase ID tokens
- [ ] Handle token expiration and refresh

### Task 8.3: Authentication Middleware
- [ ] Create `core/auth.py` middleware (already done ✓)
- [ ] Extract Bearer token from Authorization header
- [ ] Verify Firebase token
- [ ] Inject user info into request context
- [ ] Return 401 for invalid tokens

### Task 8.4: Protected Endpoints
- [ ] Apply authentication to all patient/risk/referral endpoints
- [ ] Use dependency injection with FastAPI `Depends()`
- [ ] Test authentication failures
- [ ] Verify token validation

### Task 8.5: Role-Based Access Control (RBAC)
- [ ] Define roles: `CHPS_WORKER`, `ADMIN`, `SUPERVISOR`
- [ ] Implement role checking middleware
- [ ] Add role-based endpoint restrictions
- [ ] Test role authorization

### Task 8.6: Firestore Security Rules
- [ ] Write Firestore rules for collections:
  ```
  - Users can only read/write their own patient records
  - Admins can access all records
  - Historical data is immutable after grace period
  ```
- [ ] Test rules with authenticated and unauthenticated requests
- [ ] Verify data isolation

### Task 8.7: Audit Logging
- [ ] Log all authenticated requests
- [ ] Record user, endpoint, and timestamp
- [ ] Store audit logs in Firestore
- [ ] Implement audit log queries

**Checkpoint**: All endpoints require authentication; RBAC enforced; security rules protect data.

---

## Phase 9: Dashboard & Analytics

**Goal**: Provide system monitoring and health insights.

### Task 9.1: Dashboard Schema
- [ ] Define dashboard data structure
- [ ] Aggregate metrics: patient counts, risk statistics, referral status
- [ ] Design time-series data storage

### Task 9.2: Dashboard Metrics Service
- [ ] Create metrics calculation service
- [ ] Implement queries for:
  - Total patients (mothers + children)
  - High-risk patient count
  - Pending referral count
  - Completed referral count
  - Overdue follow-ups
  - SMS delivery status

### Task 9.3: Dashboard Endpoints
- [ ] Create `api/routes/dashboard.py`:
  - `GET /api/v1/dashboard/` - Main dashboard metrics
  - `GET /api/v1/dashboard/statistics` - Detailed statistics
  - `GET /api/v1/dashboard/trends` - Time-series trends
- [ ] Support date range filtering
- [ ] Optimize for quick response

### Task 9.4: Analytics Functions
- [ ] Risk distribution analysis
- [ ] Referral completion rates
- [ ] Follow-up compliance tracking
- [ ] SMS delivery metrics
- [ ] Worker performance stats

### Task 9.5: Report Generation
- [ ] Implement report templates
- [ ] Support CSV/PDF exports
- [ ] Schedule automated reports
- [ ] Email report distribution

**Checkpoint**: Dashboard displays key metrics; reports generate successfully.

---

## Phase 10: Testing & Deployment

**Goal**: Comprehensive testing and production-ready deployment.

### Task 10.1: Unit Tests
- [ ] Test schema validation:
  ```bash
  pytest tests/test_schemas.py
  ```
- [ ] Test service layer logic
- [ ] Test error conditions
- [ ] Aim for >80% code coverage

### Task 10.2: Integration Tests
- [ ] Test complete workflows:
  - Patient registration → Assessment → Risk → Referral
  - Offline sync workflow
  - Authentication flow
- [ ] Test Firestore interactions
- [ ] Test SMS integration

### Task 10.3: Endpoint Tests
- [ ] Test all API endpoints with valid/invalid data
- [ ] Test authentication requirements
- [ ] Test role-based access
- [ ] Test error responses
- [ ] Load test high-traffic endpoints

### Task 10.4: Offline Testing (Mobile)
- [ ] Test app functionality without internet
- [ ] Verify local data storage
- [ ] Test sync after reconnection
- [ ] Test conflict resolution

### Task 10.5: Security Testing
- [ ] Test authentication token validation
- [ ] Test Firestore rules
- [ ] Verify no sensitive data in logs
- [ ] Test CORS and origin validation
- [ ] Penetration test basic scenarios

### Task 10.6: Performance Optimization
- [ ] Profile slow endpoints
- [ ] Optimize Firestore queries with indexes
- [ ] Implement caching where appropriate
- [ ] Monitor database usage

### Task 10.7: Production Checklist
- [ ] [ ] Set `DEBUG=False` in production
- [ ] [ ] Use environment-specific configs
- [ ] [ ] Enable HTTPS only
- [ ] [ ] Configure CORS properly
- [ ] [ ] Set up error logging and monitoring
- [ ] [ ] Configure database backups
- [ ] [ ] Document deployment process
- [ ] [ ] Set up CI/CD pipeline

### Task 10.8: Deployment
- [ ] Choose hosting: Cloud Run, AWS Lambda, or traditional server
- [ ] Configure environment variables securely
- [ ] Deploy backend service
- [ ] Configure domain/DNS
- [ ] Set up SSL/TLS certificates
- [ ] Test production endpoints
- [ ] Monitor application health

### Task 10.9: Documentation
- [ ] Document API with OpenAPI/Swagger
- [ ] Write deployment guide
- [ ] Create troubleshooting guide
- [ ] Document database schema
- [ ] Record architecture decisions

### Task 10.10: Post-Launch
- [ ] Monitor error rates and performance
- [ ] Gather user feedback
- [ ] Plan next feature iterations
- [ ] Establish SLA and monitoring
- [ ] Train CHPS workers on system

**Checkpoint**: All tests pass, production deployment successful, monitoring active.

---

## 🎯 Success Criteria

- ✅ Backend API fully functional and tested
- ✅ All patient data flows working (registration → assessment → referral)
- ✅ Offline synchronization working
- ✅ Authentication and security enforced
- ✅ SMS notifications sending
- ✅ Dashboard providing actionable insights
- ✅ >80% code coverage
- ✅ Zero security vulnerabilities
- ✅ Response times <200ms for normal operations
- ✅ Production deployment successful

---

## 📞 Support & Troubleshooting

### Common Issues

**Firebase Connection Failed**
- Verify `serviceAccountKey.json` is valid
- Check Firebase project settings
- Confirm credentials environment variable

**Firestore Queries Slow**
- Add collection indexes in Firebase Console
- Optimize query predicates
- Consider query caching

**SMS Not Sending**
- Verify SMS provider credentials
- Check `SMS_ENABLED=True` in `.env`
- Review SMS service logs

**Offline Sync Conflicts**
- Implement conflict resolution strategy
- Use timestamps as conflict tiebreaker
- Log conflicts for manual review

---

**Last Updated**: 2026-08-30  
**Status**: ✅ In Progress  
**Current Phase**: Phase 2 ✓ → Phase 3 (Next)
