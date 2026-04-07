from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta
from utils.database import execute_query
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    data = request.json
    
    if not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    # Verificar se email já existe
    existing = execute_query(
        "SELECT id_usuario FROM usuario WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )
    
    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409
    
    # Hash da senha
    senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Inserir usuário
    user_id = execute_query("""
        INSERT INTO usuario (nome, email, senha_hash, role, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['nome'], data['email'], senha_hash, 'usuario', 'ativo'), commit=True)
    
    # Criar carrinho para o usuário
    execute_query("INSERT INTO carrinho (id_usuario) VALUES (%s)", (user_id,), commit=True)
    
    return jsonify({'message': 'Usuário criado com sucesso', 'user_id': user_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    # Buscar usuário
    user = execute_query("""
        SELECT id_usuario, nome, email, senha_hash, role, status
        FROM usuario
        WHERE email = %s
    """, (data['email'],), fetch_one=True)
    
    if not user:
        return jsonify({'error': 'Email ou senha inválidos'}), 401
    
    if user['status'] != 'ativo':
        return jsonify({'error': 'Usuário não está ativo'}), 401
    
    # Verificar senha
    if not bcrypt.checkpw(data['senha'].encode('utf-8'), user['senha_hash'].encode('utf-8')):
        return jsonify({'error': 'Email ou senha inválidos'}), 401
    
    # Gerar JWT
    token = jwt.encode({
        'user_id': user['id_usuario'],
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION
    }, Config.JWT_SECRET, algorithm='HS256')
    
    # Remover senha_hash do retorno
    del user['senha_hash']
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'usuario': user
    })

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token não fornecido'}), 401
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        
        user = execute_query("""
            SELECT id_usuario, nome, email, role, status, data_cadastro
            FROM usuario WHERE id_usuario = %s
        """, (payload['user_id'],), fetch_one=True)
        
        return jsonify(user)
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401