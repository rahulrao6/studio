import re
from typing import List
import spacy
from spacy.language import Language
from models.clause import Clause
from utils.logging import logger
from core.config import settings
from transformers import pipeline

class ClauseExtractionService:
    """
    Extracts clauses from a contract text using NLP, classifies them, and
    identifies cross-references. Implements a heuristic approach with semantic
    segmentation and attempts to recognize clause titles/headers.

    To alter this service:
    1. Modify the `segment_text` function to use a different segmentation algorithm.
    2. Change the `determine_clause_type` function to use a different classification model.
    3. Modify the `find_clause_references` function to use a different cross-reference identification algorithm.

    To improve the accuracy of this service:
    1. Improve the segmentation logic.
    2. Improve the clause typing logic.
    3. Improve the cross-reference identification logic.
    """
    def __init__(self):
        try:
            self.nlp: Language = spacy.load("en_core_web_lg")
            logger.info("spaCy model loaded successfully.")
        except OSError:
            logger.warning("Downloading en_core_web_lg spaCy model...")
            spacy.cli.download("en_core_web_lg")
            self.nlp: Language = spacy.load("en_core_web_lg")
            logger.info("spaCy model downloaded and loaded.")

        # Load a pre-trained transformer model for clause classification
        try:
            self.classifier = pipeline(
                "text-classification",
                model="cross-encoder/nli-distilroberta-base",  # CAUD Fine-tuned model (Example)
                tokenizer="cross-encoder/nli-distilroberta-base",
                device=0 if settings.environment != "development" else -1, # Use GPU if available
            )
            logger.info("Transformer classifier loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading transformer classifier: {e}")
            self.classifier = None

    def extract_clauses(self, text: str) -> List[Clause]:
        """
        Extracts clauses from a contract text using NLP, classifies them, and
        identifies cross-references. Implements a heuristic approach with semantic
        segmentation and attempts to recognize clause titles/headers.

        Args:
            text (str): The contract text to extract clauses from.

        Returns:
            List[Clause]: A list of Clause objects.
        """
        clauses: List[Clause] = []
        clause_id = 0
        segments = self.segment_text(text)

        for segment_text in segments:
            clause_type = self.determine_clause_type(segment_text)
            risk_score = self.calculate_risk_score(segment_text)

            clause = Clause(
                id=clause_id,
                type=clause_type,
                text=segment_text,
                precision_score=0.8,  # Placeholder
                risk_score=risk_score,
                references=self.find_clause_references(segment_text),
                party="Unknown",  # To be populated later
            )
            clauses.append(clause)
            clause_id += 1

        self.build_clause_graph(clauses)
        return clauses

    def segment_text(self, text: str) -> List[str]:
        """
        Segments the contract text into clauses using regex, spaCy, and header detection.

        Args:
            text (str): The contract text to segment.

        Returns:
            List[str]: A list of segments.
        """
        # Split by common clause delimiters (e.g., "1. ", "A. ", "(a)")
        clause_delimiters = r"\n(?:\d+\.|[A-Z]\.|[a-z]\))\s"
        segments = re.split(clause_delimiters, text)
        segments = [s.strip() for s in segments if s.strip()]

        # Further refine segmentation using spaCy to handle complex sentences and phrasing
        refined_segments: List[str] = []
        for segment in segments:
            doc = self.nlp(segment)
            for sent in doc.sents:
                refined_segments.append(sent.text.strip())

        return refined_segments

    def determine_clause_type(self, text: str) -> str:
        """
        Determines the type of a clause based on NLP and Transformer model.
        Leverages self.is_clause_header to improve accuracy.

        Args:
            text (str): The clause text to determine the type of.

        Returns:
            str: The type of the clause.
        """
        if self.is_clause_header(text):
            return "header"  # Mark as header

        if self.classifier:
            try:
                classification = self.classifier(text, truncation=True, max_length=512)
                predicted_label = classification[0]["label"]
                logger.debug(f"Clause classification: {predicted_label}")
                return predicted_label
            except Exception as e:
                logger.warning(f"Classification error: {e}.  Using rule-based fallback.")
                return self.rule_based_clause_type(text)
        else:
            return self.rule_based_clause_type(text)

    def is_clause_header(self, text: str) -> bool:
        """
        Heuristic to determine if a segment is a clause header/title.

        Args:
            text (str): The clause text to check.

        Returns:
            bool: True if the text is a clause header, False otherwise.
        """
        # Check for common header patterns: uppercase, short length, numbering
        if re.match(r"^(?:\d+\.|[A-Z]\.|[a-z]\))", text):
            return True
        if len(text.split()) <= 5 and text.upper() == text:
            return True
        return False

    def rule_based_clause_type(self, text: str) -> str:
        """Fallback rule-based clause typing."""
        text = text.lower()
        if "shall" in text:
            return "obligation"
        elif "may" in text:
            return "right"
        elif "definition" in text or "means" in text:
            return "definition"
        elif "warranty" in text:
            return "warranty"
        elif "indemnify" in text:
            return "indemnity"
        elif "limitation of liability" in text:
            return "limitation"
        elif "governing law" in text:
            return "governing_law"
        elif "dispute resolution" in text:
            return "dispute_resolution"
        elif "force majeure" in text:
            return "force_majeure"
        elif "assignment" in text:
            return "assignment"
        elif "confidentiality" in text:
            return "confidentiality"
        elif "intellectual property" in text or "ip license" in text:
            return "ip_license"
        elif "termination" in text:
            return "termination"
        elif "renewal" in text:
            return "renewal"
        elif "exclusivity" in text:
            return "exclusivity"
        elif "non-compete" in text:
            return "non_compete"
        else:
            return "unknown"

    def calculate_risk_score(self, text: str) -> float:
        """Calculates a risk score (Placeholder - replace with ML model)."""
        text = text.lower()
        score = 0.0
        if "liability" in text:
            score += 0.3
        if "terminate" in text:
            score += 0.2
        if "exclusive" in text:
            score += 0.2
        return min(score, 1.0)

    def find_clause_references(self, text: str) -> List[str]:
        """Identifies cross-references to other clauses (e.g., "See Section 5.2")."""
        references = []
        for match in re.finditer(r"(?:Section|Clause)\s+(\d+(?:\.\d+)?(?:[a-z]+)?)", text):
            references.append(match.group(1))
        return references

    def build_clause_graph(self, clauses: List[Clause]) -> None:
        """Builds a clause graph by identifying cross-references."""
        for clause in clauses:
            for ref in clause.references:
                try:
                    # Naive matching - improve with more sophisticated methods
                    referenced_clause = next(
                        c for c in clauses if str(c.id + 1) == ref
                    )  # Changed to ID + 1 since clause IDs start at 0
                    if referenced_clause:
                        clause.references.append(str(referenced_clause.id))  # Store IDs
                except StopIteration:
                    logger.warning(f"Reference to clause {ref} not found.")
                    continue
