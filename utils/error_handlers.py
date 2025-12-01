"""
Manejo centralizado de errores para la aplicación
"""
from flask import jsonify, request, current_app, render_template, flash
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils.exceptions import ExpenseAppException, ValidationError, DatabaseError
from utils.logging_config import error_logger
import traceback

def handle_expense_app_exception(e):
    """Manejador para excepciones personalizadas de la aplicación"""
    
    # Loggear el error
    error_logger.error(
        f"Application Error: {e.message}",
        extra={
            'user_id': getattr(current_user, 'id', 'Anonymous'),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint,
            'extra_info': {
                'error_code': e.error_code,
                'status_code': e.status_code,
                'payload': e.payload
            }
        }
    )
    
    # Determinar tipo de respuesta
    if request.path.startswith('/api/'):
        # Respuesta JSON para API
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    else:
        # Respuesta HTML para web
        flash(e.message, 'error')
        return render_template('errors/error.html', 
                             error=e, 
                             status_code=e.status_code), e.status_code

def handle_validation_error(e):
    """Manejador para errores de validación"""
    return handle_expense_app_exception(e)

def handle_database_error(e):
    """Manejador para errores de base de datos"""
    
    # Loggear el error con traceback
    error_logger.error(
        f"Database Error: {str(e)}",
        extra={
            'user_id': getattr(current_user, 'id', 'Anonymous'),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint,
            'extra_info': {
                'traceback': traceback.format_exc()
            }
        }
    )
    
    # No exponer detalles internos en producción
    if current_app.config.get('ENV') == 'production':
        message = "Error interno del servidor. Por favor, inténtalo más tarde."
    else:
        message = f"Error de base de datos: {str(e)}"
    
    db_error = DatabaseError(
        message=message,
        operation=getattr(e, '__class__', '__name__', 'Unknown')
    )
    
    return handle_expense_app_exception(db_error)

def handle_integrity_error(e):
    """Manejador para errores de integridad"""
    
    error_logger.error(
        f"Integrity Error: {str(e)}",
        extra={
            'user_id': getattr(current_user, 'id', 'Anonymous'),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint,
            'extra_info': {
                'original_error': str(e)
            }
        }
    )
    
    # Intentar extraer información útil del error
    error_str = str(e).lower()
    
    if 'unique' in error_str:
        if 'email' in error_str:
            message = "El email ya está registrado"
        elif 'rut' in error_str:
            message = "El RUT ya está registrado"
        else:
            message = "Registro duplicado: el valor ya existe"
    elif 'foreign key' in error_str:
        message = "Referencia inválida: el registro relacionado no existe"
    elif 'not null' in error_str:
        message = "Campo requerido faltante"
    else:
        message = "Error de integridad de datos"
    
    from utils.exceptions import IntegrityError as CustomIntegrityError
    integrity_error = CustomIntegrityError(
        message=message,
        constraint=str(e)
    )
    
    return handle_expense_app_exception(integrity_error)

def handle_http_exception(e):
    """Manejador para excepciones HTTP estándar"""
    
    error_logger.warning(
        f"HTTP Error {e.code}: {e.name}",
        extra={
            'user_id': getattr(current_user, 'id', 'Anonymous'),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint,
            'extra_info': {
                'description': e.description
            }
        }
    )
    
    if request.path.startswith('/api/'):
        # Respuesta JSON para API
        response = jsonify({
            'error': e.name,
            'message': e.description,
            'success': False,
            'status_code': e.code
        })
        response.status_code = e.code
        return response
    else:
        # Respuesta HTML para web
        return render_template('errors/http_error.html', 
                             error=e, 
                             status_code=e.code), e.code

def handle_generic_exception(e):
    """Manejador para excepciones genéricas no capturadas"""
    
    # Loggear el error completo con traceback
    error_logger.critical(
        f"Unhandled Exception: {str(e)}",
        extra={
            'user_id': getattr(current_user, 'id', 'Anonymous'),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint,
            'extra_info': {
                'exception_type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
        }
    )
    
    # No exponer detalles internos en producción
    if current_app.config.get('ENV') == 'production':
        message = "Error interno del servidor. Por favor, contacta al soporte."
    else:
        message = f"Error no manejado: {str(e)}"
    
    generic_error = ExpenseAppException(
        message=message,
        error_code='INTERNAL_ERROR',
        status_code=500
    )
    
    return handle_expense_app_exception(generic_error)

def register_error_handlers(app):
    """Registrar todos los manejadores de errores en la aplicación Flask"""
    
    # Excepciones personalizadas
    app.register_error_handler(ExpenseAppException, handle_expense_app_exception)
    app.register_error_handler(ValidationError, handle_validation_error)
    
    # Errores de base de datos
    app.register_error_handler(SQLAlchemyError, handle_database_error)
    app.register_error_handler(IntegrityError, handle_integrity_error)
    
    # Excepciones HTTP estándar
    app.register_error_handler(HTTPException, handle_http_exception)
    
    # Excepción genérica (catch-all)
    app.register_error_handler(Exception, handle_generic_exception)
    
    # Errores específicos comunes
    app.register_error_handler(404, lambda e: handle_http_exception(e))
    app.register_error_handler(500, lambda e: handle_generic_exception(e))
    app.register_error_handler(403, lambda e: handle_http_exception(e))
    app.register_error_handler(401, lambda e: handle_http_exception(e))

def log_request_info():
    """Middleware para loggear información de requests"""
    
    # Loggear request
    current_app.logger.info(
        f"Request: {request.method} {request.path}"
    )

def setup_error_middleware(app):
    """Configurar middleware de manejo de errores"""
    
    @app.before_request
    def before_request():
        """Ejecutar antes de cada request"""
        log_request_info()
    
    @app.after_request
    def after_request(response):
        """Ejecutar después de cada request"""
        
        # Loggear response
        current_app.logger.info(
            f"Response: {response.status_code}"
        )
        
        return response