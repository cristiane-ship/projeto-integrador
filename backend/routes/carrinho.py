from flask import Blueprint, request, jsonify
import jwt
from utils.database import execute_query
from config import Config

carrinho_bp = Blueprint('carrinho', __name__, url_prefix='/api/carrinho')

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

@carrinho_bp.route('/', methods=['GET'])
@token_required
def get_carrinho():
    # Buscar carrinho do usuário
    carrinho = execute_query("""
        SELECT id_carrinho FROM carrinho WHERE id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    if not carrinho:
        return jsonify({'items': [], 'total': 0})
    
    # Buscar itens do carrinho
    itens = execute_query("""
        SELECT ic.id_item_carrinho, ic.id_produto, ic.quantidade,
               p.nome, p.preco, p.imagem_url,
               (ic.quantidade * p.preco) as subtotal
        FROM item_carrinho ic
        JOIN produto p ON ic.id_produto = p.id_produto
        WHERE ic.id_carrinho = %s
    """, (carrinho['id_carrinho'],), fetch_all=True)
    
    total = sum(item['subtotal'] for item in itens) if itens else 0
    
    return jsonify({
        'items': itens if itens else [],
        'total': float(total)
    })

@carrinho_bp.route('/items', methods=['POST'])
@token_required
def adicionar_item():
    data = request.json
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)
    
    # Verificar estoque
    estoque = execute_query("""
        SELECT quantidade, reservado FROM estoque WHERE id_produto = %s
    """, (produto_id,), fetch_one=True)
    
    if not estoque:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    disponivel = estoque['quantidade'] - estoque['reservado']
    
    if disponivel < quantidade:
        return jsonify({'error': 'Estoque insuficiente'}), 400
    
    # Buscar carrinho do usuário
    carrinho = execute_query("""
        SELECT id_carrinho FROM carrinho WHERE id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    if not carrinho:
        carrinho_id = execute_query("""
            INSERT INTO carrinho (id_usuario) VALUES (%s)
        """, (request.user_id,), commit=True)
    else:
        carrinho_id = carrinho['id_carrinho']
    
    # Verificar se produto já está no carrinho
    item_existente = execute_query("""
        SELECT id_item_carrinho, quantidade FROM item_carrinho
        WHERE id_carrinho = %s AND id_produto = %s
    """, (carrinho_id, produto_id), fetch_one=True)
    
    if item_existente:
        nova_quantidade = item_existente['quantidade'] + quantidade
        execute_query("""
            UPDATE item_carrinho SET quantidade = %s
            WHERE id_item_carrinho = %s
        """, (nova_quantidade, item_existente['id_item_carrinho']), commit=True)
    else:
        execute_query("""
            INSERT INTO item_carrinho (id_carrinho, id_produto, quantidade)
            VALUES (%s, %s, %s)
        """, (carrinho_id, produto_id, quantidade), commit=True)
    
    # Reservar estoque
    execute_query("""
        UPDATE estoque SET reservado = reservado + %s
        WHERE id_produto = %s
    """, (quantidade, produto_id), commit=True)
    
    return jsonify({'message': 'Produto adicionado ao carrinho'})

@carrinho_bp.route('/items/<int:item_id>', methods=['DELETE'])
@token_required
def remover_item(item_id):
    # Buscar item
    item = execute_query("""
        SELECT ic.*, c.id_usuario 
        FROM item_carrinho ic
        JOIN carrinho c ON ic.id_carrinho = c.id_carrinho
        WHERE ic.id_item_carrinho = %s
    """, (item_id,), fetch_one=True)
    
    if not item:
        return jsonify({'error': 'Item não encontrado'}), 404
    
    if item['id_usuario'] != request.user_id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Liberar estoque reservado
    execute_query("""
        UPDATE estoque SET reservado = reservado - %s
        WHERE id_produto = %s
    """, (item['quantidade'], item['id_produto']), commit=True)
    
    # Remover item
    execute_query("DELETE FROM item_carrinho WHERE id_item_carrinho = %s", (item_id,), commit=True)
    
    return jsonify({'message': 'Item removido'})