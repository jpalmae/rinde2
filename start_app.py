#!/usr/bin/env python3
"""
Script de inicio para la aplicación de gastos
Maneja errores comunes y proporciona información útil
"""
import sys
import os
import socket

def check_port_available(port):
    """Verificar si un puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=5000):
    """Encontrar un puerto disponible"""
    for port in range(start_port, start_port + 10):
        if check_port_available(port):
            return port
    return None

def main():
    """Función principal de inicio"""
    print("🚀 Iniciando aplicación de gastos...")
    
    # Verificar entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No se detecta entorno virtual")
        print("   Se recomienda ejecutar: source venv/bin/activate")
    
    # Verificar directorio actual
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py en el directorio actual")
        print("   Asegúrate de estar en el directorio raíz del proyecto")
        sys.exit(1)
    
    # Encontrar puerto disponible
    port = find_available_port(5000)
    if not port:
        print("❌ Error: No hay puertos disponibles en el rango 5000-5010")
        sys.exit(1)
    
    if port != 5000:
        print(f"ℹ️  Puerto 5000 en uso, usando puerto {port}")
    
    try:
        # Importar y crear aplicación
        print("📦 Importando módulos...")
        from app import create_app
        
        print("🔧 Creando aplicación...")
        app = create_app()
        
        print(f"🌐 Iniciando servidor en http://localhost:{port}")
        print("📝 Logs disponibles en directorio logs/")
        print("⏹️  Presiona Ctrl+C para detener")
        print("=" * 50)
        
        # Iniciar servidor
        app.run(
            debug=True,
            host='0.0.0.0',
            port=port,
            use_reloader=False  # Evitar problemas con el script
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Solución:")
        print("   1. Activa el entorno virtual: source venv/bin/activate")
        print("   2. Instala dependencias: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()