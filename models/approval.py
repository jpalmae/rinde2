from extensions import db
from datetime import datetime

class Approval(db.Model):
    __tablename__ = 'approvals'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False) # approved, rejected
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices para rendimiento
    __table_args__ = (
        db.Index('idx_approval_expense_id', 'expense_id'),
        db.Index('idx_approval_approver_id', 'approver_id'),
        db.Index('idx_approval_action', 'action'),
        db.Index('idx_approval_created_at', 'created_at'),
    )
