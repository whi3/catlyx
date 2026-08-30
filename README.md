# 🏥 **CatalystCare** — *Transforming Health at the Last Mile*

> **An offline-first AI-powered health decision support system that brings clinical intelligence to frontline health workers in underserved communities.**

```
                      🌍 Offline First
                      
    ╔════════════════════════════════════════╗
    ║   CHPS Worker (No Internet)            ║
    ║   ├── Register Mother/Child             ║
    ║   ├── Conduct Health Assessment        ║
    ║   ├── Get AI Risk Analysis              ║
    ║   ├── Create Smart Referrals            ║
    ║   └── Track Outcomes                    ║
    ╚═══════════╤════════════════════════════╝
                │
                │ [When Connected]
                ▼
    ┌─────────────────────────────────────────┐
    │   Cloud Firestore (Sync & Archive)      │
    │   • Aggregate Health Data                │
    │   • Analytics & Insights                 │
    │   • SMS Notifications                    │
    └─────────────────────────────────────────┘
```

---

## 🎯 **What Problem Does CatalystCare Solve?**

Imagine a dedicated CHPS worker in a rural village. She has no internet, pen-and-paper records, and a village where maternal and child mortality is tragically high.

**The Problem:**
- 📋 Paper records get lost or damaged
- 🤔 Difficulty identifying truly high-risk patients
- ❌ No referral tracking — did the patient reach the facility?
- 📞 No way to remind patients about follow-ups
- 🔒 Patient data scattered and unprotected
- 🌐 Everything stops when there's no internet

**CatalystCare's Answer:**
A digital system that *works offline*, *learns from observations*, *predicts risk*, and *stays synchronized* when connectivity returns. It transforms CHPS workers from record-keepers into decision-makers.

---

## ✨ **Key Features**

### 🚀 **1. Offline-First Architecture**
- Works seamlessly without internet
- Local data storage on mobile device
- Automatic synchronization when connected
- Never loses critical patient information

### 🔍 **2. Intelligent Risk Assessment**
- AI-powered risk scoring engine
- Separate algorithms for mothers and under-five children
- Real-time analysis of health observations
- Clear, actionable risk classifications: **LOW** → **MEDIUM** → **HIGH** → **CRITICAL**

### 🎯 **3. Smart Referral System**
```
HIGH-RISK ASSESSMENT
        ↓
  AI DECISION
        ↓
 AUTO-REFERRAL
        ↓
   SMS ALERT
        ↓
 FACILITY RECEIVES
        ↓
  STATUS TRACKED
        ↓
 OUTCOME RECORDED
```

### 📱 **4. Follow-up Management**
- Automated follow-up scheduling
- Overdue alert detection
- Outcome recording
- Complete patient journey tracking

### 💬 **5. SMS Notifications**
- Referral alerts to health facilities
- Follow-up reminders to patients
- Status updates to health workers
- Two-way communication channel

### 📊 **6. Real-Time Dashboard**
- High-risk patient alerts
- Referral completion metrics
- Follow-up compliance tracking
- Worker productivity insights

### 🔐 **7. Enterprise Security**
- Firebase authentication (OAuth, phone, email)
- Role-based access control
- End-to-end encrypted data
- Audit logging of all actions

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Native Mobile App                      │
│  (Offline-First Patient Management & Assessment)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │ (REST API over HTTP/HTTPS)
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend Server                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Patient Management   │ Risk Engines │  Referral Logic   │   │
│  │ - Registration       │ - Maternal   │  - Creation       │   │
│  │ - Records            │ - Child      │  - Tracking       │   │
│  │ - History            │ - Scoring    │  - Status Update  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Authentication │ Notifications │ Sync Engine │ Analytics │   │
│  │ - Firebase     │ - SMS Alerts   │ - Offline  │ - Dashboard  │
│  │ - JWT Tokens   │ - Reminders    │ - Conflict │ - Reports    │
│  │ - RBAC         │ - Status       │ - Merging  │ - Trends     │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ┌────────────┐   ┌────────────┐   ┌──────────────┐
    │ Firestore  │   │ SMS API    │   │ Analytics    │
    │ (Database) │   │ (Twilio)   │   │ (BigQuery)   │
    └────────────┘   └────────────┘   └──────────────┘
```

---

## 📚 **Technology Stack**

| Component | Technology | Why? |
|-----------|-----------|------|
| **Backend** | FastAPI (Python) | Fast, modern, excellent async support |
| **Database** | Google Cloud Firestore | Scales, offline sync, real-time |
| **Auth** | Firebase Authentication | Secure, free, mobile-friendly |
| **Mobile** | React Native | Cross-platform (iOS/Android) |
| **Communication** | SMS + REST API | Works in low connectivity zones |
| **Deployment** | Google Cloud Run | Serverless, cost-effective, scalable |

---

## 🚀 **Getting Started**

### Prerequisites
- Python 3.9+
- Firebase project (free tier works!)
- Git
- Virtual environment (`venv`)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/whi3/catlyx.git
cd catlyx

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup Firebase credentials
# Download serviceAccountKey.json from Firebase Console
# Place in project root (DO NOT COMMIT!)

# 5. Configure environment
cp .env.example .env
# Edit .env with your Firebase credentials and settings

# 6. Start development server
uvicorn main:app --reload

# 7. Access API documentation
# Browser: http://localhost:8000/docs
```

---

## 📖 **API Overview**

### Patient Management
```
POST   /api/v1/patients/mothers         # Register mother
POST   /api/v1/patients/children        # Register child
GET    /api/v1/patients/                # List patients
GET    /api/v1/patients/{id}            # Get patient details
PUT    /api/v1/patients/{id}            # Update patient
```

### Risk Assessment
```
POST   /api/v1/risk-assessment/         # Conduct assessment & get risk
GET    /api/v1/patients/{id}/risk       # Get current risk
GET    /api/v1/patients/{id}/assessments # Get assessment history
```

### Referral Management
```
POST   /api/v1/referrals/               # Create referral
GET    /api/v1/referrals/{id}           # Get referral details
PUT    /api/v1/referrals/{id}/status    # Update referral status
POST   /api/v1/referrals/{id}/followup  # Record follow-up
```

### Sync & Dashboard
```
POST   /api/v1/sync/patients            # Sync offline changes
GET    /api/v1/dashboard/               # Get dashboard metrics
```

---

## 🎓 **Core Concepts**

### **Patient-Centric Workflow**

Every interaction starts with a **patient**:

```
1️⃣  REGISTER
    Mother or Child enters the system
        ↓
2️⃣  ASSESS
    CHPS worker conducts health assessment
        ↓
3️⃣  ANALYZE
    AI engine calculates risk level + factors
        ↓
4️⃣  DECIDE
    Worker reviews risk and decides:
    • Monitor at home (LOW/MEDIUM risk)
    • Refer to facility (HIGH/CRITICAL risk)
        ↓
5️⃣  TRACK
    System tracks referral status + follow-ups
        ↓
6️⃣  CLOSE
    Record outcome and next steps
```

### **Risk Levels Explained**

| Level | Color | Action | Example |
|-------|-------|--------|---------|
| **LOW** | 🟢 Green | Continue routine care | Healthy baby, normal vitals |
| **MEDIUM** | 🟡 Yellow | Increased monitoring | Mild malnutrition, cough |
| **HIGH** | 🔴 Red | Refer to clinic | Severe malnutrition, high fever |
| **CRITICAL** | 🟣 Purple | Urgent referral | Severe bleeding, seizures |

### **Offline Synchronization**

```
SCENARIO: Worker with no internet

TIME 0:00  Worker registers patient (offline)
           ✓ Saved to local database
           ⏳ Marked "pending sync"

TIME 0:15  Worker conducts assessment (offline)
           ✓ Saved locally
           ⏳ Marked "pending sync"

TIME 1:00  Worker connects to internet
           🔄 Sync engine detects changes
           🔄 Uploads patient + assessment
           ✓ Cloud database updated
           ✓ Marked "synced"
           
RESULT:    No data lost, perfect continuity!
```

---

## 🧪 **Testing & Quality**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Test specific module
pytest tests/test_risk_engine.py -v

# Load test the API
artillery run load-test.yml
```

---

## 📊 **Dashboard Insights**

Once deployed, CatalystCare provides:

📈 **Metrics You'll See:**
- Total patients registered (mothers + children)
- High-risk patients requiring intervention
- Referrals created vs. completed
- Follow-up compliance rates
- SMS delivery success rates
- Average response time to referrals
- CHPS worker productivity

---

## 🤝 **Contributing**

We welcome contributions! To get involved:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-thing`)
3. **Make your changes** and test thoroughly
4. **Write/update tests** to maintain coverage
5. **Submit a Pull Request** with clear description
6. **Reference related issues** using `#issue-number`

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed implementation roadmap.

---

## 📋 **Project Roadmap**

### Phase 1-4: ✅ Complete
- ✅ Backend foundation
- ✅ Patient management
- ✅ Risk assessment engine
- ✅ Referral system

### Phase 5-7: 🚀 In Progress
- 🚀 Follow-up tracking
- 🚀 SMS notifications
- 🚀 Offline architecture

### Phase 8-10: 📋 Planned
- 📋 Security hardening
- 📋 Dashboard & analytics
- 📋 Testing & deployment

---

## 🔐 **Security**

CatalystCare takes security seriously:

- ✅ **Authentication**: Firebase (industry-standard)
- ✅ **Encryption**: TLS/HTTPS for all data in transit
- ✅ **Authorization**: Role-based access control (RBAC)
- ✅ **Data Protection**: Patient data encrypted at rest
- ✅ **Audit Logs**: Complete action history for compliance
- ✅ **Secure Defaults**: Never log sensitive patient data

---

## 📞 **Support & Documentation**

- 📚 **Full Documentation**: [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/whi3/catlyx/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/whi3/catlyx/discussions)
- 📧 **Contact**: [Open issue with tag `question`]

---

## 📄 **License**

This project is open source and available under the MIT License.

---

## 🙏 **Acknowledgments**

CatalystCare is built with ❤️ for CHPS workers and the communities they serve.

Inspired by the real-world challenges of maternal and child health in underserved regions.

---

## 🌟 **The Vision**

> *A world where every child receives the healthcare they deserve, and every health worker has the tools they need to make life-saving decisions — regardless of internet connectivity.*

**CatalystCare: Delivering Healthcare Intelligence to Every Corner** 🌍

---

<div align="center">

**[📖 Full Documentation](BUILD_GUIDE.md)** • **[🐛 Report Bug](https://github.com/whi3/catlyx/issues)** • **[💡 Request Feature](https://github.com/whi3/catlyx/issues)**

⭐ If CatalystCare helps you build better health systems, please star this repository!

</div>
