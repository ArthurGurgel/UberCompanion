from flask import Flask
# Carregar .env para obter SECRET_KEY e outras variáveis antes de criar a app
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # secret key necessária para session/flash - troque em produção
    import os
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-please-change')
    CORS(app)
    
    # Registrar blueprints
    from app.routes import ganhos_bp, abastecimentos_bp, dashboard_bp, app_home, app_cad
    
    app.register_blueprint(ganhos_bp)
    app.register_blueprint(abastecimentos_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(app_home)
    app.register_blueprint(app_cad)
    
    return app
