from typing import List
from models.clause import Clause
from models.risk_report import RiskReport


class RiskScoringService:
    def __init__(self):
        pass

    def score_clauses(self, clauses: List[Clause]) -> RiskReport:
        clause_risks = []
        overall_score = 0.0
        compliance_score = 0.0
        suggestions = []

        for clause in clauses:
            # Dummy risk scoring logic
            if "liability" in clause.text.lower():
                clause.risk_score = 0.9
                suggestions.append(f"High liability risk in clause: {clause.text[:50]}...")
            elif "payment" in clause.text.lower():
                clause.risk_score = 0.7
                suggestions.append(f"Moderate payment risk in clause: {clause.text[:50]}...")
            else:
                clause.risk_score = 0.3
            
            clause_risks.append({"clause_id": clause.id, "risk_score": clause.risk_score})
            overall_score += clause.risk_score

        if len(clauses) > 0:
            overall_score /= len(clauses)
        else:
            overall_score = 0

        # Dummy compliance scoring logic
        if overall_score > 0.7:
            compliance_score = 0.4
            suggestions.append("Compliance risk identified.")
        else:
            compliance_score = 0.8

        return RiskReport(clause_risks=clause_risks, overall_score=overall_score, compliance_score=compliance_score, suggestions=suggestions)