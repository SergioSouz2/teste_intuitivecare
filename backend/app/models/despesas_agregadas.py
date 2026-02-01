import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.operadora import Operadora  # importa o model corretos

class DespesasAgregadas(Base):
    __tablename__ = "despesas_agregadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operadora_id = Column(UUID(as_uuid=True), ForeignKey("operadoras.id"))
    razao_social = Column(String(255))
    uf = Column(String(20))
    total_despesas = Column(Numeric(20, 2))
    media_despesas = Column(Numeric(20, 2))
    desvio_padrao = Column(Numeric(20, 2))

    # Relacionamento com operadora
    operadora = relationship("Operadora", back_populates="despesas_agregadas")
