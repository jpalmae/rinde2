from app import create_app
from extensions import db
from models.user import User
from models.company import Area, Company, ExpenseCategory

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data exists
        if User.query.first():
            print("Database already initialized.")
            return

        print("Creating initial data...")
        
        # Create Areas
        area_it = Area(name="IT", budget_monthly=1000000)
        area_sales = Area(name="Ventas", budget_monthly=5000000)
        db.session.add_all([area_it, area_sales])
        db.session.commit()
        
        # Create Test User
        admin = User(
            email="admin@sixmanager.com",
            first_name="Admin",
            last_name="User",
            role="admin",
            area_id=area_it.id
        )
        admin.set_password("admin123")
        
        user = User(
            email="user@sixmanager.com",
            first_name="Test",
            last_name="User",
            role="user",
            area_id=area_sales.id
        )
        user.set_password("user123")
        
        db.session.add_all([admin, user])
        
        # Create Categories
        cats = [
            ExpenseCategory(name="Transporte", max_amount=50000),
            ExpenseCategory(name="Alimentación", max_amount=20000),
            ExpenseCategory(name="Hospedaje", max_amount=100000),
            ExpenseCategory(name="Materiales", max_amount=200000),
            ExpenseCategory(name="Otros", max_amount=10000)
        ]
        db.session.add_all(cats)
        
        # Create Clients
        client = Company(
            rut="76.123.456-7",
            name="Cliente Ejemplo SpA",
            contact_email="contacto@ejemplo.cl"
        )
        db.session.add(client)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
