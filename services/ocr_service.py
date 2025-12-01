"""
Servicio de OCR para extraer datos de boletas y recibos
"""
import re
from PIL import Image
import pytesseract
from datetime import datetime


def extract_text_from_image(image_path):
    """
    Extrae texto de una imagen usando Tesseract OCR
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='spa')
        return text
    except Exception as e:
        print(f"Error al procesar imagen con OCR: {str(e)}")
        return ""


def extract_amounts(text):
    """
    Busca montos en el texto
    Formatos: $12.345, 12345, $12,345
    """
    amounts = []

    # Patrón para montos chilenos: $12.345 o 12.345
    patterns = [
        r'\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # $12.345 o 12.345,00
        r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $12,345 o 12,345.00 (formato US)
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            amount_str = match.group(1)
            # Limpiar y convertir
            amount_str = amount_str.replace('.', '').replace(',', '.')
            try:
                amount = float(amount_str)
                if amount > 0 and amount < 100000000:  # Filtrar montos razonables
                    amounts.append(amount)
            except:
                continue

    return amounts


def extract_date(text):
    """
    Busca fechas en el texto
    Formatos: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    """
    patterns = [
        r'(\d{1,2})[/-.](\d{1,2})[/-.](\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})[/-.](\d{1,2})[/-.](\d{2})',  # DD/MM/YY
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            try:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))

                # Ajustar año de 2 dígitos
                if year < 100:
                    year += 2000 if year < 50 else 1900

                # Validar fecha
                if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                    date = datetime(year, month, day)
                    return date.strftime('%Y-%m-%d')
            except:
                continue

    return None


def extract_rut(text):
    """
    Busca RUTs en el texto
    Formato: 12.345.678-9
    """
    pattern = r'(\d{1,2}\.?\d{3}\.?\d{3}[-]?[0-9kK])'
    matches = re.finditer(pattern, text)

    ruts = []
    for match in matches:
        rut = match.group(1)
        # Limpiar formato
        clean_rut = re.sub(r'[^0-9kK]', '', rut)
        if len(clean_rut) >= 8:
            ruts.append(rut)

    return ruts


def extract_keywords(text):
    """
    Busca palabras clave que indican categorías
    """
    text_lower = text.lower()

    categories = {
        'Transporte': ['taxi', 'uber', 'cabify', 'bus', 'metro', 'peaje', 'combustible', 'bencina', 'estacionamiento'],
        'Alimentación': ['restaurant', 'almuerzo', 'cena', 'comida', 'cafe', 'cafetería'],
        'Hospedaje': ['hotel', 'hostal', 'alojamiento', 'hospedaje'],
        'Materiales': ['ferretería', 'materiales', 'insumos', 'equipamiento'],
    }

    found_categories = []
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_categories.append(category)
                break

    return found_categories


def process_receipt(image_path):
    """
    Procesa una imagen de boleta y extrae toda la información posible
    Retorna: dict con datos extraídos
    """
    text = extract_text_from_image(image_path)

    if not text:
        return {
            'success': False,
            'raw_text': '',
            'amounts': [],
            'date': None,
            'ruts': [],
            'suggested_categories': [],
            'confidence': 'low'
        }

    amounts = extract_amounts(text)
    date = extract_date(text)
    ruts = extract_rut(text)
    categories = extract_keywords(text)

    # Determinar confianza basada en datos encontrados
    confidence = 'low'
    if amounts and date:
        confidence = 'high'
    elif amounts or date:
        confidence = 'medium'

    return {
        'success': True,
        'raw_text': text,
        'amounts': sorted(amounts, reverse=True),  # Ordenar de mayor a menor
        'suggested_amount': amounts[0] if amounts else None,
        'date': date,
        'ruts': ruts,
        'suggested_categories': categories,
        'confidence': confidence
    }
