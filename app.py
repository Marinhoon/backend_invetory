import sys
import os
from flask import Flask
from flask_cors import CORS
from config import Config
from pymongo import MongoClient
from routes.auth import auth_bp
from routes.produtos import produtos_bp
from routes.nfes import nfes_bp

# Adicionar o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Conexão com MongoDB
    try:
        client = MongoClient(app.config['MONGODB_URI'])
        db = client[app.config['MONGODB_DB_NAME']]
        app.db = db
        print(f"[v0] Conectado ao MongoDB com sucesso - DB: {app.config['MONGODB_DB_NAME']}")
    except Exception as e:
        print(f"[v0] Erro ao conectar ao MongoDB: {e}")

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(produtos_bp, url_prefix='/api/produtos')
    app.register_blueprint(nfes_bp, url_prefix='/api/nfes')

    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'message': 'API está funcionando'}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
