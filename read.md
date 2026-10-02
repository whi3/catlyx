## **re analysed*


## ✅ Completed (5 features)
- **Feature 1**: Patient/Case Registration
- **Feature 2**: Field Assessment Intake  
- **Feature 4**: Referral Record Creation
- **Feature 6**: Assessment/Case History
- **Feature 10**: Follow-up/Close-out Tracking


##  Partially Implemented (4 features)
- **Feature 3**: Hybrid Risk Detection (rule engine works, ML classifier missing)
- **Feature 5**: Push Notifications (SMS works, Firebase Cloud Messaging missing)
- **Feature 7**: Role-Based Access (framework exists, enforcement missing)
- **Feature 8**: Audit Trail (logging functions exist, middleware missing)


##  Not Yet Implemented (3 features)
- **Feature 9**: Offline Queue Simulation
- **Feature 11**: Conflict Resolution
- **Feature 12**: Longitudinal Risk Trend Detection

from ucimlrepo import fetch_ucirepo 
  
# fetch dataset 
maternal_health_risk = fetch_ucirepo(id=863) 
  
# data (as pandas dataframes) 
X = maternal_health_risk.data.features 
y = maternal_health_risk.data.targets 
  
# metadata 
print(maternal_health_risk.metadata) 
  
# variable information 
print(maternal_health_risk.variables) 
