from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.expense import Expense
from models.user import User
from models.approval import Approval
from models.company import Company, Area, ExpenseCategory
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import or_

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def api_response(data=None, message=None, status=200, error=None):
    """Helper para respuestas consistentes de la API"""
    response = {}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if error:
        response['error'] = error
        response['success'] = False
    else:
        response['success'] = True

    return jsonify(response), status


def serialize_expense(expense):
    """Serializar un objeto Expense a dict"""
    return {
        'id': expense.id,
        'user_id': expense.user_id,
        'user_name': expense.user.full_name if expense.user else None,
        'client_id': expense.client_id,
        'client_name': expense.client.name if expense.client else None,
        'amount': float(expense.amount),
        'expense_date': expense.expense_date.isoformat(),
        'category': expense.category,
        'reason': expense.reason,
        'receipt_image': expense.receipt_image,
        'latitude': float(expense.latitude) if expense.latitude else None,
        'longitude': float(expense.longitude) if expense.longitude else None,
        'address': expense.address,
        'status': expense.status,
        'created_at': expense.created_at.isoformat(),
        'updated_at': expense.updated_at.isoformat() if expense.updated_at else None,
        'ocr_data': expense.ocr_data
    }


def serialize_user(user):
    """Serializar un objeto User a dict"""
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'role': user.role,
        'area_id': user.area_id,
        'area_name': user.area.name if user.area else None,
        'supervisor_id': user.supervisor_id,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }


# ============= EXPENSES ENDPOINTS =============

@api_bp.route('/expenses', methods=['GET'])
@login_required
def get_expenses():
    """
    GET /api/v1/expenses
    Query params: page, per_page, status, category, user_id
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category = request.args.get('category')
    user_id = request.args.get('user_id', type=int)

    # Base query según rol
    if current_user.role == 'admin':
        query = Expense.query
    elif current_user.role == 'supervisor':
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates] + [current_user.id]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))
    else:
        query = Expense.query.filter_by(user_id=current_user.id)

    # Aplicar filtros
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if user_id and current_user.role in ['admin', 'supervisor']:
        query = query.filter_by(user_id=user_id)

    # Paginación
    pagination = query.order_by(Expense.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return api_response(data={
        'expenses': [serialize_expense(e) for e in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page
    })


@api_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@login_required
def get_expense(expense_id):
    """GET /api/v1/expenses/<id>"""
    expense = Expense.query.get_or_404(expense_id)

    # Verificar permisos
    if current_user.role == 'user' and expense.user_id != current_user.id:
        return api_response(error='No tienes permiso para ver este gasto', status=403)

    return api_response(data=serialize_expense(expense))


@api_bp.route('/expenses', methods=['POST'])
@login_required
def create_expense():
    """
    POST /api/v1/expenses
    Body: { amount, category, reason, client_id, expense_date, latitude, longitude, receipt_image }
    """
    data = request.get_json()

    required_fields = ['amount', 'category', 'reason', 'receipt_image']
    for field in required_fields:
        if field not in data:
            return api_response(error=f'Campo requerido: {field}', status=400)

    try:
        expense = Expense(
            user_id=current_user.id,
            amount=float(data['amount']),
            category=data['category'],
            reason=data['reason'],
            receipt_image=data['receipt_image'],
            client_id=data.get('client_id'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address'),
            expense_date=datetime.fromisoformat(data['expense_date']) if 'expense_date' in data else datetime.now(),
            status='pending'
        )

        db.session.add(expense)
        db.session.commit()

        return api_response(
            data=serialize_expense(expense),
            message='Gasto creado exitosamente',
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


@api_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id):
    """PUT /api/v1/expenses/<id>"""
    expense = Expense.query.get_or_404(expense_id)

    # Solo el creador o admin pueden modificar
    if expense.user_id != current_user.id and current_user.role != 'admin':
        return api_response(error='No tienes permiso para modificar este gasto', status=403)

    # Solo se pueden editar gastos pendientes
    if expense.status != 'pending':
        return api_response(error='Solo se pueden editar gastos pendientes', status=400)

    data = request.get_json()

    # Actualizar campos permitidos
    if 'amount' in data:
        expense.amount = float(data['amount'])
    if 'category' in data:
        expense.category = data['category']
    if 'reason' in data:
        expense.reason = data['reason']
    if 'client_id' in data:
        expense.client_id = data['client_id']

    expense.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        return api_response(data=serialize_expense(expense), message='Gasto actualizado')
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


@api_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    """DELETE /api/v1/expenses/<id>"""
    expense = Expense.query.get_or_404(expense_id)

    # Solo el creador o admin pueden eliminar
    if expense.user_id != current_user.id and current_user.role != 'admin':
        return api_response(error='No tienes permiso para eliminar este gasto', status=403)

    # Solo se pueden eliminar gastos pendientes
    if expense.status != 'pending':
        return api_response(error='Solo se pueden eliminar gastos pendientes', status=400)

    try:
        db.session.delete(expense)
        db.session.commit()
        return api_response(message='Gasto eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


# ============= APPROVALS ENDPOINTS =============

@api_bp.route('/expenses/<int:expense_id>/approve', methods=['POST'])
@login_required
def approve_expense(expense_id):
    """POST /api/v1/expenses/<id>/approve"""
    if current_user.role not in ['supervisor', 'admin']:
        return api_response(error='No tienes permisos para aprobar gastos', status=403)

    expense = Expense.query.get_or_404(expense_id)

    if expense.status != 'pending':
        return api_response(error='Este gasto ya fue procesado', status=400)

    data = request.get_json() or {}
    comments = data.get('comments', '')

    try:
        approval = Approval(
            expense_id=expense.id,
            approver_id=current_user.id,
            action='approved',
            comments=comments
        )

        expense.status = 'approved'
        expense.updated_at = datetime.utcnow()

        db.session.add(approval)
        db.session.commit()

        return api_response(
            data=serialize_expense(expense),
            message='Gasto aprobado exitosamente'
        )
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


@api_bp.route('/expenses/<int:expense_id>/reject', methods=['POST'])
@login_required
def reject_expense(expense_id):
    """POST /api/v1/expenses/<id>/reject"""
    if current_user.role not in ['supervisor', 'admin']:
        return api_response(error='No tienes permisos para rechazar gastos', status=403)

    expense = Expense.query.get_or_404(expense_id)

    if expense.status != 'pending':
        return api_response(error='Este gasto ya fue procesado', status=400)

    data = request.get_json() or {}
    comments = data.get('comments', '')

    if not comments:
        return api_response(error='Debes proporcionar un motivo para rechazar', status=400)

    try:
        approval = Approval(
            expense_id=expense.id,
            approver_id=current_user.id,
            action='rejected',
            comments=comments
        )

        expense.status = 'rejected'
        expense.updated_at = datetime.utcnow()

        db.session.add(approval)
        db.session.commit()

        return api_response(
            data=serialize_expense(expense),
            message='Gasto rechazado'
        )
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


# ============= USERS ENDPOINTS (Admin only) =============

@api_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """GET /api/v1/users (Admin only)"""
    if current_user.role != 'admin':
        return api_response(error='Acceso denegado', status=403)

    users = User.query.all()
    return api_response(data=[serialize_user(u) for u in users])


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """GET /api/v1/users/<id>"""
    if current_user.role != 'admin' and current_user.id != user_id:
        return api_response(error='Acceso denegado', status=403)

    user = User.query.get_or_404(user_id)
    return api_response(data=serialize_user(user))


@api_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """POST /api/v1/users (Admin only)"""
    if current_user.role != 'admin':
        return api_response(error='Acceso denegado', status=403)

    data = request.get_json()
    required_fields = ['email', 'first_name', 'last_name', 'password', 'role']

    for field in required_fields:
        if field not in data:
            return api_response(error=f'Campo requerido: {field}', status=400)

    if User.query.filter_by(email=data['email']).first():
        return api_response(error='El email ya está registrado', status=400)

    try:
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            area_id=data.get('area_id'),
            supervisor_id=data.get('supervisor_id')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return api_response(
            data=serialize_user(user),
            message='Usuario creado exitosamente',
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(error=str(e), status=500)


# ============= STATS ENDPOINTS =============

@api_bp.route('/stats/summary', methods=['GET'])
@login_required
def get_stats_summary():
    """GET /api/v1/stats/summary"""
    if current_user.role == 'admin':
        query = Expense.query
    elif current_user.role == 'supervisor':
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates] + [current_user.id]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))
    else:
        query = Expense.query.filter_by(user_id=current_user.id)

    total = query.count()
    pending = query.filter_by(status='pending').count()
    approved = query.filter_by(status='approved').count()
    rejected = query.filter_by(status='rejected').count()

    total_amount = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.id.in_([e.id for e in query.all()])
    ).scalar() or 0

    return api_response(data={
        'total_expenses': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'total_amount': float(total_amount)
    })


# ============= COMPANIES/CLIENTS ENDPOINTS =============

@api_bp.route('/clients', methods=['GET'])
@login_required
def get_clients():
    """GET /api/v1/clients"""
    clients = Company.query.filter_by(is_active=True).all()
    return api_response(data=[{
        'id': c.id,
        'rut': c.rut,
        'name': c.name,
        'contact_email': c.contact_email,
        'status': c.status
    } for c in clients])


# ============= CATEGORIES ENDPOINTS =============

@api_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """GET /api/v1/categories"""
    categories = ExpenseCategory.query.filter_by(is_active=True).all()
    return api_response(data=[{
        'id': c.id,
        'name': c.name,
        'requires_client': c.requires_client,
        'max_amount': float(c.max_amount) if c.max_amount else None
    } for c in categories])


# ============= HEALTH CHECK =============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """GET /api/v1/health"""
    return api_response(data={'status': 'ok', 'version': '1.0'})
