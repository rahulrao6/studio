from typing import List, Tuple
from models.clause import Clause
from models.obligation import Obligation
from models.right import Right


class ObligationMappingService:
    def map_obligations(self, clauses: List[Clause]) -> Tuple[List[Obligation], List[Right]]:
        """
        Maps obligations and rights from a list of clauses.

        Args:
            clauses: A list of Clause objects.

        Returns:
            A tuple containing two lists:
            - A list of Obligation objects.
            - A list of Right objects.
        """
        obligations: List[Obligation] = []
        rights: List[Right] = []

        for clause in clauses:
            if clause.type == "obligation":
                # Basic example: Extract party, action, condition from clause text.
                # In a real-world scenario, this would involve more advanced NLP.
                party = "Party A"  # Placeholder, needs to be extracted
                action = "Perform X"  # Placeholder
                condition = "If Y occurs"  # Placeholder
                due_date = "Date"  # Placeholder
                obligation = Obligation(
                    party=party, action=action, condition=condition, due_date=due_date
                )
                obligations.append(obligation)
            elif clause.type == "right":
                # Similar logic for rights.
                party = "Party B"  # Placeholder
                action = "Receive Z"  # Placeholder
                condition = "If W occurs"  # Placeholder
                due_date = "Date"  # Placeholder
                right = Right(
                    party=party, action=action, condition=condition, due_date=due_date
                )
                rights.append(right)

        return obligations, rights