from extensions import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  # Ahora obligatorio
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    receipt_image = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected, reimbursed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ocr_data = db.Column(db.JSON)

    approvals = db.relationship('Approval', backref='expense', lazy='dynamic')
