# 🚀 Guía de Inicio Rápida

## ✅ Requisitos
- Python 3.8+
- Entorno virtual activado

## 🛠️ Instalación
```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar base de datos
python init_db.py
```

## 🚀 Iniciar Aplicación

### Opción 1: Script recomendado (maneja errores automáticamente)
```bash
python start_app.py
```

### Opción 2: Inicio directo
```bash
python app.py
```

### Opción 3: Con Gunicorn (producción)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔧 Solución de Problemas Comunes

### Error: "Puerto 5000 en uso"
```bash
# Usar el script (automático)
python start_app.py

# O matar el proceso
sudo lsof -ti:5000 | xargs kill -9
```

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el entorno virtual
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "ImportError"
```bash
# Verificar que estás en el directorio correcto
pwd  # Debe ser /home/jpalma/dev/rinde/expense-app

# Verificar archivos clave
ls app.py config.py requirements.txt
```

## 📝 Logs
Los logs se guardan en el directorio `logs/`:
- `app.log` - Logs generales de la aplicación
- `security.log` - Eventos de seguridad
- `errors.log` - Errores y excepciones
- `api.log` - Logs de endpoints API

## 🧪 Tests
```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=.
```

## 🌐 Acceso
- **Aplicación web**: http://localhost:5001 (o puerto asignado)
- **API endpoints**: http://localhost:5001/api/v1/
- **Health check**: http://localhost:5001/api/v1/health

## 👤 Usuarios por Defecto
- **Admin**: admin@test.com / admin123
- **Supervisor**: supervisor@test.com / super123  
- **Usuario**: user@test.com / user123

---
🎉 **¡Listo! Tu aplicación mejorada está funcionando.**