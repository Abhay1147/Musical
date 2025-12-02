from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "musical.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.secret_key = 'dev-secret-change-me'

    db.init_app(app)

    # Create DB and uploads directory early so schema is ready before routes import/use it
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # register blueprints (view and edit interfaces)
    from routes import view_bp, edit_bp
    app.register_blueprint(view_bp)
    app.register_blueprint(edit_bp, url_prefix='/edit')
    
    # seed initial production if none exists
    from seed_mermaid import seed_mermaid
    with app.app_context():
        seed_mermaid(app, db)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)