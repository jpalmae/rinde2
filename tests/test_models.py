"""
Tests para modelos de datos
"""
import pytest
from models.user import User
from models.expense import Expense
from models.company import Company, Area
from datetime import datetime


class TestUserModel:
    """Tests para el modelo User"""

    def test_user_creation(self, app, init_database):
        """Test crear usuario"""
        with app.app_context():
            user = User.query.filter_by(email="user@test.com").first()
            assert user is not None
            assert user.first_name == "User"
            assert user.last_name == "Test"
            assert user.full_name == "User Test"
            assert user.role == "user"

    def test_user_password(self, app, init_database):
        """Test hash y verificación de contraseña"""
        with app.app_context():
            user = User.query.filter_by(email="user@test.com").first()
            assert user.check_password("user123") is True
            assert user.check_password("wrong") is False

    def test_user_supervisor_relationship(self, app, init_database):
        """Test relación supervisor-subordinado"""
        with app.app_context():
            user = User.query.filter_by(email="user@test.com").first()
            supervisor = User.query.filter_by(email="supervisor@test.com").first()

            assert user.supervisor_id == supervisor.id
            assert user.supervisor == supervisor
            assert user in supervisor.subordinates


class TestExpenseModel:
    """Tests para el modelo Expense"""

    def test_expense_creation(self, app, init_database):
        """Test crear gasto"""
        with app.app_context():
            from extensions import db

            user = User.query.filter_by(email="user@test.com").first()
            client = Company.query.first()
            expense = Expense(
                user_id=user.id,
                client_id=client.id,
                amount=10000,
                category="Transporte",
                reason="Taxi al cliente",
                receipt_image="test.jpg",
                expense_date=datetime.now(),
                status="pending"
            )

            db.session.add(expense)
            db.session.commit()

            assert expense.id is not None
            assert expense.amount == 10000
            assert expense.status == "pending"
            assert expense.user == user

    def test_expense_with_client(self, app, init_database):
        """Test gasto asociado a cliente"""
        with app.app_context():
            from extensions import db

            user = User.query.filter_by(email="user@test.com").first()
            client = Company.query.first()

            expense = Expense(
                user_id=user.id,
                client_id=client.id,
                amount=10000,
                category="Transporte",
                reason="Visita a cliente",
                receipt_image="test.jpg",
                expense_date=datetime.now(),
                status="pending"
            )

            db.session.add(expense)
            db.session.commit()

            assert expense.client == client
            assert expense in client.expenses


class TestCompanyModel:
    """Tests para el modelo Company"""

    def test_company_creation(self, app, init_database):
        """Test crear cliente"""
        with app.app_context():
            company = Company.query.first()
            assert company is not None
            assert company.name == "Cliente Test"
            assert company.rut == "76.123.456-7"
            assert company.status == "active"
            assert company.is_active is True


class TestAreaModel:
    """Tests para el modelo Area"""

    def test_area_creation(self, app, init_database):
        """Test crear área"""
        with app.app_context():
            area = Area.query.first()
            assert area is not None
            assert area.name == "IT"
            assert area.budget_monthly == 1000000

    def test_area_users_relationship(self, app, init_database):
        """Test relación área-usuarios"""
        with app.app_context():
            area = Area.query.first()
            users = area.users.all()
            assert len(users) > 0
            assert all(u.area_id == area.id for u in users)
