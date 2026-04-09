from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query
import re

frete_bp = Blueprint('frete', __name__, url_prefix='/api/frete')

def limpar_cep(cep):
    """Remove caracteres não numéricos do CEP"""
    return re.sub(r'\D', '', cep)

@frete_bp.route('/calcular', methods=['POST'])
@token_required
def calcular_frete():
    data = request.json
    cep_destino = limpar_cep(data.get('cep', ''))
    
    if not cep_destino or len(cep_destino) != 8:
        return jsonify({'error': 'CEP inválido'}), 400
    
    # Buscar itens do carrinho
    itens_carrinho = execute_query("""
        SELECT ic.*, p.peso, p.preco, p.nome
        FROM item_carrinho ic
        JOIN produto p ON ic.id_produto = p.id_produto
        JOIN carrinho c ON ic.id_carrinho = c.id_carrinho
        WHERE c.id_usuario = %s
    """, (request.user_id,), fetch_all=True)
    
    if not itens_carrinho:
        return jsonify({'error': 'Carrinho vazio'}), 400
    
    # Calcular peso total (assumindo peso padrão 0.5kg se não tiver)
    peso_total = sum(item.get('peso', 0.5) * item['quantidade'] for item in itens_carrinho)
    
    # Buscar transportadoras com regras de frete para o CEP
    transportadoras = execute_query("""
        SELECT t.id_transp, t.nome, t.prazo_medio, tf.valor_kg
        FROM transportadora t
        JOIN tabela_frete tf ON t.id_transp = tf.id_transp
        WHERE %s BETWEEN REPLACE(tf.cep_inicio, '-', '') AND REPLACE(tf.cep_fim, '-', '')
    """, (cep_destino,), fetch_all=True)
    
    if not transportadoras:
        # Regra padrão caso não encontre
        transportadoras = [
            {'id_transp': 1, 'nome': 'Correios - PAC', 'prazo_medio': 5, 'valor_kg': 8.00},
            {'id_transp': 2, 'nome': 'Correios - Sedex', 'prazo_medio': 2, 'valor_kg': 15.00}
        ]
    
    # Calcular frete para cada transportadora
    opcoes_frete = []
    for transp in transportadoras:
        valor_frete = peso_total * transp['valor_kg']
        # Valor mínimo de frete
        if valor_frete < 10:
            valor_frete = 10.00
            
        opcoes_frete.append({
            'id_transportadora': transp['id_transp'],
            'transportadora': transp['nome'],
            'valor': round(valor_frete, 2),
            'prazo': transp['prazo_medio'],
            'prazo_texto': f"{transp['prazo_medio']} dias úteis"
        })
    
    return jsonify({
        'cep': cep_destino,
        'peso_total': round(peso_total, 2),
        'opcoes': opcoes_frete
    })

@frete_bp.route('/transportadoras', methods=['GET'])
def listar_transportadoras():
    """Listar todas as transportadoras disponíveis"""
    transportadoras = execute_query("""
        SELECT id_transp, nome, prazo_medio FROM transportadora WHERE 1=1
    """, fetch_all=True)
    
    return jsonify(transportadoras)