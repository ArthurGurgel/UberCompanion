from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app)
    
    # Registrar blueprints
    from app.routes import ganhos_bp, abastecimentos_bp, dashboard_bp
    
    app.register_blueprint(ganhos_bp)
    app.register_blueprint(abastecimentos_bp)
    app.register_blueprint(dashboard_bp)
    
    return app
