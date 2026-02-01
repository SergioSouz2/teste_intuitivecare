from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

# ---------- Operadoras ----------

class OperadoraBase(BaseModel):
    id: UUID   # 👈 muda aqui
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    uf: Optional[str]
    cidade: Optional[str]

    class Config:
        from_attributes = True

class PaginatedOperadoras(BaseModel):
    page: int
    limit: int
    total: int
    data: List[OperadoraBase]

# ---------- Despesas ----------

class DespesaBase(BaseModel):
    id: UUID
    ano: int
    trimestre: int
    valor_despesas: float

    class Config:
        from_attributes = True

# ---------- Estatísticas ----------

class EstatisticasTop(BaseModel):
    cnpj: str
    razao_social: str
    total: float

class EstatisticasResponse(BaseModel):
    total_despesas: float
    media_despesas: float
    top5_operadoras: List[EstatisticasTop]
