"""
Excepciones personalizadas para la aplicación
"""

class ExpenseAppException(Exception):
    """Clase base para excepciones de la aplicación"""
    
    def __init__(self, message, error_code=None, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convertir excepción a diccionario para respuestas API"""
        result = {
            'error': self.message,
            'error_code': self.error_code,
            'success': False
        }
        if self.payload:
            result.update(self.payload)
        return result

# ============= Excepciones de Validación =============

class ValidationError(ExpenseAppException):
    """Error de validación de datos"""
    
    def __init__(self, message, field=None, **kwargs):
        super().__init__(message, error_code='VALIDATION_ERROR', status_code=400, **kwargs)
        self.field = field
    
    def to_dict(self):
        result = super().to_dict()
        if self.field:
            result['field'] = self.field
        return result

class AuthenticationError(ExpenseAppException):
    """Error de autenticación"""
    
    def __init__(self, message='Credenciales inválidas', **kwargs):
        super().__init__(message, error_code='AUTH_ERROR', status_code=401, **kwargs)

class AuthorizationError(ExpenseAppException):
    """Error de autorización"""
    
    def __init__(self, message='Permisos insuficientes', **kwargs):
        super().__init__(message, error_code='AUTHZ_ERROR', status_code=403, **kwargs)

class ResourceNotFoundError(ExpenseAppException):
    """Recurso no encontrado"""
    
    def __init__(self, resource='Recurso', **kwargs):
        message = f'{resource} no encontrado'
        super().__init__(message, error_code='NOT_FOUND', status_code=404, **kwargs)
        self.resource = resource
    
    def to_dict(self):
        result = super().to_dict()
        result['resource'] = self.resource
        return result

class ConflictError(ExpenseAppException):
    """Conflicto de recursos"""
    
    def __init__(self, message, **kwargs):
        super().__init__(message, error_code='CONFLICT', status_code=409, **kwargs)

# ============= Excepciones de Negocio =============

class BusinessRuleError(ExpenseAppException):
    """Violación de reglas de negocio"""
    
    def __init__(self, message, rule=None, **kwargs):
        super().__init__(message, error_code='BUSINESS_RULE_ERROR', status_code=422, **kwargs)
        self.rule = rule
    
    def to_dict(self):
        result = super().to_dict()
        if self.rule:
            result['rule'] = self.rule
        return result

class ExpenseLimitError(BusinessRuleError):
    """Error de límite de gasto"""
    
    def __init__(self, amount, limit, **kwargs):
        message = f'Monto ${amount:,.0f} excede el límite de ${limit:,.0f}'
        super().__init__(message, rule='EXPENSE_LIMIT', **kwargs)
        self.amount = amount
        self.limit = limit
    
    def to_dict(self):
        result = super().to_dict()
        result.update({
            'amount': self.amount,
            'limit': self.limit
        })
        return result

class DuplicateResourceError(ConflictError):
    """Recurso duplicado"""
    
    def __init__(self, resource, field, value, **kwargs):
        message = f'{resource} con {field} "{value}" ya existe'
        super().__init__(message, **kwargs)
        self.resource = resource
        self.field = field
        self.value = value
    
    def to_dict(self):
        result = super().to_dict()
        result.update({
            'resource': self.resource,
            'field': self.field,
            'value': self.value
        })
        return result

# ============= Excepciones de Archivos =============

class FileUploadError(ExpenseAppException):
    """Error en subida de archivos"""
    
    def __init__(self, message, **kwargs):
        super().__init__(message, error_code='FILE_UPLOAD_ERROR', status_code=400, **kwargs)

class FileValidationError(FileUploadError):
    """Error de validación de archivo"""
    
    def __init__(self, message, file_type=None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_type = file_type
    
    def to_dict(self):
        result = super().to_dict()
        if self.file_type:
            result['file_type'] = self.file_type
        return result

class FileSizeError(FileUploadError):
    """Error de tamaño de archivo"""
    
    def __init__(self, size, max_size, **kwargs):
        message = f'Archivo de {size}MB excede el límite de {max_size}MB'
        super().__init__(message, **kwargs)
        self.size = size
        self.max_size = max_size
    
    def to_dict(self):
        result = super().to_dict()
        result.update({
            'size': self.size,
            'max_size': self.max_size
        })
        return result

# ============= Excepciones de Base de Datos =============

class DatabaseError(ExpenseAppException):
    """Error de base de datos"""
    
    def __init__(self, message, operation=None, **kwargs):
        super().__init__(message, error_code='DATABASE_ERROR', **kwargs)
        self.operation = operation
    
    def to_dict(self):
        result = super().to_dict()
        if self.operation:
            result['operation'] = self.operation
        return result

class IntegrityError(DatabaseError):
    """Error de integridad de datos"""
    
    def __init__(self, message, constraint=None, **kwargs):
        super().__init__(message, operation='INTEGRITY_CHECK', **kwargs)
        self.constraint = constraint
    
    def to_dict(self):
        result = super().to_dict()
        if self.constraint:
            result['constraint'] = self.constraint
        return result

# ============= Excepciones de Servicios Externos =============

class ExternalServiceError(ExpenseAppException):
    """Error de servicio externo"""
    
    def __init__(self, service, message, **kwargs):
        super().__init__(message, error_code='EXTERNAL_SERVICE_ERROR', **kwargs)
        self.service = service
    
    def to_dict(self):
        result = super().to_dict()
        result['service'] = self.service
        return result

class OCRError(ExternalServiceError):
    """Error en servicio OCR"""
    
    def __init__(self, message, **kwargs):
        super().__init__('OCR', message, **kwargs)

class EmailError(ExternalServiceError):
    """Error en servicio de email"""
    
    def __init__(self, message, **kwargs):
        super().__init__('EMAIL', message, **kwargs)

# ============= Excepciones de API =============

class APIError(ExpenseAppException):
    """Error genérico de API"""
    
    def __init__(self, message, endpoint=None, **kwargs):
        super().__init__(message, error_code='API_ERROR', **kwargs)
        self.endpoint = endpoint
    
    def to_dict(self):
        result = super().to_dict()
        if self.endpoint:
            result['endpoint'] = self.endpoint
        return result

class RateLimitError(APIError):
    """Error de rate limiting"""
    
    def __init__(self, limit, reset_time, **kwargs):
        message = f'Límite de solicitudes excedido. Máximo: {limit}'
        super().__init__(message, error_code='RATE_LIMIT', status_code=429, **kwargs)
        self.limit = limit
        self.reset_time = reset_time
    
    def to_dict(self):
        result = super().to_dict()
        result.update({
            'limit': self.limit,
            'reset_time': self.reset_time
        })
        return result