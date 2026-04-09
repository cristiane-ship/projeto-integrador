from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query
from datetime import datetime

mensagens_bp = Blueprint('mensagens', __name__, url_prefix='/api/mensagens')

@mensagens_bp.route('/', methods=['POST'])
@token_required
def enviar_mensagem():
    data = request.json
    
    destinatario_id = data.get('destinatario_id')
    assunto = data.get('assunto', '')
    conteudo = data.get('conteudo')
    
    if not destinatario_id or not conteudo:
        return jsonify({'error': 'Destinatário e conteúdo são obrigatórios'}), 400
    
    # Não pode enviar mensagem para si mesmo
    if destinatario_id == request.user_id:
        return jsonify({'error': 'Não pode enviar mensagem para si mesmo'}), 400
    
    # Verificar se destinatário existe
    destinatario = execute_query(
        "SELECT id_usuario FROM usuario WHERE id_usuario = %s",
        (destinatario_id,), fetch_one=True
    )
    
    if not destinatario:
        return jsonify({'error': 'Destinatário não encontrado'}), 404
    
    # Enviar mensagem
    mensagem_id = execute_query("""
        INSERT INTO mensagem (id_remetente, id_destinatario, assunto, conteudo)
        VALUES (%s, %s, %s, %s)
    """, (request.user_id, destinatario_id, assunto, conteudo), commit=True)
    
    return jsonify({
        'message': 'Mensagem enviada com sucesso',
        'id_mensagem': mensagem_id
    }), 201

@mensagens_bp.route('/conversas', methods=['GET'])
@token_required
def listar_conversas():
    """Lista todos os usuários com quem o usuário atual já conversou"""
    conversas = execute_query("""
        SELECT DISTINCT 
            CASE 
                WHEN m.id_remetente = %s THEN m.id_destinatario
                ELSE m.id_remetente
            END as outro_usuario_id,
            u.nome as outro_usuario_nome,
            u.email as outro_usuario_email,
            (SELECT conteudo FROM mensagem 
             WHERE (id_remetente = %s AND id_destinatario = outro_usuario_id)
                OR (id_remetente = outro_usuario_id AND id_destinatario = %s)
             ORDER BY data_envio DESC LIMIT 1) as ultima_mensagem,
            (SELECT data_envio FROM mensagem 
             WHERE (id_remetente = %s AND id_destinatario = outro_usuario_id)
                OR (id_remetente = outro_usuario_id AND id_destinatario = %s)
             ORDER BY data_envio DESC LIMIT 1) as ultima_data,
            (SELECT COUNT(*) FROM mensagem 
             WHERE id_destinatario = %s AND id_remetente = outro_usuario_id AND lida = FALSE) as nao_lidas
        FROM mensagem m
        JOIN usuario u ON (CASE WHEN m.id_remetente = %s THEN m.id_destinatario ELSE m.id_remetente END) = u.id_usuario
        WHERE m.id_remetente = %s OR m.id_destinatario = %s
        ORDER BY ultima_data DESC
    """, (request.user_id, request.user_id, request.user_id, 
          request.user_id, request.user_id, request.user_id,
          request.user_id, request.user_id, request.user_id), fetch_all=True)
    
    return jsonify(conversas)

@mensagens_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@token_required
def buscar_mensagens(usuario_id):
    """Buscar todas as mensagens entre o usuário atual e outro usuário"""
    
    # Marcar mensagens recebidas como lidas
    execute_query("""
        UPDATE mensagem SET lida = TRUE 
        WHERE id_remetente = %s AND id_destinatario = %s AND lida = FALSE
    """, (usuario_id, request.user_id), commit=True)
    
    # Buscar mensagens
    mensagens = execute_query("""
        SELECT m.*, 
               u_rem.nome as remetente_nome,
               u_dest.nome as destinatario_nome
        FROM mensagem m
        JOIN usuario u_rem ON m.id_remetente = u_rem.id_usuario
        JOIN usuario u_dest ON m.id_destinatario = u_dest.id_usuario
        WHERE (id_remetente = %s AND id_destinatario = %s)
           OR (id_remetente = %s AND id_destinatario = %s)
        ORDER BY data_envio ASC
    """, (request.user_id, usuario_id, usuario_id, request.user_id), fetch_all=True)
    
    # Informações do outro usuário
    outro_usuario = execute_query(
        "SELECT id_usuario, nome, email FROM usuario WHERE id_usuario = %s",
        (usuario_id,), fetch_one=True
    )
    
    return jsonify({
        'outro_usuario': outro_usuario,
        'mensagens': mensagens
    })

@mensagens_bp.route('/nao-lidas', methods=['GET'])
@token_required
def contar_nao_lidas():
    """Contar mensagens não lidas do usuário"""
    total = execute_query("""
        SELECT COUNT(*) as total FROM mensagem 
        WHERE id_destinatario = %s AND lida = FALSE
    """, (request.user_id,), fetch_one=True)
    
    return jsonify({'total_nao_lidas': total['total']}) 
