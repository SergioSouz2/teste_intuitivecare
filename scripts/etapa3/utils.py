import logging
import re

logger = logging.getLogger("pipeline")

def sanitize_value(value, max_len):
    """Remove espaços e limita tamanho da string"""
    if value is None:
        return None
    value = str(value).strip()
    if len(value) > max_len:
        logger.warning(f"Valor truncado: '{value}' -> '{value[:max_len]}'")
    return value[:max_len]

def is_valid_cnpj(cnpj):
    """Valida formato do CNPJ: apenas números e 14 dígitos"""
    if cnpj is None:
        return False
    cnpj = re.sub(r'\D', '', str(cnpj))
    return len(cnpj) == 14
