from pydantic import BaseModel

class Right(BaseModel):
    party: str
    action: str
    condition: str
    due_date: str