from flask import Blueprint, request, jsonify
import jwt
from utils.database import execute_query
from config import Config

produtos_bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')

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
            request.user_email = payload['email']
            request.user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated

def role_required(roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user_role not in roles:
                return jsonify({'error': 'Acesso negado. Permissão insuficiente.'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

@produtos_bp.route('/', methods=['GET'])
def listar_produtos():
    categoria = request.args.get('categoria')
    busca = request.args.get('busca')
    
    query = """
        SELECT p.*, 
               (e.quantidade - e.reservado) as disponivel,
               u.nome as vendedor_nome
        FROM produto p
        JOIN estoque e ON p.id_produto = e.id_produto
        JOIN vendedor v ON p.id_vendedor = v.id_vendedor
        JOIN usuario u ON v.id_usuario = u.id_usuario
        WHERE p.status = 'ativo' AND (e.quantidade - e.reservado) > 0
    """
    params = []
    
    if categoria:
        query += " AND p.categoria = %s"
        params.append(categoria)
    
    if busca:
        query += " AND (p.nome LIKE %s OR p.descricao LIKE %s)"
        params.extend([f'%{busca}%', f'%{busca}%'])
    
    produtos = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(produtos)

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    produto = execute_query("""
        SELECT p.*, 
               (e.quantidade - e.reservado) as disponivel,
               u.nome as vendedor_nome,
               u.id_usuario as vendedor_id
        FROM produto p
        JOIN estoque e ON p.id_produto = e.id_produto
        JOIN vendedor v ON p.id_vendedor = v.id_vendedor
        JOIN usuario u ON v.id_usuario = u.id_usuario
        WHERE p.id_produto = %s
    """, (produto_id,), fetch_one=True)
    
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    return jsonify(produto)

@produtos_bp.route('/', methods=['POST'])
@token_required
def criar_produto():
    data = request.json
    
    # Verificar se é vendedor
    vendedor = execute_query("""
        SELECT id_vendedor FROM vendedor WHERE id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    # Se não for vendedor e não for admin, negar
    if not vendedor and request.user_role not in ['admin', 'root']:
        return jsonify({'error': 'Usuário não é vendedor'}), 403
    
    vendedor_id = vendedor['id_vendedor'] if vendedor else None
    
    produto_id = execute_query("""
        INSERT INTO produto (id_vendedor, nome, descricao, preco, categoria, imagem_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (vendedor_id, data['nome'], data.get('descricao'), data['preco'], 
          data.get('categoria'), data.get('imagem_url')), commit=True)
    
    execute_query("""
        INSERT INTO estoque (id_produto, quantidade)
        VALUES (%s, %s)
    """, (produto_id, data.get('quantidade', 0)), commit=True)
    
    return jsonify({'message': 'Produto criado', 'id_produto': produto_id}), 201

@produtos_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = execute_query("""
        SELECT DISTINCT categoria FROM produto WHERE status = 'ativo' AND categoria IS NOT NULL
    """, fetch_all=True)
    
    return jsonify([c['categoria'] for c in categorias])

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@token_required
def atualizar_produto(produto_id):
    data = request.json
    
    # Verificar se produto existe e pertence ao vendedor
    produto = execute_query("""
        SELECT p.*, v.id_usuario as vendedor_usuario_id
        FROM produto p
        JOIN vendedor v ON p.id_vendedor = v.id_vendedor
        WHERE p.id_produto = %s
    """, (produto_id,), fetch_one=True)
    
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    # Verificar permissão (dono do produto ou admin)
    if produto['vendedor_usuario_id'] != request.user_id and request.user_role not in ['admin', 'root']:
        return jsonify({'error': 'Você não tem permissão para editar este produto'}), 403
    
    # Atualizar produto
    execute_query("""
        UPDATE produto 
        SET nome=%s, descricao=%s, preco=%s, categoria=%s, imagem_url=%s, status=%s
        WHERE id_produto = %s
    """, (
        data.get('nome'), 
        data.get('descricao'), 
        data.get('preco'), 
        data.get('categoria'),
        data.get('imagem_url'), 
        data.get('status', 'ativo'), 
        produto_id
    ), commit=True)
    
    # Atualizar estoque se veio quantidade
    if data.get('quantidade') is not None:
        execute_query("""
            UPDATE estoque SET quantidade = %s WHERE id_produto = %s
        """, (data['quantidade'], produto_id), commit=True)
    
    return jsonify({'message': 'Produto atualizado com sucesso'})

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@token_required
def deletar_produto(produto_id):
    # Verificar se produto existe e pertence ao vendedor
    produto = execute_query("""
        SELECT p.*, v.id_usuario as vendedor_usuario_id
        FROM produto p
        JOIN vendedor v ON p.id_vendedor = v.id_vendedor
        WHERE p.id_produto = %s
    """, (produto_id,), fetch_one=True)
    
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    # Verificar permissão
    if produto['vendedor_usuario_id'] != request.user_id and request.user_role not in ['admin', 'root']:
        return jsonify({'error': 'Você não tem permissão para deletar este produto'}), 403
    
    # Deletar produto (cascade vai deletar estoque também)
    execute_query("DELETE FROM produto WHERE id_produto = %s", (produto_id,), commit=True)
    
    return jsonify({'message': 'Produto deletado com sucesso'})