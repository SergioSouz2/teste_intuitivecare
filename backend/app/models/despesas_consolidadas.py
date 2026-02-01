from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class DespesaConsolidada(Base):
    __tablename__ = "despesas_consolidadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operadora_id = Column(UUID(as_uuid=True), ForeignKey("operadoras.id"))
    registro_ans = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    valor_despesas = Column(Numeric(20, 2), nullable=False)

    operadora = relationship("Operadora", back_populates="despesas")
