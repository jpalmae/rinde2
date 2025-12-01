from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.expenses import expenses_bp
    from routes.admin import admin_bp
    from routes.clients import clients_bp
    from routes.approvals import approvals_bp
    from routes.reports import reports_bp
    # from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(reports_bp)
    # app.register_blueprint(api_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Import models to ensure they are known to SQLAlchemy
        from models import User, Expense, Approval, Company, Area, ExpenseCategory
        # db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
