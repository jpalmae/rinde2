# API REST Documentation

Documentación de la API REST de Expense App.

## Base URL
```
http://localhost:5000/api/v1
```

## Autenticación
La API requiere autenticación mediante sesión de Flask-Login. Primero debes hacer login en `/login` con el formulario web, luego podrás usar los endpoints de la API.

## Endpoints

### Health Check
```
GET /api/v1/health
```
Verifica el estado de la API.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0"
  }
}
```

---

### Expenses

#### Listar Gastos
```
GET /api/v1/expenses
```

**Query Parameters:**
- `page` (int): Página (default: 1)
- `per_page` (int): Items por página (default: 20)
- `status` (string): Filtrar por estado (pending, approved, rejected, reimbursed)
- `category` (string): Filtrar por categoría
- `user_id` (int): Filtrar por usuario (solo admin/supervisor)

**Response:**
```json
{
  "success": true,
  "data": {
    "expenses": [...],
    "total": 50,
    "pages": 3,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### Obtener Gasto
```
GET /api/v1/expenses/<id>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 2,
    "user_name": "Juan Pérez",
    "amount": 10000.0,
    "category": "Transporte",
    "reason": "Taxi al cliente",
    "status": "pending",
    "receipt_image": "20231201_receipt.jpg",
    "latitude": -33.4489,
    "longitude": -70.6693,
    "expense_date": "2023-12-01",
    "created_at": "2023-12-01T10:00:00"
  }
}
```

#### Crear Gasto
```
POST /api/v1/expenses
Content-Type: application/json
```

**Body:**
```json
{
  "amount": 10000,
  "category": "Transporte",
  "reason": "Taxi al cliente",
  "receipt_image": "receipt.jpg",
  "expense_date": "2023-12-01",
  "latitude": -33.4489,
  "longitude": -70.6693,
  "client_id": 1
}
```

**Response:** Status 201
```json
{
  "success": true,
  "message": "Gasto creado exitosamente",
  "data": { ... }
}
```

#### Actualizar Gasto
```
PUT /api/v1/expenses/<id>
Content-Type: application/json
```

**Body:**
```json
{
  "amount": 15000,
  "reason": "Actualizado"
}
```

Solo se pueden actualizar gastos con estado "pending" y solo por el creador o admin.

#### Eliminar Gasto
```
DELETE /api/v1/expenses/<id>
```

Solo se pueden eliminar gastos "pending".

---

### Approvals

#### Aprobar Gasto
```
POST /api/v1/expenses/<id>/approve
Content-Type: application/json
```

**Body:**
```json
{
  "comments": "Aprobado según presupuesto"
}
```

**Permisos:** Supervisor o Admin

#### Rechazar Gasto
```
POST /api/v1/expenses/<id>/reject
Content-Type: application/json
```

**Body:**
```json
{
  "comments": "Monto excede presupuesto"
}
```

El campo `comments` es **obligatorio** al rechazar.

---

### Users (Admin only)

#### Listar Usuarios
```
GET /api/v1/users
```

#### Obtener Usuario
```
GET /api/v1/users/<id>
```

#### Crear Usuario
```
POST /api/v1/users
Content-Type: application/json
```

**Body:**
```json
{
  "email": "user@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "password": "password123",
  "role": "user",
  "area_id": 1,
  "supervisor_id": 2
}
```

---

### Statistics

#### Resumen de Estadísticas
```
GET /api/v1/stats/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_expenses": 100,
    "pending": 20,
    "approved": 70,
    "rejected": 10,
    "total_amount": 5000000.0
  }
}
```

---

### Clients

#### Listar Clientes
```
GET /api/v1/clients
```

---

### Categories

#### Listar Categorías
```
GET /api/v1/categories
```

---

## Códigos de Estado

- `200` - OK
- `201` - Created
- `400` - Bad Request (datos inválidos)
- `401` - Unauthorized (no autenticado)
- `403` - Forbidden (sin permisos)
- `404` - Not Found
- `500` - Internal Server Error

## Ejemplo de Uso con cURL

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Login primero (obtener cookie de sesión)
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "email=user@test.com&password=user123"

# Listar gastos (usando cookie de sesión)
curl -b cookies.txt http://localhost:5000/api/v1/expenses

# Crear gasto
curl -b cookies.txt -X POST http://localhost:5000/api/v1/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 10000, "category": "Transporte", "reason": "Taxi", "receipt_image": "test.jpg"}'

# Aprobar gasto
curl -b cookies.txt -X POST http://localhost:5000/api/v1/expenses/1/approve \
  -H "Content-Type: application/json" \
  -d '{"comments": "Aprobado"}'
```

## Ejemplo con Python Requests

```python
import requests

BASE_URL = "http://localhost:5000"
session = requests.Session()

# Login
session.post(f"{BASE_URL}/login", data={
    "email": "user@test.com",
    "password": "user123"
})

# Listar gastos
response = session.get(f"{BASE_URL}/api/v1/expenses")
expenses = response.json()

# Crear gasto
response = session.post(f"{BASE_URL}/api/v1/expenses", json={
    "amount": 10000,
    "category": "Transporte",
    "reason": "Taxi al cliente",
    "receipt_image": "test.jpg",
    "latitude": -33.4489,
    "longitude": -70.6693
})
```
