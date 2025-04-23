from typing import List, Dict
from models.clause import Clause
from models.risk_report import RiskReport
import re

class RiskScoringService:
    def __init__(self):
        self.high_risk_keywords = ["sole discretion", "unilateral", "without notice", "absolute discretion"]
        self.medium_risk_keywords = ["may", "reasonable", "commercially reasonable", "material adverse"]

    def score_clauses(self, clauses: List[Clause]) -> RiskReport:
        clause_risks = []
        overall_score = 0.0
        compliance_score = 0.0
        suggestions = []

        for clause in clauses:
            clause.risk_score = self.calculate_clause_risk(clause)
            clause_risks.append({"clause_id": clause.id, "risk_score": clause.risk_score})
            overall_score += clause.risk_score

        if len(clauses) > 0:
            overall_score /= len(clauses)
        else:
            overall_score = 0

        compliance_score = self.calculate_compliance_score(overall_score)
        suggestions = self.generate_suggestions(clauses, overall_score)

        return RiskReport(clause_risks=clause_risks, overall_score=overall_score, compliance_score=compliance_score, suggestions=suggestions)

    def calculate_clause_risk(self, clause: Clause) -> float:
        """Calculates the risk score for a single clause based on keywords and patterns."""
        score = 0.0
        text = clause.text.lower()

        if clause.type == "indemnity":
            score += 0.4  # Indemnity clauses are often risky
        elif clause.type == "limitation":
            score += 0.3  # Limitation of liability clauses can be significant

        for keyword in self.high_risk_keywords:
            if keyword in text:
                score += 0.5
        for keyword in self.medium_risk_keywords:
            if keyword in text:
                score += 0.2

        # Check for auto-renewal patterns (simplified)
        if re.search(r"automatically renew", text):
            score += 0.3

        # Check for data privacy/PII (very basic example)
        if "personal information" in text or "data privacy" in text:
            score += 0.4
        
        return min(score, 1.0)

    def calculate_compliance_score(self, overall_score: float) -> float:
        """Calculates a compliance score based on the overall risk."""
        # This is a very basic example; a real implementation would check against specific regulations.
        if overall_score > 0.7:
            return 0.4
        else:
            return 0.8

    def generate_suggestions(self, clauses: List[Clause], overall_score: float) -> List[str]:
        """Generates suggestions based on identified risks."""
        suggestions = []
        if overall_score > 0.6:
            suggestions.append("Consider seeking legal advice to review high-risk clauses.")
        
        for clause in clauses:
            if clause.risk_score > 0.8:
                suggestions.append(f"Review clause {clause.id} due to high-risk keywords.")
        return suggestions
