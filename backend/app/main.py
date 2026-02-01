from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.routes import operadoras, estatisticas

load_dotenv()

app = FastAPI(title="API Operadoras")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em prod, restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    operadoras.router,
    prefix="/api/operadoras",
    tags=["Operadoras"]
)

app.include_router(
    estatisticas.router,
    prefix="/api/estatisticas",
    tags=["Estatísticas"]
)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
