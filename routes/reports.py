from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.expense import Expense
from models.user import User
from models.company import Area, ExpenseCategory
from models.approval import Approval
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def require_supervisor_or_admin():
    """Helper to check if user has required permissions"""
    if current_user.role not in ['supervisor', 'admin']:
        flash('No tienes permisos para ver reportes.', 'error')
        return redirect(url_for('index'))
    return None


@reports_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal con métricas generales
    """
    redirect_result = require_supervisor_or_admin()
    if redirect_result:
        return redirect_result

    # Determinar qué gastos puede ver el usuario
    if current_user.role == 'admin':
        expense_query = Expense.query
        user_query = User.query
    else:
        # Supervisor ve solo gastos de sus subordinados
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        expense_query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))
        user_query = User.query.filter(User.id.in_(subordinate_ids))

    # Métricas generales
    total_expenses = expense_query.count()
    pending_expenses = expense_query.filter_by(status='pending').count()
    approved_expenses = expense_query.filter_by(status='approved').count()
    rejected_expenses = expense_query.filter_by(status='rejected').count()

    # Montos totales
    total_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.id.in_([e.id for e in expense_query.all()])
    ).scalar() or 0

    approved_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.id.in_([e.id for e in expense_query.filter_by(status='approved').all()])
    ).scalar() or 0

    # Gastos del mes actual
    current_month = datetime.now().month
    current_year = datetime.now().year
    month_expenses = expense_query.filter(
        extract('month', Expense.expense_date) == current_month,
        extract('year', Expense.expense_date) == current_year
    ).count()

    month_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.id.in_([e.id for e in expense_query.filter(
            extract('month', Expense.expense_date) == current_month,
            extract('year', Expense.expense_date) == current_year
        ).all()])
    ).scalar() or 0

    # Top 5 usuarios con más gastos (solo para admin)
    top_users = []
    if current_user.role == 'admin':
        top_users = db.session.query(
            User.first_name, User.last_name,
            func.count(Expense.id).label('count'),
            func.sum(Expense.amount).label('total')
        ).join(Expense).group_by(User.id).order_by(
            func.sum(Expense.amount).desc()
        ).limit(5).all()

    # Gastos por categoría
    expenses_by_category = db.session.query(
        Expense.category,
        func.count(Expense.id).label('count'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.id.in_([e.id for e in expense_query.all()])
    ).group_by(Expense.category).all()

    # Gastos recientes
    recent_expenses = expense_query.order_by(Expense.created_at.desc()).limit(10).all()

    return render_template('reports/dashboard.html',
                         total_expenses=total_expenses,
                         pending_expenses=pending_expenses,
                         approved_expenses=approved_expenses,
                         rejected_expenses=rejected_expenses,
                         total_amount=total_amount,
                         approved_amount=approved_amount,
                         month_expenses=month_expenses,
                         month_amount=month_amount,
                         top_users=top_users,
                         expenses_by_category=expenses_by_category,
                         recent_expenses=recent_expenses)


@reports_bp.route('/by-period')
@login_required
def by_period():
    """
    Reporte de gastos por período
    """
    redirect_result = require_supervisor_or_admin()
    if redirect_result:
        return redirect_result

    # Parámetros de filtro
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', type=int)

    # Determinar qué gastos puede ver el usuario
    if current_user.role == 'admin':
        query = Expense.query
    else:
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))

    # Filtrar por año
    query = query.filter(extract('year', Expense.expense_date) == year)

    # Filtrar por mes si se especifica
    if month:
        query = query.filter(extract('month', Expense.expense_date) == month)

    expenses = query.order_by(Expense.expense_date.desc()).all()

    # Calcular totales por mes si no hay mes específico
    monthly_totals = []
    if not month:
        for m in range(1, 13):
            month_query = query.filter(extract('month', Expense.expense_date) == m)
            count = month_query.count()
            total = db.session.query(func.sum(Expense.amount)).filter(
                Expense.id.in_([e.id for e in month_query.all()])
            ).scalar() or 0
            monthly_totals.append({
                'month': m,
                'month_name': calendar.month_name[m],
                'count': count,
                'total': total
            })

    # Totales generales
    total_amount = sum(e.amount for e in expenses)
    total_count = len(expenses)

    # Años disponibles
    available_years = db.session.query(
        extract('year', Expense.expense_date).label('year')
    ).distinct().order_by('year').all()
    available_years = [y[0] for y in available_years if y[0]]

    return render_template('reports/by_period.html',
                         expenses=expenses,
                         year=year,
                         month=month,
                         monthly_totals=monthly_totals,
                         total_amount=total_amount,
                         total_count=total_count,
                         available_years=available_years)


@reports_bp.route('/by-category')
@login_required
def by_category():
    """
    Reporte de gastos por categoría
    """
    redirect_result = require_supervisor_or_admin()
    if redirect_result:
        return redirect_result

    # Determinar qué gastos puede ver el usuario
    if current_user.role == 'admin':
        query = Expense.query
    else:
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))

    # Agrupar por categoría
    category_stats = db.session.query(
        Expense.category,
        func.count(Expense.id).label('count'),
        func.sum(Expense.amount).label('total'),
        func.avg(Expense.amount).label('average'),
        func.min(Expense.amount).label('min_amount'),
        func.max(Expense.amount).label('max_amount')
    ).filter(
        Expense.id.in_([e.id for e in query.all()])
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    return render_template('reports/by_category.html',
                         category_stats=category_stats)


@reports_bp.route('/by-area')
@login_required
def by_area():
    """
    Reporte de gastos por área (solo admin)
    """
    if current_user.role != 'admin':
        flash('Solo administradores pueden ver este reporte.', 'error')
        return redirect(url_for('reports.dashboard'))

    # Obtener todas las áreas
    areas = Area.query.filter_by(is_active=True).all()

    area_stats = []
    for area in areas:
        # Usuarios en esta área
        users_in_area = User.query.filter_by(area_id=area.id).all()
        user_ids = [u.id for u in users_in_area]

        # Gastos del área
        expenses = Expense.query.filter(Expense.user_id.in_(user_ids)).all()
        total_amount = sum(e.amount for e in expenses)
        count = len(expenses)

        # Gastos por estado
        pending = len([e for e in expenses if e.status == 'pending'])
        approved = len([e for e in expenses if e.status == 'approved'])

        area_stats.append({
            'area': area,
            'user_count': len(users_in_area),
            'expense_count': count,
            'total_amount': total_amount,
            'pending': pending,
            'approved': approved,
            'budget_usage': (total_amount / area.budget_monthly * 100) if area.budget_monthly else 0
        })

    return render_template('reports/by_area.html', area_stats=area_stats)


@reports_bp.route('/api/chart-data')
@login_required
def chart_data():
    """
    API endpoint para datos de gráficos
    """
    chart_type = request.args.get('type', 'monthly')

    if current_user.role == 'admin':
        query = Expense.query
    else:
        subordinates = User.query.filter_by(supervisor_id=current_user.id).all()
        subordinate_ids = [sub.id for sub in subordinates]
        query = Expense.query.filter(Expense.user_id.in_(subordinate_ids))

    if chart_type == 'monthly':
        # Últimos 12 meses
        data = []
        for i in range(11, -1, -1):
            date = datetime.now() - timedelta(days=30*i)
            month_expenses = query.filter(
                extract('month', Expense.expense_date) == date.month,
                extract('year', Expense.expense_date) == date.year
            ).all()
            total = sum(e.amount for e in month_expenses)
            data.append({
                'label': date.strftime('%b %Y'),
                'value': float(total)
            })
        return jsonify(data)

    elif chart_type == 'category':
        # Por categoría
        category_data = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.id.in_([e.id for e in query.all()])
        ).group_by(Expense.category).all()

        data = [{'label': cat, 'value': float(total)} for cat, total in category_data]
        return jsonify(data)

    elif chart_type == 'status':
        # Por estado
        status_data = db.session.query(
            Expense.status,
            func.count(Expense.id).label('count')
        ).filter(
            Expense.id.in_([e.id for e in query.all()])
        ).group_by(Expense.status).all()

        data = [{'label': status, 'value': count} for status, count in status_data]
        return jsonify(data)

    return jsonify([])
