from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

enderecos_bp = Blueprint('enderecos', __name__, url_prefix='/api/enderecos')

@enderecos_bp.route('/', methods=['GET'])
@token_required
def listar_enderecos():
    """Listar todos os endereços do usuário"""
    enderecos = execute_query("""
        SELECT * FROM endereco 
        WHERE id_usuario = %s 
        ORDER BY principal DESC, id_endereco ASC
    """, (request.user_id,), fetch_all=True)
    
    return jsonify(enderecos)

@enderecos_bp.route('/', methods=['POST'])
@token_required
def criar_endereco():
    data = request.json
    
    campos_obrigatorios = ['cep', 'logradouro', 'numero', 'bairro', 'cidade', 'estado']
    for campo in campos_obrigatorios:
        if not data.get(campo):
            return jsonify({'error': f'Campo {campo} é obrigatório'}), 400
    
    # Se for o primeiro endereço ou marcou como principal
    qtd_enderecos = execute_query(
        "SELECT COUNT(*) as total FROM endereco WHERE id_usuario = %s",
        (request.user_id,), fetch_one=True
    )
    
    eh_principal = data.get('principal', False)
    if qtd_enderecos['total'] == 0:
        eh_principal = True
    
    # Se este endereço será principal, remover principal dos outros
    if eh_principal:
        execute_query("""
            UPDATE endereco SET principal = FALSE 
            WHERE id_usuario = %s AND principal = TRUE
        """, (request.user_id,), commit=True)
    
    # Inserir endereço
    endereco_id = execute_query("""
        INSERT INTO endereco (id_usuario, cep, logradouro, numero, complemento, 
                              bairro, cidade, estado, principal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (request.user_id, data['cep'], data['logradouro'], data['numero'],
          data.get('complemento'), data['bairro'], data['cidade'], 
          data['estado'].upper(), eh_principal), commit=True)
    
    return jsonify({
        'message': 'Endereço criado com sucesso',
        'id_endereco': endereco_id,
        'principal': eh_principal
    }), 201

@enderecos_bp.route('/<int:endereco_id>', methods=['PUT'])
@token_required
def atualizar_endereco(endereco_id):
    data = request.json
    
    # Verificar se endereço pertence ao usuário
    endereco = execute_query("""
        SELECT * FROM endereco WHERE id_endereco = %s AND id_usuario = %s
    """, (endereco_id, request.user_id), fetch_one=True)
    
    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404
    
    # Verificar se vai marcar como principal
    eh_principal = data.get('principal', endereco['principal'])
    if eh_principal and not endereco['principal']:
        # Remover principal dos outros
        execute_query("""
            UPDATE endereco SET principal = FALSE 
            WHERE id_usuario = %s AND principal = TRUE
        """, (request.user_id,), commit=True)
    
    # Atualizar endereço
    execute_query("""
        UPDATE endereco 
        SET cep = %s, logradouro = %s, numero = %s, complemento = %s,
            bairro = %s, cidade = %s, estado = %s, principal = %s
        WHERE id_endereco = %s
    """, (data.get('cep', endereco['cep']),
          data.get('logradouro', endereco['logradouro']),
          data.get('numero', endereco['numero']),
          data.get('complemento', endereco['complemento']),
          data.get('bairro', endereco['bairro']),
          data.get('cidade', endereco['cidade']),
          data.get('estado', endereco['estado']).upper(),
          eh_principal,
          endereco_id), commit=True)
    
    return jsonify({'message': 'Endereço atualizado com sucesso'})

@enderecos_bp.route('/<int:endereco_id>', methods=['DELETE'])
@token_required
def deletar_endereco(endereco_id):
    # Verificar se endereço pertence ao usuário
    endereco = execute_query("""
        SELECT * FROM endereco WHERE id_endereco = %s AND id_usuario = %s
    """, (endereco_id, request.user_id), fetch_one=True)
    
    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404
    
    # Não pode deletar endereço principal se for o único
    qtd_enderecos = execute_query("""
        SELECT COUNT(*) as total FROM endereco WHERE id_usuario = %s
    """, (request.user_id,), fetch_one=True)
    
    if endereco['principal'] and qtd_enderecos['total'] == 1:
        return jsonify({'error': 'Não é possível deletar o único endereço'}), 400
    
    # Deletar
    execute_query("DELETE FROM endereco WHERE id_endereco = %s", (endereco_id,), commit=True)
    
    # Se deletou o principal, tornar outro como principal
    if endereco['principal']:
        execute_query("""
            UPDATE endereco SET principal = TRUE 
            WHERE id_usuario = %s 
            ORDER BY id_endereco LIMIT 1
        """, (request.user_id,), commit=True)
    
    return jsonify({'message': 'Endereço deletado com sucesso'})

@enderecos_bp.route('/<int:endereco_id>/principal', methods=['PUT'])
@token_required
def definir_principal(endereco_id):
    """Define um endereço como principal"""
    
    # Verificar se endereço pertence ao usuário
    endereco = execute_query("""
        SELECT * FROM endereco WHERE id_endereco = %s AND id_usuario = %s
    """, (endereco_id, request.user_id), fetch_one=True)
    
    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404
    
    # Remover principal de todos
    execute_query("""
        UPDATE endereco SET principal = FALSE WHERE id_usuario = %s
    """, (request.user_id,), commit=True)
    
    # Definir novo principal
    execute_query("""
        UPDATE endereco SET principal = TRUE WHERE id_endereco = %s
    """, (endereco_id,), commit=True)
    
    return jsonify({'message': 'Endereço principal definido com sucesso'})