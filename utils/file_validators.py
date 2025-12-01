"""
Utilidades de validación de archivos para seguridad
"""
import os
import magic
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

class FileValidationError(Exception):
    """Excepción para errores de validación de archivos"""
    pass

def validate_file_upload(file, allowed_extensions=None, max_size_mb=None):
    """
    Validación completa de archivos subidos
    
    Args:
        file: Objeto FileStorage de Flask
        allowed_extensions: Set de extensiones permitidas (opcional)
        max_size_mb: Tamaño máximo en MB (opcional)
    
    Returns:
        dict: Información del archivo validado
    
    Raises:
        FileValidationError: Si el archivo no es válido
    """
    if not file or file.filename == '':
        raise FileValidationError('No se seleccionó ningún archivo')
    
    # Usar configuración por defecto si no se especifica
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    
    if max_size_mb is None:
        max_size_mb = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024) // (1024 * 1024)
    
    filename = secure_filename(file.filename)
    
    # Validar extensión
    if not ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        raise FileValidationError(
            f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(allowed_extensions)}'
        )
    
    # Validar tamaño
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise FileValidationError(
            f'Archivo demasiado grande. Tamaño máximo: {max_size_mb}MB'
        )
    
    # Validar contenido real del archivo (magic bytes)
    try:
        # Leer primeros bytes para determinar tipo real
        file_content = file.read(1024)
        file.seek(0)
        
        # Usar python-magic para detectar tipo real
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Mapear MIME types permitidos
        allowed_mime_types = {
            'image/jpeg',
            'image/png', 
            'image/gif',
            'image/webp'
        }
        
        if mime_type not in allowed_mime_types:
            raise FileValidationError(
                f'Tipo de archivo no detectado como imagen válida. Detectado: {mime_type}'
            )
        
        # Validar que sea realmente una imagen usando PIL
        try:
            img = Image.open(file)
            img.verify()  # Verificar que es una imagen válida
            file.seek(0)
            
            # Obtener dimensiones
            img = Image.open(file)
            width, height = img.size
            file.seek(0)
            
        except Exception as e:
            raise FileValidationError(f'El archivo no es una imagen válida: {str(e)}')
        
        return {
            'filename': filename,
            'mime_type': mime_type,
            'size': file_size,
            'width': width,
            'height': height,
            'is_valid': True
        }
        
    except Exception as e:
        if isinstance(e, FileValidationError):
            raise
        raise FileValidationError(f'Error validando archivo: {str(e)}')

def generate_unique_filename(original_filename, user_id=None):
    """
    Generar nombre de archivo único para evitar colisiones
    
    Args:
        original_filename: Nombre original del archivo
        user_id: ID del usuario (opcional)
    
    Returns:
        str: Nombre de archivo único
    """
    from datetime import datetime
    
    # Limpiar nombre de archivo
    filename = secure_filename(original_filename)
    
    # Extraer extensión
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
    else:
        name, ext = filename, ''
    
    # Generar timestamp y user_id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    user_suffix = f"_{user_id}" if user_id else ""
    
    # Construir nombre único
    unique_name = f"{name}_{timestamp}{user_suffix}.{ext}" if ext else f"{name}_{timestamp}{user_suffix}"
    
    return unique_name

def scan_file_for_malware(file_path):
    """
    Escaneo básico de malware (puede ser expandido con herramientas reales)
    
    Args:
        file_path: Ruta al archivo a escanear
    
    Returns:
        tuple: (is_clean, threat_info)
    """
    try:
        # Escaneo básico - patrones conocidos en archivos
        with open(file_path, 'rb') as f:
            content = f.read(1024)  # Leer primeros KB
            
            # Patrones sospechosos básicos
            suspicious_patterns = [
                b'<?php',
                b'<script',
                b'javascript:',
                b'data:text/html',
                b'vbscript:',
                b'%PDF-',  # PDF files disfrazados
            ]
            
            for pattern in suspicious_patterns:
                if pattern in content.lower():
                    return False, f"Patrón sospechoso detectado: {pattern.decode('utf-8', errors='ignore')}"
        
        # Verificar que el archivo no sea ejecutable
        if os.name == 'nt':  # Windows
            if file_path.lower().endswith(('.exe', '.bat', '.cmd', '.scr')):
                return False, "Tipo de archivo ejecutable no permitido"
        else:  # Unix/Linux
            # Verificar permisos ejecutables
            if os.access(file_path, os.X_OK):
                return False, "Archivo con permisos de ejecución"
        
        return True, "Archivo limpio"
        
    except Exception as e:
        # En caso de error, asumir que es sospechoso
        return False, f"Error escaneando archivo: {str(e)}"