CatalystCare — SRS

Software Requirements Specification

CatalystCare

Offline-First Digital Health and Referral Support System for CHPS Workers

Team: CatalystX
Backend: FastAPI
Database: Cloud Firestore
Authentication: Firebase Authentication
Client: React Native
Communication: SMS
Architecture: Offline-first


---

1. Introduction

CatalystCare is an offline-first digital health support application designed to assist frontline CHPS workers in managing maternal and under-five health information in communities where internet connectivity may be unreliable.

The system provides structured digital patient records, health assessments, risk assessment, referral management, referral tracking, and follow-up management.

The application is designed to support, rather than replace, healthcare professionals. Its risk assessment functionality provides decision support based on defined screening criteria and does not constitute medical diagnosis.


---

2. Problem Statement

Maternal, newborn, and under-five healthcare delivery in underserved communities can be affected by fragmented records, manual record keeping, difficulty identifying potentially high-risk cases, weak referral coordination, missed follow-ups, and unreliable internet connectivity.

Paper-based or disconnected records can make it difficult for CHPS workers to access relevant patient information and maintain continuity of care.

CatalystCare addresses these operational challenges by providing a structured digital record and referral-support workflow that can continue operating when connectivity is unavailable and synchronize information when connectivity is restored.


---

3. Aim

The aim of CatalystCare is to provide an offline-first digital platform that assists CHPS workers in managing maternal and under-five patient records, conducting structured risk assessments, managing referrals, and monitoring follow-up activities in low-connectivity environments.


---

4. Objectives

CatalystCare will:

1. Provide digital registration and management of maternal and under-five patient records.


2. Provide structured health assessment forms.


3. Assist CHPS workers in identifying potentially high-risk cases.


4. Provide clear reasons for risk classifications.


5. Allow health workers to create and manage referrals.


6. Track referral status.


7. Support follow-up activities.


8. Provide SMS notifications where network connectivity is available.


9. Support offline operation.


10. Synchronize locally stored records with Cloud Firestore when connectivity is restored.


11. Protect sensitive patient information through appropriate authentication and access controls.




---

5. Scope

CatalystCare covers:

Mother registration

Child registration

Patient record management

Health assessments

Risk assessment

Referral creation

Referral tracking

Follow-up management

SMS notifications

Offline data storage

Cloud synchronization

CHPS worker authentication

Dashboard and basic monitoring


The system does not diagnose diseases or replace qualified healthcare professionals.


---

6. Users

CHPS Worker

The primary user.

The CHPS worker can:

Register patients

View patient records

Conduct assessments

Review risk assessments

Create referrals

Track referrals

Record follow-ups


System Administrator

The administrator can manage:

CHPS worker accounts

System configuration

Basic monitoring

Authorized access



---

7. Core Workflow

This is the most important part of Catlyx.

CHPS Worker
     │
     ▼
Register Mother / Child
     │
     ▼
Patient Record
     │
     ▼
Health Assessment
     │
     ▼
Risk Assessment
     │
     ▼
Risk Level + Reasons
     │
     ├───────────────┐
     ▼               ▼
 Monitor           Refer
                     │
                     ▼
             Referral Created
                     │
                     ▼
              SMS Notification
                     │
                     ▼
              Referral Tracking
                     │
                     ▼
                 Follow-up
                     │
                     ▼
               Update Record



---

8. Functional Requirements

FR1 — Authentication

The system shall allow authorized CHPS workers to authenticate securely.

FR2 — Mother Registration

The system shall allow CHPS workers to register maternal patients.

FR3 — Child Registration

The system shall allow CHPS workers to register children under five.

FR4 — Patient Records

The system shall allow authorized users to view and update patient information.

FR5 — Health Assessment

The system shall allow users to enter relevant maternal and child health observations.

FR6 — Risk Assessment

The system shall analyze assessment information and provide:

Risk level

Risk score where applicable

Contributing factors

Recommended next action


FR7 — Referral Management

The system shall allow users to:

Create referrals

Specify referral destination

Record referral reason

Record referral date

Update referral status


FR8 — Referral Tracking

The system shall allow CHPS workers to monitor pending and completed referrals.

FR9 — Follow-up

The system shall allow users to record follow-up activities and outcomes.

FR10 — SMS

The system shall support SMS notifications for relevant referral and follow-up events when network connectivity and the configured SMS service are available.

FR11 — Offline Operation

The application shall allow core workflows to continue without an active internet connection.

FR12 — Synchronization

The application shall synchronize locally stored information with Cloud Firestore when connectivity becomes available.


---

9. Non-Functional Requirements

CatalystCare is designed to be:

Simple to use

Responsive

Secure

Reliable

Offline-capable

Resource-efficient

Suitable for Android smartphones

Designed for low digital literacy

Capable of synchronization after connectivity restoration



---

10. Data Architecture
Will use Cloud Firestore.

Conceptually:

Firestore
│
├── users/
│
├── patients/
│   ├── mothers
│   └── children
│
├── assessments/
│
├── referrals/
│
└── followups/

Mobile application will also maintain an appropriate local offline data layer.

catlx important principle is:

INTERNET AVAILABLE
                     │
                     ▼
             Cloud Firestore
                     ▲
                     │
                Synchronize
                     │
                     ▼
              Local Database
                     ▲
                     │
             Mobile Application

When offline:

Mobile App
    │
    ▼
Local Database
    │
    ▼
Continue working

When connectivity returns:

Local Database
      │
      ▼
Sync Engine
      │
      ▼
Cloud Firestore


---

11. CatalystCare Build Guide


Phase 1 — Backend Foundation

01. Project setup
02. requirements.txt
03. .gitignore
04. .env
05. configuration
06. Firebase initialization
07. FastAPI application
08. API router
09. health endpoint


---

Phase 2 — Patient Management

10. Base patient schema
11. Mother schema
12. Child schema
13. Patient service
14. Mother registration
15. Child registration
16. Firestore persistence
17. Patient retrieval
18. Patient update

The resulting API will eventually look approximately like:

POST   /api/v1/patients/mothers
POST   /api/v1/patients/children

GET    /api/v1/patients/{patient_id}
PUT    /api/v1/patients/{patient_id}


---

Phase 3 — Assessment:

19. Assessment schema
20. Assessment service
21. Risk engine
22. Assessment endpoint
23. Save assessment
24. Retrieve assessment history


---

Phase 4 — Referral:

25. Referral schema
26. Referral service
27. Create referral endpoint
28. Referral status
29. Referral history
30. Referral tracking

Workflow:

High-risk assessment
       ↓
Referral
       ↓
Facility
       ↓
Status


---

Phase 5 — Follow-up:

31. Follow-up schema
32. Follow-up service
33. Follow-up endpoint
34. Pending follow-ups
35. Overdue follow-ups
36. Follow-up history


---

Phase 6 — SMS


---

Phase 7 — Offline Architecture

This is primarily a React Native/mobile responsibility,Also the FastAPI backend support synchronization.

design:

Mobile
   │
   ├── Online → API → Firestore
   │
   └── Offline → Local DB
                     │
                     ▼
                  Sync Queue
                     │
                     ▼
                  API



---

Phase 8 — Security

We'll implement:

Firebase Authentication
          ↓
Firebase ID Token
          ↓
FastAPI
          ↓
Token Verification
          ↓
Authorized endpoint

And Firestore security rules will also be considered.


---

Phase 9 — Dashboard

Finally:

Dashboard
│
├── Total patients
├── Mothers
├── Children
├── High-risk cases
├── Pending referrals
├── Completed referrals
└── Pending follow-ups


---

Phase 10 — Testing

We'll test:

Backend

Schema validation

Authentication

Patient registration

Assessment

Risk engine

Referrals

Follow-ups

SMS

Error handling


Offline

Create record offline

Modify record offline

Reconnect

Synchronize

Handle duplicate/conflicting changes



12. Technology Stack

For CatalystCare, I would freeze the stack as:

Component	Technology

Mobile	React Native
Backend	FastAPI
Language	Python
Authentication	Firebase Authentication
Cloud database	Cloud Firestore
Offline storage	React Native local database/storage layer
SMS	SMS provider
API communication	REST
AI/risk engine	Python
Deployment	To be determined
Version control	Git/GitHub