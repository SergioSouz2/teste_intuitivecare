from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Operadora(Base):
    __tablename__ = "operadoras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registro_operadora = Column(Integer, unique=True, nullable=False)
    cnpj = Column(String(14), nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    modalidade = Column(String(100))
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    cep = Column(String(8))
    ddd = Column(String(3))
    telefone = Column(String(20))
    fax = Column(String(20))
    endereco_eletronico = Column(String(255))
    representante = Column(String(255))
    cargo_representante = Column(String(100))
    regiao_de_comercializacao = Column(Integer)
    data_registro_ans = Column(Date)
    despesas_agregadas = relationship(
        "DespesasAgregadas",
        back_populates="operadora",
        cascade="all, delete-orphan"
    )

    despesas = relationship("DespesaConsolidada", back_populates="operadora")
