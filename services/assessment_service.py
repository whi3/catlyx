import uuid

from ai.engine import assess_risk
from core.firebase import db
from schemas.assessment import AssessmentCreate
from schemas.risk import RiskAssessmentRequest
 
COLLECTION = "assessment"