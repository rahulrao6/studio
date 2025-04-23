from pydantic import BaseModel

class Obligation(BaseModel):
    party: str
    action: str
    condition: str
    due_date: str