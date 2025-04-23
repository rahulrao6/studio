from typing import List, Dict
from pydantic import BaseModel

class RiskReport(BaseModel):
    clause_risks: List[Dict]
    overall_score: float
    compliance_score: float
    suggestions: List[str]