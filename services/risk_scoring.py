from typing import List, Dict
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

        compliance_score = self.calculate_compliance_score(overall_score)
        suggestions = self.generate_suggestions(clauses, overall_score)

        return RiskReport(
            clause_risks=clause_risks,
            overall_score=overall_score,
            compliance_score=compliance_score,
            suggestions=suggestions,
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

        score = min(score, 1.0)  # Cap the score

        return {"score": score, "factors": risk_factors}

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
