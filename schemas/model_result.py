from pydantic import BaseModel
from typing import Dict


class ModelResult(BaseModel):
    model: str
    prediction: str
    probabilities: Dict[str, float]
    confidence: float