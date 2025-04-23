from pydantic import BaseModel
from typing import List

class LegalMemo(BaseModel):
    risk_area: str
    analysis: str
    citations: List[str]