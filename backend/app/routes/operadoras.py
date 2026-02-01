from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
import re

from app.database import get_db
from app.models.operadora import Operadora
from app.models.despesas_consolidadas import DespesaConsolidada
from app.schemas import OperadoraBase, DespesaBase, PaginatedOperadoras

router = APIRouter()

# ======================================================
# LISTAR OPERADORAS (COM BUSCA + PAGINAÇÃO)
# ======================================================
@router.get("/", response_model=PaginatedOperadoras)
def listar_operadoras(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    razao_social: str | None = None,
    uf: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Operadora)

    if search:
        search_clean = re.sub(r"\D", "", search)
        query = query.filter(
            or_(
                Operadora.cnpj.ilike(f"%{search_clean}%"),
                Operadora.razao_social.ilike(f"%{search}%"),
            )
        )
    if razao_social:
        query = query.filter(Operadora.razao_social == razao_social)
    if uf:
        query = query.filter(Operadora.uf == uf)

    total = query.count()
    operadoras = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": [
            {
                "id": str(o.id),
                "cnpj": o.cnpj,
                "razao_social": o.razao_social,
                "nome_fantasia": o.nome_fantasia,
                "uf": o.uf,
                "cidade": o.cidade,
            }
            for o in operadoras
        ],
    }


# 🔹 Retorna todos os UFs distintos
@router.get("/ufs")
def get_ufs(db: Session = Depends(get_db)):
    resultados = db.query(Operadora.uf).distinct().all()
    return [r[0] for r in resultados]

# 🔹 Retorna todas as razões sociais distintas
@router.get("/razao_social")
def get_razao_social(db: Session = Depends(get_db)):
    resultados = db.query(Operadora.razao_social).distinct().all()
    return [r[0] for r in resultados]

# ======================================================
# DETALHES DA OPERADORA
# ======================================================
@router.get("/{cnpj}", response_model=OperadoraBase)
def detalhes_operadora(cnpj: str, db: Session = Depends(get_db)):
    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()

    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    return OperadoraBase(
        id=str(operadora.id),
        cnpj=operadora.cnpj,
        razao_social=operadora.razao_social,
        nome_fantasia=operadora.nome_fantasia,
        uf=operadora.uf,
        cidade=operadora.cidade,
    )


# ======================================================
# DESPESAS DA OPERADORA
# ======================================================
@router.get("/{cnpj}/despesas", response_model=list[DespesaBase])
def despesas_operadora(cnpj: str, db: Session = Depends(get_db)):
    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()

    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    despesas = (
        db.query(DespesaConsolidada)
        .filter(DespesaConsolidada.operadora_id == operadora.id)
        .order_by(
            DespesaConsolidada.ano,
            DespesaConsolidada.trimestre
        )
        .all()
    )

    return [
        DespesaBase(
            id=str(d.id),
            ano=d.ano,
            trimestre=d.trimestre,
            valor_despesas=float(d.valor_despesas),
            pago=None,
        )
        for d in despesas
    ]




