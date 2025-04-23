from typing import List, Dict, Tuple
from models.clause import Clause
from models.risk_report import RiskReport
import re
import spacy
from utils.logging import logger
from core.config import settings
from transformers import pipeline

class RiskScoringService:
    def __init__(self):
         try:
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("spaCy model loaded successfully for risk scoring.")
         except OSError:
            logger.warning("Downloading en_core_web_lg spaCy model...")
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("spaCy model downloaded and loaded for risk scoring.")
         # Load a pre-trained transformer model for risk assessment (CAUD Fine-tuned model example)
         try:
            self.risk_analyzer = pipeline(
                "text-classification",
                model="bhadresh-savani/distilbert-base-uncased-finetuned-ner",  # CAUD Fine-tuned model (Example)
                tokenizer="bhadresh-savani/distilbert-base-uncased-finetuned-ner",
                device=0 if settings.environment != "development" else -1,  # Use GPU if available
            )
            logger.info("Transformer risk analyzer loaded successfully.")
         except Exception as e:
            logger.error(f"Error loading transformer risk analyzer: {e}")
            self.risk_analyzer = None

        # Expanded risk keywords (can load from file or DB for dynamic updates)
        self.high_risk_keywords = ["sole discretion", "unilateral", "without notice", "absolute discretion", "indemnify", "hold harmless"]
        self.medium_risk_keywords = ["may", "reasonable", "commercially reasonable", "material adverse", "best efforts"]
        self.auto_renewal_patterns = [r"automatically renew", r"unless notice is given"]
        self.force_majeure_patterns = [r"act of god", r"unforeseen circumstances"]
        self.security_patterns = [r"data breach", r"cybersecurity incident"]
        self.data_privacy_patterns = [r"personal data", r"personally identifiable information", r"pii"]
        self.missing_injunctive_relief_pattern = r"injunctive relief"
        self.missing_liquidated_damages_pattern = r"liquidated damages"

    def score_clauses(self, clauses: List[Clause]) -> RiskReport:
        """Scores clauses and generates a risk report."""
        clause_risks = []
        overall_score = 0.0
        compliance_score = 0.0
        suggestions = []

        for clause in clauses:
            clause_risk = self.calculate_clause_risk(clause)
            clause_risks.append(
                {
                    "clause_id": clause.id,
                    "risk_score": clause_risk["score"],
                    "risk_factors": clause_risk["factors"],
                }
            )
            overall_score += clause_risk["score"]

        if len(clauses) > 0:
            overall_score /= len(clauses)
        else:
            overall_score = 0

        # Calibrate overall score based on contract type (NDA vs MSA)
        overall_score = self.calibrate_overall_risk_score(overall_score, "MSA")  # Assuming MSA for this example

        compliance_score = self.calculate_compliance_score(overall_score)
        suggestions = self.generate_suggestions(clauses, overall_score)

        # Prioritize key negotiation points
        negotiation_points = self.get_negotiation_points(clauses)

        return RiskReport(
            clause_risks=clause_risks,
            overall_score=overall_score,
            compliance_score=compliance_score,
            suggestions=suggestions,
            negotiation_points = negotiation_points, #add negotiation points
        )

    def calculate_clause_risk(self, clause: Clause) -> Dict:
        """Calculates the risk score for a single clause based on keywords and patterns."""
        score = 0.0
        risk_factors = []
        text = clause.text.lower()

        # Use transformer model for initial risk assessment
        if self.risk_analyzer:
            try:
                result = self.risk_analyzer(text, truncation=True, max_length=512)
                risk_label = result[0]["label"]
                risk_confidence = result[0]["score"]
                logger.debug(f"Transformer risk assessment: {risk_label} with confidence {risk_confidence}")
                if risk_label == "High Risk":
                    score += risk_confidence  # Use confidence score to adjust
                    risk_factors.append(f"Transformer: High Risk ({risk_confidence:.2f})")
                elif risk_label == "Medium Risk":
                    score += risk_confidence * 0.5
                    risk_factors.append(f"Transformer: Medium Risk ({risk_confidence:.2f})")
            except Exception as e:
                logger.warning(f"Transformer risk analysis failed: {e}. Using keyword-based analysis.")
                # Fallback to keyword-based analysis if transformer fails
                score, factors = self.keyword_based_risk(text)
                risk_factors.extend(factors)
        else:
            score, factors = self.keyword_based_risk(text)
            risk_factors.extend(factors)


        # Additional checks
        if clause.type == "indemnity":
            score += 0.4
            risk_factors.append("Clause Type: Indemnity (High Risk)")
        elif clause.type == "limitation":
            score += 0.3
            risk_factors.append("Clause Type: Limitation of Liability (Medium Risk)")

        if re.search(r"automatically renew", text):
            score += 0.3
            risk_factors.append("Auto-renewal Pattern Detected")
        if any(pattern.search(text) for pattern in self.force_majeure_patterns):
            score += 0.4
            risk_factors.append("Force Majeure Pattern Detected")
        if any(pattern.search(text) for pattern in self.security_patterns):
            score += 0.5
            risk_factors.append("Security/Data Breach Pattern Detected")
        if any(pattern.search(text) for pattern in self.data_privacy_patterns):
            score += 0.6
            risk_factors.append("Data privacy/PII risk detected")


        score = min(score, 1.0)  # Cap the score

        return {"score": score, "factors": risk_factors, "suggestions": self.generate_clause_suggestions(clause)}

    def keyword_based_risk(self, text: str) -> Tuple[float, List[str]]:
        """Calculates risk based on keyword matching."""
        score = 0.0
        factors = []
        for keyword in self.high_risk_keywords:
            if keyword in text:
                score += 0.5
                factors.append(f"Keyword: {keyword} (High Risk)")
        for keyword in self.medium_risk_keywords:
            if keyword in text:
                score += 0.2
                factors.append(f"Keyword: {keyword} (Medium Risk)")
        return score, factors

    def calculate_compliance_score(self, overall_score: float) -> float:
        """Calculates a compliance score based on the overall risk."""
        # Example: check against GDPR (simplified)
        if overall_score > 0.7 and ("personal information" in self.high_risk_keywords or "data privacy" in self.high_risk_keywords):
            return 0.4  # Low compliance if high risk and PII related
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

    def calibrate_overall_risk_score(self, score: float, contract_type: str) -> float:
        """Calibrates the overall risk score based on the contract type."""
        if contract_type == "NDA":
            score = min(20, score * 20)  # NDA - Cap at 20
        elif contract_type == "MSA":
            score = min(85, 70 + score * 15)  # MSA - Range between 70-85
        return score

    def generate_clause_suggestions(self, clause: Clause) -> List[str]:
        """Generates specific suggestions for a clause based on identified risks."""
        suggestions = []
        text = clause.text.lower()

        if "liability" in text:
            suggestions.append("Consider limiting liability to the extent permitted by law.")
        if "terminate" in text:
            suggestions.append("Ensure termination rights are balanced and clearly defined.")
        if "exclusive" in text:
            suggestions.append("Review the scope and duration of exclusivity provisions.")
        if re.search(self.missing_injunctive_relief_pattern, text) is None:
            suggestions.append("Consider adding an injunctive relief clause to protect confidential information.")
        if re.search(self.missing_liquidated_damages_pattern, text) is None:
            suggestions.append("Consider adding a liquidated damages clause to address potential breaches.")
        return suggestions

    def get_negotiation_points(self, clauses: List[Clause]) -> List[str]:
        """Prioritizes key negotiation points based on risk and other factors."""
        negotiation_points = []

        # Prioritize based on patterns first
        if any(re.search(self.missing_injunctive_relief_pattern, clause.text.lower()) is None for clause in clauses):
            negotiation_points.append("Add injunctive relief / equitable remedies")
        if any("data-return" in clause.text.lower() for clause in clauses):
            negotiation_points.append("Ensure data-return/destroy timelines are clear and reasonable")
        # Removed 'hidden' from list, and just keep it as 'removal of fees'
        if any("fee" in clause.text.lower() for clause in clauses):
            negotiation_points.append("Removal of hidden/unilateral fees")


        # Add other negotiation points based on keyword matches
        for clause in clauses:
            if "liability" in clause.text.lower() and "Consider limiting liability" not in negotiation_points:
                negotiation_points.append("Limit the Provider's Liability")
            if "termination" in clause.text.lower() and "Ensure termination rights" not in negotiation_points:
                negotiation_points.append("Balance Termination Rights for both parties")


        return negotiation_points
