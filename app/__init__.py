from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pmo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey'  # Pastikan untuk mengganti ini dengan kunci yang lebih aman

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import views
        db.create_all()

    return app
