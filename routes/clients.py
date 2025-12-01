from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.company import Company
from utils.validators import validate_rut, validate_email, format_rut

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        rut = request.form.get('rut')
        name = request.form.get('name')
        contact_email = request.form.get('contact_email')

        # Validar RUT
        is_valid_rut, rut_error = validate_rut(rut)
        if not is_valid_rut:
            flash(f'RUT inválido: {rut_error}', 'error')
            return render_template('clients/new.html', rut=rut, name=name, contact_email=contact_email)

        # Formatear RUT
        formatted_rut = format_rut(rut)

        # Validar email si se proporciona
        if contact_email:
            is_valid_email, email_error = validate_email(contact_email)
            if not is_valid_email:
                flash(f'Email inválido: {email_error}', 'error')
                return render_template('clients/new.html', rut=rut, name=name, contact_email=contact_email)

        # Check if exists
        if Company.query.filter_by(rut=formatted_rut).first():
            flash('Este cliente ya existe.', 'error')
        else:
            client = Company(
                rut=formatted_rut,
                name=name,
                contact_email=contact_email,
                status='pending',
                is_active=False,
                created_by=current_user.id
            )
            db.session.add(client)
            db.session.commit()
            flash('Solicitud de cliente enviada. Debe ser aprobada por un administrador.', 'success')
            return redirect(url_for('index'))

    return render_template('clients/new.html')
