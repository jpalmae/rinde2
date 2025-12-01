"""
Script de migración para hacer el campo client_id obligatorio
y agregar campo created_with_expense
"""
from app import create_app
from extensions import db
from models.company import Company
from models.expense import Expense

app = create_app()

def migrate():
    with app.app_context():
        print("Iniciando migración de base de datos...")

        # 1. Verificar si hay gastos sin cliente
        expenses_without_client = Expense.query.filter(
            (Expense.client_id == None) | (Expense.client_id == '')
        ).all()

        if expenses_without_client:
            print(f"\n⚠️ Encontrados {len(expenses_without_client)} gastos sin cliente asignado.")
            print("Estos gastos necesitan un cliente antes de continuar.")

            # Buscar o crear un cliente "Por Defecto"
            default_client = Company.query.filter_by(rut='00.000.000-0').first()

            if not default_client:
                print("\nCreando cliente por defecto...")
                default_client = Company(
                    rut='00.000.000-0',
                    name='Cliente No Especificado',
                    contact_email='',
                    status='active',
                    is_active=True,
                    created_with_expense=False
                )
                db.session.add(default_client)
                db.session.flush()

            # Asignar cliente por defecto a gastos sin cliente
            print(f"\nAsignando cliente por defecto a {len(expenses_without_client)} gasto(s)...")
            for expense in expenses_without_client:
                expense.client_id = default_client.id

            db.session.commit()
            print("✓ Gastos actualizados con cliente por defecto.")

        # 2. Agregar campo created_with_expense a clientes existentes
        print("\nActualizando clientes existentes...")
        clients = Company.query.all()
        for client in clients:
            if not hasattr(client, 'created_with_expense') or client.created_with_expense is None:
                client.created_with_expense = False

        db.session.commit()
        print(f"✓ {len(clients)} cliente(s) actualizados.")

        # 3. Verificación final
        print("\n--- Verificación Final ---")
        total_expenses = Expense.query.count()
        expenses_with_client = Expense.query.filter(Expense.client_id != None).count()
        total_clients = Company.query.count()

        print(f"Total de gastos: {total_expenses}")
        print(f"Gastos con cliente: {expenses_with_client}")
        print(f"Total de clientes: {total_clients}")

        if total_expenses == expenses_with_client:
            print("\n✓ Migración completada exitosamente!")
            print("\nAhora puedes ejecutar: python update_schema.py")
        else:
            print(f"\n⚠️ Aún hay {total_expenses - expenses_with_client} gastos sin cliente.")
            print("Por favor, asigna manualmente los clientes antes de continuar.")

if __name__ == "__main__":
    migrate()
