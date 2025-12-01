"""
Utilidades de validación para formularios
"""
import re


def clean_rut(rut):
    """
    Limpia un RUT removiendo puntos, guiones y espacios
    Ejemplo: '12.345.678-9' -> '123456789'
    """
    if not rut:
        return ''
    return re.sub(r'[^0-9kK]', '', str(rut))


def format_rut(rut):
    """
    Formatea un RUT al formato chileno estándar: XX.XXX.XXX-X
    """
    clean = clean_rut(rut)
    if not clean:
        return ''

    # Separar número y dígito verificador
    num = clean[:-1]
    dv = clean[-1].upper()

    # Formatear con puntos
    formatted = ''
    for i, digit in enumerate(reversed(num)):
        if i > 0 and i % 3 == 0:
            formatted = '.' + formatted
        formatted = digit + formatted

    return f"{formatted}-{dv}"


def calculate_rut_dv(rut_number):
    """
    Calcula el dígito verificador de un RUT
    """
    rut_number = str(rut_number)
    reversed_digits = map(int, reversed(rut_number))
    factors = [2, 3, 4, 5, 6, 7]

    s = 0
    for i, digit in enumerate(reversed_digits):
        s += digit * factors[i % 6]

    remainder = 11 - (s % 11)

    if remainder == 11:
        return '0'
    elif remainder == 10:
        return 'K'
    else:
        return str(remainder)


def validate_rut(rut):
    """
    Valida un RUT chileno
    Retorna: (is_valid: bool, error_message: str)
    """
    if not rut:
        return False, "RUT es requerido"

    # Limpiar RUT
    clean = clean_rut(rut)

    # Validar largo mínimo (7 números + 1 DV)
    if len(clean) < 2:
        return False, "RUT debe tener al menos 2 caracteres"

    # Validar que tenga solo números y posiblemente K
    if not re.match(r'^\d+[0-9kK]$', clean):
        return False, "RUT tiene formato inválido"

    # Separar número y dígito verificador
    rut_number = clean[:-1]
    provided_dv = clean[-1].upper()

    # Validar largo razonable (RUT chileno tiene entre 7-8 dígitos + DV)
    if len(rut_number) < 7 or len(rut_number) > 8:
        return False, "RUT debe tener entre 7 y 8 dígitos"

    # Calcular dígito verificador correcto
    calculated_dv = calculate_rut_dv(rut_number)

    # Comparar
    if calculated_dv != provided_dv:
        return False, f"Dígito verificador inválido. Debería ser {calculated_dv}"

    return True, ""


def validate_email(email):
    """
    Validación básica de email
    """
    if not email:
        return False, "Email es requerido"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email tiene formato inválido"

    return True, ""
