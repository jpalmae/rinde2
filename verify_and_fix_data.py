"""
Script para verificar y corregir datos antes de hacer client_id obligatorio
"""
import sqlite3
import os

def verify_and_fix():
    db_path = 'database/expense.db'

    if not os.path.exists(db_path):
        print(f"❌ Error: No se encontró la base de datos en {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=== Verificación de Datos ===\n")

        # 1. Verificar gastos sin cliente
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE client_id IS NULL")
        expenses_without_client = cursor.fetchone()[0]

        print(f"Gastos sin cliente: {expenses_without_client}")

        if expenses_without_client > 0:
            print(f"\n⚠️ Hay {expenses_without_client} gasto(s) sin cliente asignado.")
            print("Creando cliente por defecto...")

            # Verificar si existe el cliente por defecto
            cursor.execute("SELECT id FROM clients WHERE rut = '00.000.000-0'")
            result = cursor.fetchone()

            if result:
                default_client_id = result[0]
                print(f"✓ Cliente por defecto ya existe (ID: {default_client_id})")
            else:
                # Crear cliente por defecto
                cursor.execute("""
                    INSERT INTO clients (rut, name, contact_email, status, is_active, created_with_expense)
                    VALUES ('00.000.000-0', 'Cliente No Especificado', '', 'active', 1, 0)
                """)
                default_client_id = cursor.lastrowid
                print(f"✓ Cliente por defecto creado (ID: {default_client_id})")

            # Asignar cliente por defecto a gastos sin cliente
            cursor.execute("""
                UPDATE expenses
                SET client_id = ?
                WHERE client_id IS NULL
            """, (default_client_id,))

            conn.commit()
            print(f"✓ {expenses_without_client} gasto(s) actualizados con cliente por defecto.")

        else:
            print("✓ Todos los gastos tienen cliente asignado.")

        # 2. Verificar total de clientes
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        print(f"\nTotal de clientes: {total_clients}")

        # 3. Verificar total de gastos
        cursor.execute("SELECT COUNT(*) FROM expenses")
        total_expenses = cursor.fetchone()[0]
        print(f"Total de gastos: {total_expenses}")

        # 4. Verificar gastos por estado
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM expenses
            GROUP BY status
        """)
        print("\nGastos por estado:")
        for status, count in cursor.fetchall():
            print(f"  - {status}: {count}")

        # 5. Verificación final
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE client_id IS NULL")
        final_check = cursor.fetchone()[0]

        print("\n=== Verificación Final ===")
        if final_check == 0:
            print("✅ Todos los gastos tienen cliente asignado.")
            print("\n🚀 La base de datos está lista.")
            print("Puedes reiniciar la aplicación: python app.py")
        else:
            print(f"❌ Aún hay {final_check} gasto(s) sin cliente.")
            print("Por favor, revisa los datos manualmente.")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_and_fix()
