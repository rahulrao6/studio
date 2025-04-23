from typing import List, Tuple
from models.clause import Clause
from models.obligation import Obligation
from models.right import Right
import spacy
from utils.logging import logger

class ObligationMappingService:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")  # Ensure you have this model
            logger.info("spaCy model loaded successfully for obligation mapping.")
        except OSError:
            logger.warning("Downloading en_core_web_lg spaCy model...")
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("spaCy model downloaded and loaded for obligation mapping.")

    def map_obligations(self, clauses: List[Clause]) -> Tuple[List[Obligation], List[Right]]:
        """
        Maps obligations and rights from a list of clauses using NLP.
        """
        obligations: List[Obligation] = []
        rights: List[Right] = []

        for clause in clauses:
            if clause.type == "obligation":
                obligation = self.extract_obligation(clause.text)
                if obligation:
                    obligations.append(obligation)
            elif clause.type == "right":
                right = self.extract_right(clause.text)
                if right:
                    rights.append(right)

        return obligations, rights

    def extract_obligation(self, clause_text: str) -> Obligation | None:
        """
        Extracts obligation details from a clause using NLP.
        This is a placeholder and needs to be replaced with a proper information extraction model.
        """
        doc = self.nlp(clause_text)
        party = "Unknown"
        action = "Unknown"
        condition = "Unknown"
        due_date = "Unknown"

        # Example logic: looking for "shall" for obligations
        if "shall" in clause_text.lower():
            for token in doc:
                if token.dep_ == "nsubj":
                    party = token.text
                elif token.dep_ == "ROOT":
                    action = token.text
            obligation = Obligation(
                party=party, action=action, condition=condition, due_date=due_date
            )
            return obligation
        else:
            return None  # Not an obligation

    def extract_right(self, clause_text: str) -> Right | None:
        """
        Extracts right details from a clause using NLP.
        This is a placeholder and needs to be replaced with a proper information extraction model.
        """
        doc = self.nlp(clause_text)
        party = "Unknown"
        action = "Unknown"
        condition = "Unknown"
        due_date = "Unknown"

        # Example logic: looking for "may" for rights
        if "may" in clause_text.lower():
            for token in doc:
                if token.dep_ == "nsubj":
                    party = token.text
                elif token.dep_ == "ROOT":
                    action = token.text
            right = Right(party=party, action=action, condition=condition, due_date=due_date)
            return right
        else:
            return None  # Not a right
