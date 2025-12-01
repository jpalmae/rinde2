"""
Tests para API REST
"""
import pytest
import json
from models.user import User
from models.expense import Expense
from models.company import Company
from datetime import datetime


def login(client, email, password):
    """Helper para hacer login"""
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


class TestHealthCheck:
    """Tests para health check"""

    def test_health_check(self, client):
        """Test endpoint de salud"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'ok'


class TestExpensesAPI:
    """Tests para endpoints de gastos"""

    def test_get_expenses_without_login(self, client):
        """Test obtener gastos sin autenticación"""
        response = client.get('/api/v1/expenses')
        assert response.status_code == 401

    def test_get_expenses_as_user(self, client, app, init_database):
        """Test obtener gastos como usuario normal"""
        with client:
            login(client, 'user@test.com', 'user123')

            response = client.get('/api/v1/expenses')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'expenses' in data['data']

    def test_create_expense(self, client, app, init_database):
        """Test crear gasto"""
        with client:
            login(client, 'user@test.com', 'user123')

        with app.app_context():
            company = Company.query.first()

            expense_data = {
                'amount': 10000,
                'category': 'Transporte',
                'reason': 'Taxi al cliente',
                'receipt_image': 'test.jpg',
                'latitude': -33.4489,
                'longitude': -70.6693,
                'expense_date': datetime.now().isoformat(),
                'client_id': company.id
            }

            response = client.post('/api/v1/expenses',
                                  data=json.dumps(expense_data),
                                  content_type='application/json')

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['amount'] == 10000

    def test_create_expense_missing_fields(self, client, app, init_database):
        """Test crear gasto con campos faltantes"""
        with client:
            login(client, 'user@test.com', 'user123')

            expense_data = {
                'amount': 10000
                # Faltan campos requeridos
            }

            response = client.post('/api/v1/expenses',
                                  data=json.dumps(expense_data),
                                  content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False

    def test_get_expense_by_id(self, client, app, init_database):
        """Test obtener gasto por ID"""
        with client:
            with app.app_context():
                from extensions import db

                # Crear gasto
                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'user@test.com', 'user123')
            response = client.get(f'/api/v1/expenses/{expense_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['id'] == expense_id

    def test_update_expense(self, client, app, init_database):
        """Test actualizar gasto"""
        with client:
            with app.app_context():
                from extensions import db

                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'user@test.com', 'user123')

            update_data = {
                'amount': 15000,
                'reason': 'Updated reason'
            }

            response = client.put(f'/api/v1/expenses/{expense_id}',
                                data=json.dumps(update_data),
                                content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['amount'] == 15000

    def test_delete_expense(self, client, app, init_database):
        """Test eliminar gasto"""
        with client:
            with app.app_context():
                from extensions import db

                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'user@test.com', 'user123')
            response = client.delete(f'/api/v1/expenses/{expense_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True


class TestApprovalsAPI:
    """Tests para endpoints de aprobaciones"""

    def test_approve_expense_as_supervisor(self, client, app, init_database):
        """Test aprobar gasto como supervisor"""
        with client:
            with app.app_context():
                from extensions import db

                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'supervisor@test.com', 'super123')

            approval_data = {
                'comments': 'Aprobado'
            }

            response = client.post(f'/api/v1/expenses/{expense_id}/approve',
                                  data=json.dumps(approval_data),
                                  content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['status'] == 'approved'

    def test_reject_expense_without_comments(self, client, app, init_database):
        """Test rechazar gasto sin comentarios"""
        with client:
            with app.app_context():
                from extensions import db

                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'supervisor@test.com', 'super123')

            response = client.post(f'/api/v1/expenses/{expense_id}/reject',
                                  data=json.dumps({}),
                                  content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False

    def test_approve_expense_without_permissions(self, client, app, init_database):
        """Test aprobar gasto sin permisos"""
        with client:
            with app.app_context():
                from extensions import db

                user = User.query.filter_by(email="user@test.com").first()
                client_obj = Company.query.first()
                expense = Expense(
                    user_id=user.id,
                    client_id=client_obj.id,
                    amount=10000,
                    category="Transporte",
                    reason="Test",
                    receipt_image="test.jpg",
                    expense_date=datetime.now(),
                    status="pending"
                )
                db.session.add(expense)
                db.session.commit()
                expense_id = expense.id

            login(client, 'user@test.com', 'user123')

            response = client.post(f'/api/v1/expenses/{expense_id}/approve',
                                  data=json.dumps({}),
                                  content_type='application/json')

            assert response.status_code == 403


class TestUsersAPI:
    """Tests para endpoints de usuarios"""

    def test_get_users_as_admin(self, client, app, init_database):
        """Test obtener usuarios como admin"""
        with client:
            login(client, 'admin@test.com', 'admin123')
            response = client.get('/api/v1/users')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) >= 3

    def test_get_users_as_non_admin(self, client, app, init_database):
        """Test obtener usuarios como no-admin"""
        with client:
            login(client, 'user@test.com', 'user123')
            response = client.get('/api/v1/users')

            assert response.status_code == 403

    def test_create_user_as_admin(self, client, app, init_database):
        """Test crear usuario como admin"""
        with client:
            login(client, 'admin@test.com', 'admin123')

            user_data = {
                'email': 'newuser@test.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'password123',
                'role': 'user'
            }

            response = client.post('/api/v1/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['email'] == 'newuser@test.com'


class TestStatsAPI:
    """Tests para endpoints de estadísticas"""

    def test_get_stats_summary(self, client, app, init_database):
        """Test obtener resumen de estadísticas"""
        with client:
            login(client, 'user@test.com', 'user123')
            response = client.get('/api/v1/stats/summary')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'total_expenses' in data['data']
            assert 'pending' in data['data']
            assert 'approved' in data['data']