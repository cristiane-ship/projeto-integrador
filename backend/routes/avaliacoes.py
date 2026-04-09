from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/api/avaliacoes')

@avaliacoes_bp.route('/', methods=['POST'])
@token_required
def criar_avaliacao():
    """RN03: Usuário só pode avaliar se comprou o produto"""
    data = request.json
    
    produto_id = data.get('produto_id')
    nota = data.get('nota')
    comentario = data.get('comentario', '')
    
    if not produto_id or not nota:
        return jsonify({'error': 'Produto e nota são obrigatórios'}), 400
    
    if nota < 1 or nota > 5:
        return jsonify({'error': 'Nota deve ser entre 1 e 5'}), 400
    
    # Verificar se o usuário já comprou este produto
    pedido_comprou = execute_query("""
        SELECT ip.id_item_pedido 
        FROM item_pedido ip
        JOIN pedido p ON ip.id_pedido = p.id_pedido
        WHERE p.id_usuario = %s AND ip.id_produto = %s AND p.status = 'pago'
        LIMIT 1
    """, (request.user_id, produto_id), fetch_one=True)
    
    if not pedido_comprou:
        return jsonify({'error': 'Você só pode avaliar produtos que comprou'}), 403
    
    # Verificar se já avaliou este produto
    ja_avaliou = execute_query("""
        SELECT id_avaliacao FROM avaliacao 
        WHERE id_produto = %s AND id_pedido IN (
            SELECT id_pedido FROM item_pedido WHERE id_produto = %s
        )
    """, (produto_id, produto_id), fetch_one=True)
    
    if ja_avaliou:
        return jsonify({'error': 'Você já avaliou este produto'}), 409
    
    # Buscar um pedido_id válido para o produto
    pedido = execute_query("""
        SELECT p.id_pedido 
        FROM pedido p
        JOIN item_pedido ip ON p.id_pedido = ip.id_pedido
        WHERE p.id_usuario = %s AND ip.id_produto = %s AND p.status = 'pago'
        LIMIT 1
    """, (request.user_id, produto_id), fetch_one=True)
    
    # Criar avaliação
    avaliacao_id = execute_query("""
        INSERT INTO avaliacao (id_pedido, id_produto, nota, comentario)
        VALUES (%s, %s, %s, %s)
    """, (pedido['id_pedido'], produto_id, nota, comentario), commit=True)
    
    return jsonify({
        'message': 'Avaliação criada com sucesso',
        'id_avaliacao': avaliacao_id
    }), 201

@avaliacoes_bp.route('/produto/<int:produto_id>', methods=['GET'])
def listar_avaliacoes_produto(produto_id):
    """Listar todas as avaliações de um produto"""
    avaliacoes = execute_query("""
        SELECT a.*, u.nome as usuario_nome, u.id_usuario
        FROM avaliacao a
        JOIN pedido p ON a.id_pedido = p.id_pedido
        JOIN usuario u ON p.id_usuario = u.id_usuario
        WHERE a.id_produto = %s
        ORDER BY a.data_avaliacao DESC
    """, (produto_id,), fetch_all=True)
    
    # Calcular média
    media = 0
    if avaliacoes:
        soma = sum(a['nota'] for a in avaliacoes)
        media = round(soma / len(avaliacoes), 1)
    
    return jsonify({
        'media': media,
        'total': len(avaliacoes),
        'avaliacoes': avaliacoes
    })

@avaliacoes_bp.route('/meu/<int:produto_id>', methods=['GET'])
@token_required
def minha_avaliacao(produto_id):
    """Verificar se o usuário já avaliou este produto"""
    avaliacao = execute_query("""
        SELECT a.* 
        FROM avaliacao a
        JOIN pedido p ON a.id_pedido = p.id_pedido
        WHERE p.id_usuario = %s AND a.id_produto = %s
    """, (request.user_id, produto_id), fetch_one=True)
    
    if avaliacao:
        return jsonify({'avaliou': True, 'avaliacao': avaliacao})
    return jsonify({'avaliou': False})