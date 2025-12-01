from extensions import db
from datetime import datetime

class Area(db.Model):
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    budget_monthly = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='area', lazy='dynamic')
    
    # Índices para rendimiento
    __table_args__ = (
        db.Index('idx_area_name', 'name'),
        db.Index('idx_area_is_active', 'is_active'),
    )

class Company(db.Model): # Mapped to 'clients' table in schema
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120))
    status = db.Column(db.String(20), default='pending') # pending, active, rejected
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=False)  # False hasta aprobación
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_with_expense = db.Column(db.Boolean, default=False)  # Creado desde formulario de gasto

    expenses = db.relationship('Expense', backref='client', lazy='dynamic')
    
    # Índices para rendimiento
    __table_args__ = (
        db.Index('idx_client_rut', 'rut'),
        db.Index('idx_client_status', 'status'),
        db.Index('idx_client_created_by', 'created_by'),
        db.Index('idx_client_is_active', 'is_active'),
    )

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    requires_client = db.Column(db.Boolean, default=False)
    max_amount = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    
    # Índices para rendimiento
    __table_args__ = (
        db.Index('idx_category_name', 'name'),
        db.Index('idx_category_is_active', 'is_active'),
    )
