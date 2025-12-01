"""
Configuración de pytest y fixtures compartidos
"""
import pytest
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models.user import User
from models.company import Area, Company, ExpenseCategory
from config import Config


class TestConfig(Config):
    """Configuración para tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture(scope='function')
def app():
    """Crear aplicación de prueba"""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """CLI runner para tests de comandos"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def init_database(app):
    """Inicializar base de datos con datos de prueba"""
    with app.app_context():
        # Crear área
        area = Area(name="IT", budget_monthly=1000000)
        db.session.add(area)
        db.session.commit()

        # Crear usuarios
        admin = User(
            email="admin@test.com",
            first_name="Admin",
            last_name="Test",
            role="admin",
            area_id=area.id
        )
        admin.set_password("admin123")

        supervisor = User(
            email="supervisor@test.com",
            first_name="Supervisor",
            last_name="Test",
            role="supervisor",
            area_id=area.id
        )
        supervisor.set_password("super123")

        user = User(
            email="user@test.com",
            first_name="User",
            last_name="Test",
            role="user",
            area_id=area.id,
            supervisor_id=None  # Se asignará después
        )
        user.set_password("user123")

        db.session.add_all([admin, supervisor, user])
        db.session.commit()

        # Asignar supervisor
        user.supervisor_id = supervisor.id
        db.session.commit()

        # Crear categorías
        categories = [
            ExpenseCategory(name="Transporte", max_amount=50000),
            ExpenseCategory(name="Alimentación", max_amount=20000),
        ]
        db.session.add_all(categories)

        # Crear cliente
        client = Company(
            rut="76.123.456-7",
            name="Cliente Test",
            contact_email="test@test.com",
            status="active",
            is_active=True
        )
        db.session.add(client)

        db.session.commit()

        yield db

        db.session.remove()
