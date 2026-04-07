from flask import Blueprint, request, jsonify
import jwt
from utils.database import execute_query
from config import Config

vendedor_bp = Blueprint('vendedor', __name__, url_prefix='/api/vendedor')

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated

@vendedor_bp.route('/produtos', methods=['GET'])
@token_required
def get_meus_produtos():
    # Buscar vendedor
    vendedor = execute_query("""
        SELECT id_vendedor FROM vendedor WHERE id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    if not vendedor and request.user_role not in ['admin', 'root']:
        return jsonify([])
    
    vendedor_id = vendedor['id_vendedor'] if vendedor else None
    
    if vendedor_id:
        produtos = execute_query("""
            SELECT p.*, e.quantidade
            FROM produto p
            JOIN estoque e ON p.id_produto = e.id_produto
            WHERE p.id_vendedor = %s
        """, (vendedor_id,), fetch_all=True)
    else:
        # Admin vê todos os produtos
        produtos = execute_query("""
            SELECT p.*, e.quantidade
            FROM produto p
            JOIN estoque e ON p.id_produto = e.id_produto
        """, fetch_all=True)
    
    return jsonify(produtos)