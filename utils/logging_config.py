"""
Configuración de logging estructurado para la aplicación
"""
import logging
import logging.config
import os
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato base
        log_format = f"{color}[{self.formatTime(record)}] {record.levelname:8} {reset}"
        log_format += f" {getattr(record, 'user_id', 'N/A'):>5} "
        log_format += f"{getattr(record, 'ip_address', 'N/A'):>15} "
        log_format += f"{getattr(record, 'endpoint', 'N/A'):>20} "
        log_format += f"- {record.getMessage()}"
        
        # Añadir extra info si existe
        extra_info = getattr(record, 'extra_info', '')
        if extra_info:
            log_format += f" | Extra: {extra_info}"
            
        return log_format

def setup_logging(app):
    """Configurar logging para la aplicación"""
    
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuración de logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[{asctime}] {levelname:8} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[{asctime}] {levelname:8} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'colored': {
            '()': ColoredFormatter,
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'colored',
                'stream': 'ext://sys.stdout'
            },
            'file_app': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'app.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_security': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'security.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_errors': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'errors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_api': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'api.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file_app'],
                'level': 'DEBUG',
                'propagate': False
            },
            'security': {
                'handlers': ['console', 'file_security'],
                'level': 'INFO',
                'propagate': False
            },
            'errors': {
                'handlers': ['console', 'file_errors'],
                'level': 'ERROR',
                'propagate': False
            },
            'api': {
                'handlers': ['console', 'file_api'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    # Aplicar configuración
    logging.config.dictConfig(logging_config)
    
    # Crear loggers específicos
    app.logger_security = logging.getLogger('security')
    app.logger_errors = logging.getLogger('errors')
    app.logger_api = logging.getLogger('api')
    
    # Configurar nivel según entorno
    if app.config.get('TESTING'):
        logging.getLogger('').setLevel(logging.WARNING)
    elif app.config.get('DEBUG'):
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

def get_logger_with_context(logger_name='app'):
    """Obtener logger con contexto de la aplicación"""
    logger = logging.getLogger(logger_name)
    
    def log_with_context(level, message, **context):
        """Crear log entry con contexto"""
        extra = {
            'user_id': context.get('user_id', 'N/A'),
            'ip_address': context.get('ip_address', 'N/A'),
            'endpoint': context.get('endpoint', 'N/A'),
            'extra_info': context.get('extra_info', '')
        }
        
        logger.log(level, message, extra=extra)
    
    return log_with_context

# Logger específicos para diferentes propósitos
security_logger = logging.getLogger('security')
error_logger = logging.getLogger('errors')
api_logger = logging.getLogger('api')