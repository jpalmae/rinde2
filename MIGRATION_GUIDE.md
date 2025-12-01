# Guía de Migración - Cliente Obligatorio

Esta guía explica cómo migrar tu base de datos existente al nuevo flujo donde el cliente es obligatorio.

## Cambios Implementados

1. **Campo `client_id` ahora es obligatorio** en el modelo Expense
2. **Nuevo campo `created_with_expense`** en el modelo Company
3. **Flujo de aprobación en cascada**: Cliente → Gasto
4. **Creación de cliente desde formulario de gasto**

---

## Paso 1: Backup de la Base de Datos

**IMPORTANTE:** Siempre haz un backup antes de migrar.

```bash
# Backup de SQLite
cp database/expense.db database/expense.db.backup_$(date +%Y%m%d)

# Verificar backup
ls -lh database/
```

---

## Paso 2: Ejecutar Script de Migración

El script `migrate_client_required.py` realiza las siguientes acciones:

1. Identifica gastos sin cliente asignado
2. Crea un cliente "Por Defecto" si es necesario
3. Asigna el cliente por defecto a gastos huérfanos
4. Actualiza el campo `created_with_expense` en clientes existentes

```bash
# Ejecutar migración
python migrate_client_required.py
```

**Salida esperada:**
```
Iniciando migración de base de datos...

⚠️ Encontrados 5 gastos sin cliente asignado.
Estos gastos necesitan un cliente antes de continuar.

Creando cliente por defecto...

Asignando cliente por defecto a 5 gasto(s)...
✓ Gastos actualizados con cliente por defecto.

Actualizando clientes existentes...
✓ 3 cliente(s) actualizados.

--- Verificación Final ---
Total de gastos: 15
Gastos con cliente: 15
Total de clientes: 4

✓ Migración completada exitosamente!

Ahora puedes ejecutar: python update_schema.py
```

---

## Paso 3: Actualizar Esquema (Opcional)

Si usas `update_schema.py` para reflejar cambios:

```bash
python update_schema.py
```

---

## Paso 4: Verificación Manual (Recomendado)

### Verificar gastos sin cliente:

```python
python
>>> from app import create_app
>>> from extensions import db
>>> from models.expense import Expense
>>> app = create_app()
>>> with app.app_context():
...     no_client = Expense.query.filter_by(client_id=None).count()
...     print(f"Gastos sin cliente: {no_client}")
```

**Resultado esperado:** `Gastos sin cliente: 0`

### Verificar cliente por defecto:

```python
>>> from models.company import Company
>>> with app.app_context():
...     default = Company.query.filter_by(rut='00.000.000-0').first()
...     if default:
...         print(f"Cliente por defecto: {default.name}")
...         print(f"Gastos asociados: {default.expenses.count()}")
```

---

## Resolución de Problemas

### Error: "NOT NULL constraint failed"

**Causa:** Hay gastos sin cliente y la migración falló.

**Solución:**
```bash
# Restaurar backup
cp database/expense.db.backup_YYYYMMDD database/expense.db

# Asignar clientes manualmente desde la app
# o re-ejecutar el script de migración
python migrate_client_required.py
```

### Gastos con cliente pendiente no se pueden aprobar

**Causa:** El flujo de aprobación en cascada está funcionando correctamente.

**Solución:**
1. Ir a `/admin/clients/approvals`
2. Aprobar o rechazar el cliente primero
3. Luego aprobar el gasto

### Cliente "No Especificado" aparece en listados

**Causa:** Se creó el cliente por defecto para gastos huérfanos.

**Solución:**
```python
# Opción 1: Cambiar nombre del cliente por defecto
>>> from models.company import Company
>>> with app.app_context():
...     default = Company.query.filter_by(rut='00.000.000-0').first()
...     default.name = "Gastos Internos"
...     db.session.commit()

# Opción 2: Reasignar gastos a un cliente real
# Desde la interfaz web, editar cada gasto y cambiar el cliente
```

---

## Nuevo Flujo de Trabajo

### Para Usuarios:

1. **Crear gasto con cliente existente:**
   - Ir a "Nuevo Gasto"
   - Seleccionar cliente de la lista
   - Completar formulario
   - Enviar

2. **Crear gasto con cliente nuevo:**
   - Ir a "Nuevo Gasto"
   - Seleccionar "Crear cliente nuevo"
   - Completar datos del cliente (RUT, Nombre, Email)
   - Completar formulario de gasto
   - Enviar

   **Resultado:** Cliente queda pendiente, gasto queda pendiente hasta aprobación del cliente.

### Para Administradores:

1. **Aprobar clientes pendientes:**
   - Ir a `/admin/clients/approvals`
   - Revisar clientes pendientes
   - Ver cantidad de gastos asociados
   - Aprobar o rechazar

   **Al aprobar:** Los gastos asociados quedan disponibles para aprobación normal
   **Al rechazar:** Los gastos asociados se rechazan automáticamente

2. **Aprobar gastos:**
   - Ir a `/approvals/pending`
   - Solo se pueden aprobar gastos con clientes activos
   - Gastos con cliente pendiente muestran advertencia

---

## Rollback (En caso de emergencia)

Si necesitas volver atrás:

```bash
# 1. Detener la aplicación
# 2. Restaurar backup
cp database/expense.db.backup_YYYYMMDD database/expense.db

# 3. Revertir cambios en código (usando git)
git checkout main  # o el branch anterior

# 4. Reiniciar aplicación
python app.py
```

---

## Preguntas Frecuentes

**¿Puedo tener gastos sin cliente?**
No, ahora el cliente es obligatorio para todos los gastos.

**¿Qué pasa con los gastos existentes sin cliente?**
El script de migración asigna automáticamente un cliente por defecto.

**¿Puedo crear múltiples clientes con el mismo RUT?**
No, el RUT es único. Si intentas crear un cliente con RUT existente, se usará el cliente existente.

**¿Qué pasa si rechazo un cliente con gastos asociados?**
Todos los gastos asociados se rechazan automáticamente.

**¿Puedo editar un cliente después de crearlo?**
No desde la app actualmente. Debes contactar a un administrador.

---

## Soporte

Si encuentras problemas durante la migración:
1. Revisa los logs de la aplicación
2. Verifica el backup de la BD
3. Consulta esta guía
4. Contacta al equipo de desarrollo con el error específico
