# Expense App

Sistema completo de gestión de gastos empresariales con aprobaciones jerárquicas, OCR automático, reportes y API REST.

## Características Principales

- ✅ **Gestión de Gastos**: Crear, editar, listar gastos con fotos de boletas
- ✅ **OCR Automático**: Extracción automática de datos de boletas (monto, fecha, RUT)
- ✅ **Flujo de Aprobaciones**: Sistema jerárquico supervisor → admin
- ✅ **Validación de RUT**: Validación automática de RUT chileno
- ✅ **Geolocalización**: Ubicación obligatoria al crear gastos
- ✅ **Dashboards**: Visualización de estadísticas con gráficos interactivos
- ✅ **Reportes**: Por período, categoría, área, con exportación
- ✅ **API REST**: API completa documentada con autenticación
- ✅ **Paginación**: Listados paginados para mejor rendimiento
- ✅ **Multi-rol**: Admin, Supervisor, Usuario con permisos diferenciados
- ✅ **Tests**: Suite completa de tests unitarios e integración

## Requisitos Previos

1.  **Python 3.10+**
2.  **Tesseract OCR** (Necesario para escanear boletas)
    - Linux (Ubuntu/Debian): `sudo apt-get install tesseract-ocr`
    - macOS: `brew install tesseract`
    - Windows: Descargar instalador de [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

## Cómo ejecutar localmente (Sin Docker)

1.  **Crear y activar entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    Asegúrate de tener un archivo `.env` en la raíz (puedes copiar `.env.example` si existe, o crear uno):
    ```env
    FLASK_APP=app.py
    FLASK_DEBUG=1
    SECRET_KEY=dev
    DATABASE_URL=sqlite:///instance/expense.db
    ```

4.  **Inicializar la base de datos (si es la primera vez):**
    ```bash
    python init_db.py
    ```

5.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```
    O usando Flask:
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```

La aplicación estará disponible en `http://localhost:5000`.

## Usuarios de Prueba

Después de ejecutar `init_db.py`, tendrás estos usuarios:

- **Admin**: admin@sixmanager.com / admin123
- **Usuario**: user@sixmanager.com / user123

## Estructura del Proyecto

```
expense-app/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── extensions.py          # Extensiones Flask
├── models/                # Modelos de datos
│   ├── user.py           # Usuario (roles, jerarquía)
│   ├── expense.py        # Gastos
│   ├── approval.py       # Aprobaciones
│   └── company.py        # Clientes, Áreas, Categorías
├── routes/               # Rutas/Blueprints
│   ├── auth.py          # Autenticación
│   ├── expenses.py      # Gestión de gastos
│   ├── approvals.py     # Flujo de aprobaciones
│   ├── admin.py         # Panel admin
│   ├── clients.py       # Gestión de clientes
│   ├── reports.py       # Dashboards y reportes
│   └── api.py           # API REST
├── services/            # Servicios
│   └── ocr_service.py   # OCR para boletas
├── utils/               # Utilidades
│   └── validators.py    # Validación RUT, email
├── templates/           # Vistas HTML
├── static/              # CSS, JS, uploads
├── tests/               # Suite de tests
└── database/            # Base de datos SQLite
```

## Funcionalidades Detalladas

### 1. Gestión de Gastos
- Crear gastos con foto de boleta
- Editar/eliminar gastos pendientes
- Listado con paginación (20 por página)
- Filtros por estado, categoría, fecha
- Asociar gastos a clientes
- Geolocalización obligatoria

### 2. OCR Automático
- Extracción de monto de boletas
- Detección de fecha
- Extracción de RUT
- Sugerencia de categoría según palabras clave
- Niveles de confianza (low, medium, high)

### 3. Flujo de Aprobaciones
- Gastos pendientes para aprobar
- Aprobar/rechazar con comentarios
- Historial de aprobaciones
- Permisos por rol (supervisor ve subordinados, admin ve todo)
- Estados: pending → approved/rejected → reimbursed

### 4. Dashboards y Reportes
- **Dashboard Principal**: Métricas generales, gráficos interactivos
- **Reporte por Período**: Filtro por año/mes, totales mensuales
- **Reporte por Categoría**: Estadísticas por tipo de gasto
- **Reporte por Área**: Uso de presupuesto por departamento
- **Gráficos**: Chart.js con tendencias, distribución

### 5. API REST
- Endpoints completos para gastos, usuarios, aprobaciones
- Autenticación por sesión
- Paginación y filtros
- Documentación completa en `API_DOCUMENTATION.md`
- Health check endpoint

### 6. Validaciones
- **RUT chileno**: Validación con dígito verificador
- **Email**: Formato válido
- **Montos**: Límites por categoría
- **Permisos**: Por rol y jerarquía

## API REST

Ver documentación completa en [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)

**Endpoints principales:**
```
GET    /api/v1/expenses              # Listar gastos
POST   /api/v1/expenses              # Crear gasto
GET    /api/v1/expenses/<id>         # Detalle gasto
PUT    /api/v1/expenses/<id>         # Actualizar gasto
DELETE /api/v1/expenses/<id>         # Eliminar gasto
POST   /api/v1/expenses/<id>/approve # Aprobar gasto
POST   /api/v1/expenses/<id>/reject  # Rechazar gasto
GET    /api/v1/stats/summary         # Estadísticas
GET    /api/v1/users                 # Usuarios (admin)
GET    /api/v1/clients               # Clientes
GET    /api/v1/categories            # Categorías
```

## Tests

Ver guía completa en [`TESTING.md`](./TESTING.md)

```bash
# Instalar dependencias de testing
pip install pytest pytest-flask pytest-cov

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/test_validators.py
pytest tests/test_models.py
pytest tests/test_api.py
```

**Cobertura actual:**
- ✅ Validadores (RUT, email)
- ✅ Modelos (User, Expense, Approval, Company)
- ✅ API REST (CRUD, permisos, aprobaciones)
- ✅ Health checks

## Roles y Permisos

### Usuario (user)
- Crear sus propios gastos
- Ver/editar sus gastos pendientes
- No puede aprobar

### Supervisor (supervisor)
- Todo lo de usuario
- Aprobar/rechazar gastos de subordinados
- Ver reportes de su equipo

### Administrador (admin)
- Acceso completo
- Gestionar usuarios, áreas, clientes
- Aprobar cualquier gasto
- Ver todos los reportes
- Acceso total a API

## Solución de Problemas: Geolocalización en Móvil

Si al probar en el celular recibes el error **"No se pudo obtener la ubicación"**, es porque **los navegadores bloquean la geolocalización en sitios que no son HTTPS** (excepto localhost).

Para probar en el celular tienes dos opciones:

### Opción 1: Usar Ngrok (Recomendado)
Ngrok crea un túnel seguro (HTTPS) a tu servidor local.

1.  Descarga [ngrok](https://ngrok.com/download).
2.  Ejecuta tu app en una terminal: `python app.py`
3.  En **otra terminal**, ejecuta:
    ```bash
    ngrok http 5000
    ```
4.  Copia la URL que empieza con `https://...` y ábrela en tu celular.

### Opción 2: Certificado SSL Ad-hoc (Rápido)
Puedes forzar a Flask a usar HTTPS con un certificado temporal.

1.  Instala la dependencia necesaria:
    ```bash
    pip install pyopenssl
    ```
2.  Ejecuta Flask con modo certificado ad-hoc:
    ```bash
    flask run --host=0.0.0.0 --port=5000 --cert=adhoc
    ```
3.  Accede desde tu celular a `https://<TU_IP_LOCAL>:5000`.
    *Nota: El navegador te mostrará una advertencia de seguridad ("La conexión no es privada"). Debes dar clic en "Configuración avanzada" -> "Continuar de todos modos".*
