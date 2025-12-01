from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.expense import Expense
from models.company import Company
from services.ocr_service import process_receipt
from utils.file_validators import validate_file_upload, generate_unique_filename, scan_file_for_malware, FileValidationError
from datetime import datetime
import os
import json

expenses_bp = Blueprint('expenses', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@expenses_bp.route('/expenses/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        # Verificar si se está creando un cliente nuevo
        create_new_client = request.form.get('create_new_client') == 'true'
        client_id = request.form.get('client_id')

        if create_new_client:
            # Crear cliente nuevo
            from utils.validators import validate_rut, validate_email, format_rut

            client_rut = request.form.get('new_client_rut')
            client_name = request.form.get('new_client_name')
            client_email = request.form.get('new_client_email')

            # Validar RUT
            is_valid_rut, rut_error = validate_rut(client_rut)
            if not is_valid_rut:
                flash(f'RUT del cliente inválido: {rut_error}', 'error')
                return redirect(request.url)

            formatted_rut = format_rut(client_rut)

            # Validar email si se proporciona
            if client_email:
                is_valid_email, email_error = validate_email(client_email)
                if not is_valid_email:
                    flash(f'Email del cliente inválido: {email_error}', 'error')
                    return redirect(request.url)

            # Verificar si el cliente ya existe
            existing_client = Company.query.filter_by(rut=formatted_rut).first()
            if existing_client:
                if existing_client.status == 'rejected':
                    flash('Este cliente fue rechazado previamente. Contacte a un administrador.', 'error')
                    return redirect(request.url)
                client_id = existing_client.id
                flash(f'Cliente "{existing_client.name}" ya existe, se usará para este gasto.', 'info')
            else:
                # Crear nuevo cliente en estado pendiente
                new_client = Company(
                    rut=formatted_rut,
                    name=client_name,
                    contact_email=client_email,
                    status='pending',
                    is_active=False,
                    created_by=current_user.id,
                    created_with_expense=True
                )
                db.session.add(new_client)
                db.session.flush()  # Para obtener el ID
                client_id = new_client.id
                flash(f'Cliente nuevo "{client_name}" creado. Debe ser aprobado antes del gasto.', 'info')

        if not client_id:
            flash('Debe seleccionar un cliente o crear uno nuevo.', 'error')
            return redirect(request.url)

        # Basic validation
        if 'receipt' not in request.files:
            flash('No receipt image part', 'error')
            return redirect(request.url)
            
        # Validate geolocation
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        if not latitude or not longitude:
            flash('Geolocation is mandatory. Please enable location services.', 'error')
            return redirect(request.url)
        
        file = request.files['receipt']
        
        try:
            # Validación completa del archivo
            file_info = validate_file_upload(file)
            filename = generate_unique_filename(file.filename, current_user.id)
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Escaneo de malware
            is_clean, threat_info = scan_file_for_malware(filepath)
            if not is_clean:
                os.remove(filepath)  # Eliminar archivo sospechoso
                flash(f'Archivo rechazado por seguridad: {threat_info}', 'error')
                return redirect(request.url)
                
        except FileValidationError as e:
            flash(str(e), 'error')
            return redirect(request.url)

            # Procesar imagen con OCR
            ocr_data = None
            try:
                ocr_result = process_receipt(filepath)
                if ocr_result['success']:
                    ocr_data = ocr_result
                    # Si no se ingresó monto y OCR encontró uno, sugerir
                    if not request.form.get('amount') and ocr_result.get('suggested_amount'):
                        flash(f'OCR detectó monto sugerido: ${ocr_result["suggested_amount"]:,.0f}', 'info')
            except Exception as e:
                print(f"Error procesando OCR: {str(e)}")
                # Continuar sin OCR si falla

            # Create expense
            try:
                # Verificar estado del cliente
                client = Company.query.get(client_id)
                expense_status = 'pending'

                # Si el cliente está pendiente, el gasto también queda en estado especial
                if client and client.status == 'pending':
                    expense_status = 'pending'  # Quedará pendiente hasta que se apruebe el cliente
                    flash('El gasto quedará pendiente hasta que el cliente sea aprobado.', 'warning')

                expense = Expense(
                    user_id=current_user.id,
                    amount=float(request.form.get('amount')),
                    category=request.form.get('category'),
                    reason=request.form.get('reason'),
                    client_id=client_id,  # Ahora obligatorio
                    latitude=request.form.get('latitude') if request.form.get('latitude') else None,
                    longitude=request.form.get('longitude') if request.form.get('longitude') else None,
                    receipt_image=filename,
                    expense_date=datetime.now(),
                    ocr_data=ocr_data,
                    status=expense_status
                )

                db.session.add(expense)
                db.session.commit()

                flash('Expense submitted successfully!', 'success')
                if ocr_data and ocr_data.get('confidence') == 'high':
                    flash('Datos extraídos automáticamente con alta confianza.', 'success')

                return redirect(url_for('index'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating expense: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type', 'error')
            return redirect(request.url)

    clients = Company.query.filter_by(is_active=True).all()
    return render_template('expenses/new.html', clients=clients)

@expenses_bp.route('/expenses/my')
@login_required
def my_expenses():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('EXPENSES_PER_PAGE', 20)

    pagination = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    expenses = pagination.items

    return render_template('expenses/list.html',
                         expenses=expenses,
                         pagination=pagination)
