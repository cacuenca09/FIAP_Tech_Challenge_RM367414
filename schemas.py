from pydantic import BaseModel
from typing import Optional, Dict

class BookSchema(BaseModel):
    id: int
    titulo: str
    preco: float
    disponibilidade: str
    rating: int
    categoria: str
    imagem: str

    class Config:
        orm_mode = True

##Desafio 2 (Pipelines de ML)
class FeatureResponse(BaseModel):
    id: int
    preco: float
    rating: float


class TrainingDataResponse(BaseModel):
    id: int
    titulo: str
    preco: float
    rating: float
    categoria: Optional[str] = None


class PredictionRequest(BaseModel):
    features: Dict[str, float]


class PredictionResponse(BaseModel):
    prediction: float