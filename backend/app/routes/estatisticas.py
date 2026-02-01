from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.despesas_agregadas import DespesasAgregadas
from app.models.operadora import Operadora

router = APIRouter()

@router.get("/")
def estatisticas(db: Session = Depends(get_db)):
    resultados = db.query(DespesasAgregadas).all()
    return resultados