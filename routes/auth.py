from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400

        users_collection = current_app.db['users']
        user = users_collection.find_one({'username': username})

        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Username ou senha inválidos'}), 401

        # Criar token JWT
        token = jwt.encode({
            'user_id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'nome': user['nome'],
                'role': user['role']
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nome = data.get('nome')

        if not username or not password or not nome:
            return jsonify({'error': 'Username, password e nome são obrigatórios'}), 400

        users_collection = current_app.db['users']

        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username já existe'}), 409

        user = {
            'username': username,
            'password': generate_password_hash(password),
            'nome': nome,
            'role': 'usuario',
            'created_at': datetime.utcnow()
        }

        result = users_collection.insert_one(user)

        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user_id': str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/init-admin', methods=['POST'])
def init_admin():
    """Inicializa usuário admin padrão se não existir"""
    try:
        users_collection = current_app.db['users']

        if users_collection.find_one({'username': 'admin'}):
            return jsonify({'message': 'Admin já existe'}), 200

        admin_user = {
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'nome': 'Administrador',
            'role': 'admin',
            'created_at': datetime.utcnow()
        }

        result = users_collection.insert_one(admin_user)
        return jsonify({'message': 'Admin criado com sucesso', 'user_id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
