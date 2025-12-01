# Testing Guide

Guía para ejecutar los tests de la aplicación.

## Instalación de Dependencias de Testing

```bash
pip install pytest pytest-flask pytest-cov
```

O instalar todas las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecutar Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests con verbose
```bash
pytest -v
```

### Ejecutar tests específicos
```bash
# Solo tests de validadores
pytest tests/test_validators.py

# Solo tests de modelos
pytest tests/test_models.py

# Solo tests de API
pytest tests/test_api.py

# Test específico
pytest tests/test_validators.py::TestRUTValidation::test_validate_rut_valid
```

### Ejecutar con cobertura
```bash
pytest --cov=. --cov-report=html
```

Esto generará un reporte en `htmlcov/index.html`

### Ejecutar con output detallado
```bash
pytest -v --tb=short
```

## Estructura de Tests

```
tests/
├── __init__.py           # Paquete de tests
├── conftest.py           # Fixtures compartidos
├── test_validators.py    # Tests de validación (RUT, email)
├── test_models.py        # Tests de modelos de datos
└── test_api.py           # Tests de API REST
```

## Fixtures Disponibles

### `app`
Aplicación Flask de prueba con configuración de testing.

```python
def test_something(app):
    with app.app_context():
        # Tu código aquí
```

### `client`
Cliente de prueba para hacer requests HTTP.

```python
def test_endpoint(client):
    response = client.get('/some-endpoint')
    assert response.status_code == 200
```

### `init_database`
Base de datos inicializada con datos de prueba:
- 3 usuarios (admin, supervisor, user)
- 1 área (IT)
- 2 categorías de gastos
- 1 cliente

```python
def test_with_data(app, init_database):
    with app.app_context():
        from models.user import User
        user = User.query.first()
        assert user is not None
```

## Usuarios de Prueba

- **Admin**: admin@test.com / admin123
- **Supervisor**: supervisor@test.com / super123
- **User**: user@test.com / user123

## Ejemplo: Escribir un Test

```python
# tests/test_example.py
import pytest
from models.expense import Expense

def test_create_expense(app, init_database):
    """Test crear un gasto"""
    with app.app_context():
        from extensions import db
        from models.user import User
        from datetime import datetime

        user = User.query.filter_by(email="user@test.com").first()

        expense = Expense(
            user_id=user.id,
            amount=10000,
            category="Transporte",
            reason="Taxi",
            receipt_image="test.jpg",
            expense_date=datetime.now(),
            status="pending"
        )

        db.session.add(expense)
        db.session.commit()

        assert expense.id is not None
        assert expense.amount == 10000
```

## Cobertura de Tests

Los tests actuales cubren:

### Validadores (test_validators.py)
- ✅ Validación de RUT chileno
- ✅ Formateo de RUT
- ✅ Cálculo de dígito verificador
- ✅ Validación de email

### Modelos (test_models.py)
- ✅ Creación de usuarios
- ✅ Hash y verificación de contraseñas
- ✅ Relaciones supervisor-subordinado
- ✅ Creación de gastos
- ✅ Relaciones gasto-cliente
- ✅ Áreas y presupuestos

### API (test_api.py)
- ✅ Health check
- ✅ CRUD de gastos
- ✅ Permisos de acceso
- ✅ Aprobación/rechazo de gastos
- ✅ Gestión de usuarios (admin)
- ✅ Estadísticas

## CI/CD

Para integrar en un pipeline de CI/CD:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        sudo apt-get install tesseract-ocr

    - name: Run tests
      run: pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Debugging Tests

### Usar pdb para debugging
```python
def test_something(app):
    import pdb; pdb.set_trace()
    # Tu código aquí
```

### Ver prints durante tests
```bash
pytest -s
```

### Ver variables locales en fallos
```bash
pytest -l
```

## Mejores Prácticas

1. **Un test, una funcionalidad**: Cada test debe probar una sola cosa
2. **Nombres descriptivos**: `test_create_expense_without_required_fields`
3. **AAA Pattern**: Arrange (preparar), Act (ejecutar), Assert (verificar)
4. **Independencia**: Tests no deben depender unos de otros
5. **Cleanup**: Usar fixtures para setup y teardown
6. **Mock**: Mockear dependencias externas (APIs, OCR, etc.)

## Próximos Tests a Implementar

- [ ] Tests de OCR service
- [ ] Tests de reportes
- [ ] Tests de permisos más exhaustivos
- [ ] Tests de edge cases
- [ ] Tests de performance
- [ ] Tests e2e con Selenium
