from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.expense import Expense
from models.company import Company
from services.ocr_service import process_receipt
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
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Ensure unique filename to prevent overwrites
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"

            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

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
                expense = Expense(
                    user_id=current_user.id,
                    amount=float(request.form.get('amount')),
                    category=request.form.get('category'),
                    reason=request.form.get('reason'),
                    client_id=request.form.get('client_id') if request.form.get('client_id') else None,
                    latitude=request.form.get('latitude') if request.form.get('latitude') else None,
                    longitude=request.form.get('longitude') if request.form.get('longitude') else None,
                    receipt_image=filename,
                    expense_date=datetime.now(),
                    ocr_data=ocr_data
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
