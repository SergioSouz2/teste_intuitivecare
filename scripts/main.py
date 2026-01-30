import sys
from pathlib import Path

# Adicionar o diretório pai ao sys.path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Tentar imports relativos (quando executado como módulo)
    from .download import download_and_extract
    from .processing import process
    from .consolidation import consolidate
except ImportError:
    # Fallback para imports absolutos (quando executado como script)
    from scripts.download import download_and_extract
    from scripts.processing import process
    from scripts.consolidation import consolidate


def main():
    """Executa o pipeline completo de ETL"""
    try:
        print("\n" + "=" * 70)
        print("INICIANDO PIPELINE DE DEMONSTRAÇÕES CONTÁBEIS")
        print("=" * 70)
        
        print("\n[1/3] Baixando e extraindo arquivos...")
        download_and_extract()
        
        print("\n[2/3] Processando dados...")
        process()
        
        print("\n[3/3] Consolidando dados...")
        consolidate()
        
        print("\n" + "=" * 70)
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO NO PIPELINE: {e}\n")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

