"""
Script para agregar la columna created_with_expense a la tabla clients
"""
import sqlite3
import os

def add_column():
    db_path = 'database/expense.db'

    if not os.path.exists(db_path):
        print(f"❌ Error: No se encontró la base de datos en {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'created_with_expense' in columns:
            print("✓ La columna 'created_with_expense' ya existe.")
            conn.close()
            return

        print("Agregando columna 'created_with_expense' a la tabla clients...")

        # Agregar columna
        cursor.execute("""
            ALTER TABLE clients
            ADD COLUMN created_with_expense BOOLEAN DEFAULT 0
        """)

        conn.commit()
        print("✓ Columna agregada exitosamente!")

        # Actualizar registros existentes
        cursor.execute("UPDATE clients SET created_with_expense = 0 WHERE created_with_expense IS NULL")
        conn.commit()
        print("✓ Registros existentes actualizados.")

        # Verificar
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        print(f"\n✓ Total de clientes en la base de datos: {count}")

        conn.close()
        print("\n✅ Migración completada exitosamente!")
        print("Ahora puedes reiniciar la aplicación: python app.py")

    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        if conn:
            conn.close()

if __name__ == "__main__":
    add_column()
