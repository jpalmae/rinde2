#!/usr/bin/env python3
"""
Script de inicio simple sin logging complejo
"""
import sys
import os

def main():
    print("🚀 Iniciando aplicación de gastos...")
    
    # Verificar directorio actual
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py")
        sys.exit(1)
    
    try:
        # Importar y crear aplicación
        print("📦 Importando módulos...")
        from app import create_app
        
        print("🔧 Creando aplicación...")
        app = create_app()
        
        print("🌐 Iniciando servidor en http://localhost:5000")
        print("⏹️  Presiona Ctrl+C para detener")
        print("=" * 50)
        
        # Iniciar servidor sin logging complejo
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Solución: source venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()