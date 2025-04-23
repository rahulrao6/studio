from typing import Dict

from pydantic import BaseModel


class Contract(BaseModel):
    id: int
    text: str
    metadata: Dict