import logging
import re

logger = logging.getLogger(__name__)


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

def safe_int(value):
    try:
        if value is None or value == '':
            return None
        return int(float(value))
    except ValueError:
        return None

def safe_float(value):
    try:
        if value is None or value == '':
            return None
        return float(value)
    except ValueError:
        return None