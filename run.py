from app import create_app
from app.database import db

if __name__ == '__main__':
    app = create_app()
    
    # Criar tabelas ao iniciar
    db.criar_tabelas()
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
