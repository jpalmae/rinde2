from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.company import Area, Company
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('index'))

# --- Dashboard ---
@admin_bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html')

# --- Users Management ---
@admin_bp.route('/users')
def users_list():
    users = User.query.all()
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
def users_new():
    areas = Area.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        area_id = request.form.get('area_id')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
        else:
            user = User(email=email, first_name=first_name, last_name=last_name, role=role, area_id=area_id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('admin.users_list'))
    
    return render_template('admin/users/form.html', areas=areas)

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
def users_edit(id):
    user = User.query.get_or_404(id)
    areas = Area.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role')
        user.area_id = request.form.get('area_id')
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
            
        db.session.commit()
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/users/form.html', user=user, areas=areas)

# --- Areas Management ---
@admin_bp.route('/areas')
def areas_list():
    areas = Area.query.all()
    return render_template('admin/areas/list.html', areas=areas)

@admin_bp.route('/areas/new', methods=['GET', 'POST'])
def areas_new():
    if request.method == 'POST':
        name = request.form.get('name')
        budget = request.form.get('budget_monthly')
        
        area = Area(name=name, budget_monthly=budget)
        db.session.add(area)
        db.session.commit()
        flash('Área creada exitosamente.', 'success')
        return redirect(url_for('admin.areas_list'))
        
    return render_template('admin/areas/form.html')

@admin_bp.route('/areas/<int:id>/edit', methods=['GET', 'POST'])
def areas_edit(id):
    area = Area.query.get_or_404(id)
    
    if request.method == 'POST':
        area.name = request.form.get('name')
        area.budget_monthly = request.form.get('budget_monthly')
        db.session.commit()
        flash('Área actualizada exitosamente.', 'success')
        return redirect(url_for('admin.areas_list'))
        
    return render_template('admin/areas/form.html', area=area)

# --- Client Approvals ---
@admin_bp.route('/clients/approvals')
def clients_approvals():
    from models.expense import Expense

    pending_clients = Company.query.filter_by(status='pending').all()

    # Agregar contador de gastos asociados a cada cliente
    clients_with_expenses = []
    for client in pending_clients:
        expense_count = Expense.query.filter_by(client_id=client.id).count()
        clients_with_expenses.append({
            'client': client,
            'expense_count': expense_count
        })

    return render_template('admin/clients/approvals.html', clients_data=clients_with_expenses)

@admin_bp.route('/clients/<int:id>/approve', methods=['POST'])
def clients_approve(id):
    from models.expense import Expense

    client = Company.query.get_or_404(id)
    client.status = 'active'
    client.is_active = True

    # Contar gastos asociados pendientes
    pending_expenses = Expense.query.filter_by(client_id=client.id, status='pending').count()

    db.session.commit()

    flash(f'Cliente {client.name} aprobado.', 'success')

    # Notificar sobre gastos pendientes asociados
    if pending_expenses > 0:
        flash(f'Hay {pending_expenses} gasto(s) asociado(s) a este cliente que ahora pueden ser aprobados.', 'info')

    return redirect(url_for('admin.clients_approvals'))

@admin_bp.route('/clients/<int:id>/reject', methods=['POST'])
def clients_reject(id):
    from models.expense import Expense

    client = Company.query.get_or_404(id)

    # Contar gastos asociados pendientes
    pending_expenses = Expense.query.filter_by(client_id=client.id, status='pending').all()

    # Rechazar cliente
    client.status = 'rejected'
    client.is_active = False

    # Rechazar automáticamente gastos asociados pendientes
    rejected_count = 0
    for expense in pending_expenses:
        expense.status = 'rejected'
        rejected_count += 1

    db.session.commit()

    flash(f'Cliente {client.name} rechazado.', 'warning')
    if rejected_count > 0:
        flash(f'{rejected_count} gasto(s) asociado(s) fueron rechazados automáticamente.', 'info')

    return redirect(url_for('admin.clients_approvals'))
