from typing import List

from pydantic import BaseModel


class Clause(BaseModel):
    id: int
    type: str
    text: str
    precision_score: float
    risk_score: float
    references: List[str]
    party: str