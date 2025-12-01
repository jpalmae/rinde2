from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.expense import Expense
from models.approval import Approval
from models.user import User
from datetime import datetime

approvals_bp = Blueprint('approvals', __name__, url_prefix='/approvals')


def can_approve_expense(user, expense):
    """
    Verifica si un usuario puede aprobar un gasto
    - Admins pueden aprobar todo
    - Supervisores pueden aprobar gastos de sus subordinados
    - No se puede aprobar gastos propios
    """
    if user.id == expense.user_id:
        return False

    if user.role == 'admin':
        return True

    if user.role == 'supervisor':
        # Verificar si el creador del gasto es subordinado
        expense_owner = User.query.get(expense.user_id)
        if expense_owner and expense_owner.supervisor_id == user.id:
            return True

    return False


@approvals_bp.route('/pending')
@login_required
def pending():
    """
    Lista de gastos pendientes que el usuario puede aprobar
    """
    if current_user.role not in ['supervisor', 'admin']:
        flash('No tienes permisos para aprobar gastos.', 'error')
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    from flask import current_app
    per_page = current_app.config.get('EXPENSES_PER_PAGE', 20)

    # Obtener gastos pendientes que el usuario puede aprobar
    if current_user.role == 'admin':
        # Admin ve todos los gastos pendientes
        query = Expense.query.filter_by(status='pending')
    else:
        # Supervisor ve solo gastos de sus subordinados
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        query = Expense.query.filter(
            Expense.user_id.in_(subordinate_ids),
            Expense.status == 'pending'
        )

    pagination = query.order_by(Expense.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Filtrar gastos que el usuario puede aprobar
    approvable_expenses = [exp for exp in pagination.items if can_approve_expense(current_user, exp)]

    return render_template('approvals/pending.html',
                         expenses=approvable_expenses,
                         pagination=pagination)


@approvals_bp.route('/history')
@login_required
def history():
    """
    Historial de aprobaciones realizadas por el usuario
    """
    if current_user.role not in ['supervisor', 'admin']:
        flash('No tienes permisos para ver este contenido.', 'error')
        return redirect(url_for('index'))

    approvals = Approval.query.filter_by(approver_id=current_user.id).order_by(
        Approval.created_at.desc()
    ).all()

    return render_template('approvals/history.html', approvals=approvals)


@approvals_bp.route('/<int:expense_id>/approve', methods=['POST'])
@login_required
def approve(expense_id):
    """
    Aprobar un gasto
    """
    expense = Expense.query.get_or_404(expense_id)

    # Verificar permisos
    if not can_approve_expense(current_user, expense):
        flash('No tienes permisos para aprobar este gasto.', 'error')
        return redirect(url_for('approvals.pending'))

    # Verificar que esté pendiente
    if expense.status != 'pending':
        flash('Este gasto ya fue procesado.', 'warning')
        return redirect(url_for('approvals.pending'))

    comments = request.form.get('comments', '')

    # Crear aprobación
    approval = Approval(
        expense_id=expense.id,
        approver_id=current_user.id,
        action='approved',
        comments=comments
    )

    # Actualizar estado del gasto
    expense.status = 'approved'
    expense.updated_at = datetime.utcnow()

    db.session.add(approval)
    db.session.commit()

    flash(f'Gasto #{expense.id} aprobado exitosamente.', 'success')
    return redirect(url_for('approvals.pending'))


@approvals_bp.route('/<int:expense_id>/reject', methods=['POST'])
@login_required
def reject(expense_id):
    """
    Rechazar un gasto
    """
    expense = Expense.query.get_or_404(expense_id)

    # Verificar permisos
    if not can_approve_expense(current_user, expense):
        flash('No tienes permisos para rechazar este gasto.', 'error')
        return redirect(url_for('approvals.pending'))

    # Verificar que esté pendiente
    if expense.status != 'pending':
        flash('Este gasto ya fue procesado.', 'warning')
        return redirect(url_for('approvals.pending'))

    comments = request.form.get('comments', '')

    if not comments:
        flash('Debes proporcionar un motivo para rechazar el gasto.', 'error')
        return redirect(url_for('approvals.pending'))

    # Crear aprobación (con action='rejected')
    approval = Approval(
        expense_id=expense.id,
        approver_id=current_user.id,
        action='rejected',
        comments=comments
    )

    # Actualizar estado del gasto
    expense.status = 'rejected'
    expense.updated_at = datetime.utcnow()

    db.session.add(approval)
    db.session.commit()

    flash(f'Gasto #{expense.id} rechazado.', 'success')
    return redirect(url_for('approvals.pending'))


@approvals_bp.route('/<int:expense_id>/detail')
@login_required
def detail(expense_id):
    """
    Detalle de un gasto para aprobación
    """
    expense = Expense.query.get_or_404(expense_id)

    # Verificar permisos
    if not can_approve_expense(current_user, expense) and current_user.id != expense.user_id:
        flash('No tienes permisos para ver este gasto.', 'error')
        return redirect(url_for('index'))

    return render_template('approvals/detail.html', expense=expense)


@approvals_bp.route('/all')
@login_required
def all_expenses():
    """
    Ver todos los gastos (aprobados, rechazados, pendientes)
    Solo para supervisores y admins
    """
    if current_user.role not in ['supervisor', 'admin']:
        flash('No tienes permisos para ver este contenido.', 'error')
        return redirect(url_for('index'))

    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    from flask import current_app
    per_page = current_app.config.get('EXPENSES_PER_PAGE', 20)

    if current_user.role == 'admin':
        # Admin ve todos los gastos
        query = Expense.query
    else:
        # Supervisor ve solo gastos de sus subordinados
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))

    # Aplicar filtro de estado
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(Expense.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('approvals/all.html',
                         expenses=pagination.items,
                         pagination=pagination,
                         status_filter=status_filter)
