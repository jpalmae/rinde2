from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, supervisor, admin
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')
    approvals = db.relationship('Approval', backref='approver', lazy='dynamic')
    subordinates = db.relationship('User', backref=db.backref('supervisor', remote_side=[id]))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    # Índices para rendimiento
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_role', 'role'),
        db.Index('idx_user_area_id', 'area_id'),
        db.Index('idx_user_supervisor_id', 'supervisor_id'),
        db.Index('idx_user_is_active', 'is_active'),
    )
