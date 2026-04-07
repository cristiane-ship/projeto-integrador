from flask import Blueprint, request, jsonify
import jwt
from utils.database import execute_query
from config import Config
from datetime import datetime

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/api/pedidos')

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

@pedidos_bp.route('/', methods=['POST'])
@token_required
def criar_pedido():
    data = request.json
    endereco_id = data.get('endereco_id')
    
    # Buscar carrinho
    carrinho = execute_query("""
        SELECT c.id_carrinho, SUM(ic.quantidade * p.preco) as subtotal
        FROM carrinho c
        JOIN item_carrinho ic ON c.id_carrinho = ic.id_carrinho
        JOIN produto p ON ic.id_produto = p.id_produto
        WHERE c.id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    if not carrinho or not carrinho['subtotal']:
        return jsonify({'error': 'Carrinho vazio'}), 400
    
    valor_total = carrinho['subtotal']
    
    # Criar pedido
    pedido_id = execute_query("""
        INSERT INTO pedido (id_usuario, id_endereco_entrega, valor_frete, valor_total, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (request.user_id, endereco_id, 0, valor_total, 'pago'), commit=True)
    
    # Mover itens do carrinho para o pedido
    itens = execute_query("""
        SELECT ic.id_produto, ic.quantidade, p.preco
        FROM item_carrinho ic
        JOIN produto p ON ic.id_produto = p.id_produto
        WHERE ic.id_carrinho = %s
    """, (carrinho['id_carrinho'],), fetch_all=True)
    
    for item in itens:
        execute_query("""
            INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, item['id_produto'], item['quantidade'], item['preco']), commit=True)
        
        # Dar baixa no estoque
        execute_query("""
            UPDATE estoque 
            SET quantidade = quantidade - %s, reservado = reservado - %s
            WHERE id_produto = %s
        """, (item['quantidade'], item['quantidade'], item['id_produto']), commit=True)
    
    # Limpar carrinho
    execute_query("DELETE FROM item_carrinho WHERE id_carrinho = %s", (carrinho['id_carrinho'],), commit=True)
    
    return jsonify({
        'message': 'Pedido criado com sucesso',
        'pedido_id': pedido_id,
        'valor_total': float(valor_total)
    }), 201

@pedidos_bp.route('/', methods=['GET'])
@token_required
def listar_pedidos():
    pedidos = execute_query("""
        SELECT p.*, e.logradouro, e.numero, e.cidade, e.estado
        FROM pedido p
        LEFT JOIN endereco e ON p.id_endereco_entrega = e.id_endereco
        WHERE p.id_usuario = %s
        ORDER BY p.data_pedido DESC
    """, (request.user_id,), fetch_all=True)
    
    return jsonify(pedidos)

@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@token_required
def get_pedido(pedido_id):
    pedido = execute_query("""
        SELECT p.*, e.logradouro, e.numero, e.bairro, e.cidade, e.estado, e.cep,
               t.nome as transportadora_nome
        FROM pedido p
        LEFT JOIN endereco e ON p.id_endereco_entrega = e.id_endereco
        LEFT JOIN transportadora t ON p.id_transportadora = t.id_transp
        WHERE p.id_pedido = %s AND p.id_usuario = %s
    """, (pedido_id, request.user_id), fetch_one=True)
    
    if not pedido:
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    itens = execute_query("""
        SELECT ip.*, p.nome, p.imagem_url
        FROM item_pedido ip
        JOIN produto p ON ip.id_produto = p.id_produto
        WHERE ip.id_pedido = %s
    """, (pedido_id,), fetch_all=True)
    
    pedido['itens'] = itens
    
    return jsonify(pedido)