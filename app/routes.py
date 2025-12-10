from flask import Blueprint, jsonify, request, render_template
from app.models import Ganho, Abastecimento
from datetime import date

# Blueprints
ganhos_bp = Blueprint('ganhos', __name__, url_prefix='/api/ganhos')
abastecimentos_bp = Blueprint('abastecimentos', __name__, url_prefix='/api/abastecimentos')
dashboard_bp = Blueprint('dashboard', __name__)

# ==================== ROTAS GANHOS ====================

@ganhos_bp.route('', methods=['GET'])
def listar_ganhos():
    ganhos = Ganho.listar()
    return jsonify([{
        'id': g[0],
        'ganho': g[1],
        'kmrodado': g[2],
        'mediacar': g[3],
        'data': g[4],
        'lucro': g[5]
    } for g in ganhos])

@ganhos_bp.route('/<int:id>', methods=['GET'])
def obter_ganho(id):
    ganho = Ganho.obter(id)
    if ganho:
        return jsonify({
            'id': ganho[0],
            'ganho': ganho[1],
            'kmrodado': ganho[2],
            'mediacar': ganho[3],
            'data': ganho[4],
            'lucro': ganho[5]
        })
    return jsonify({'erro': 'Ganho não encontrado'}), 404

@ganhos_bp.route('', methods=['POST'])
def criar_ganho():
    data = request.json
    ganho = data.get('ganho')
    kmrodado = data.get('kmrodado')
    mediacar = data.get('mediacar')
    data_entrada = data.get('data', '')
    
    # Obter custolt do último abastecimento
    custolt = Abastecimento.obter_ultimo_custolt()
    if custolt is None:
        custolt = data.get('custolt')
        if custolt is None:
            return jsonify({'erro': 'Custolt não fornecido e nenhum abastecimento cadastrado'}), 400
    
    # Calcular lucro
    lucro = ganho - ((kmrodado / mediacar) * custolt)
    
    if Ganho.criar(ganho, kmrodado, mediacar, data_entrada, lucro):
        # Retornar também o total da semana
        total_semana = Ganho.total_semana_atual()
        return jsonify({
            'sucesso': True,
            'lucro': lucro,
            'total_semana': total_semana,
            'custolt_utilizado': custolt
        }), 201
    return jsonify({'erro': 'Erro ao criar ganho'}), 500

@ganhos_bp.route('/<int:id>', methods=['PUT'])
def atualizar_ganho(id):
    data = request.json
    ganho = data.get('ganho')
    kmrodado = data.get('kmrodado')
    mediacar = data.get('mediacar')
    data_entrada = data.get('data')
    
    # Obter custolt do último abastecimento
    custolt = Abastecimento.obter_ultimo_custolt()
    if custolt is None:
        custolt = data.get('custolt')
        if custolt is None:
            return jsonify({'erro': 'Custolt não fornecido'}), 400
    
    # Recalcular lucro
    lucro = ganho - ((kmrodado / mediacar) * custolt)
    
    if Ganho.atualizar(id, ganho, kmrodado, mediacar, data_entrada, lucro):
        return jsonify({
            'sucesso': True,
            'lucro': lucro
        })
    return jsonify({'erro': 'Erro ao atualizar ganho'}), 500

@ganhos_bp.route('/<int:id>', methods=['DELETE'])
def deletar_ganho(id):
    if Ganho.deletar(id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Erro ao deletar ganho'}), 500

@ganhos_bp.route('/total/<mes>', methods=['GET'])
def total_mes(mes):
    total = Ganho.total_por_mes(mes)
    return jsonify({'mes': mes, 'total': total})

# ==================== ROTAS ABASTECIMENTOS ====================

@abastecimentos_bp.route('', methods=['GET'])
def listar_abastecimentos():
    abastecimentos = Abastecimento.listar()
    return jsonify([{
        'id': a[0],
        'custo': a[1],
        'custolt': a[2],
        'data': a[3],
        'litrosa': a[4]
    } for a in abastecimentos])

@abastecimentos_bp.route('/<int:id>', methods=['GET'])
def obter_abastecimento(id):
    abastecimento = Abastecimento.obter(id)
    if abastecimento:
        return jsonify({
            'id': abastecimento[0],
            'custo': abastecimento[1],
            'custolt': abastecimento[2],
            'data': abastecimento[3],
            'litrosa': abastecimento[4]
        })
    return jsonify({'erro': 'Abastecimento não encontrado'}), 404

@abastecimentos_bp.route('', methods=['POST'])
def criar_abastecimento():
    data = request.json
    custo = data.get('custo')
    custolt = data.get('custolt')
    data_entrada = data.get('data', '')
    litrosa = custo / custolt if custolt > 0 else 0
    
    if Abastecimento.criar(custo, custolt, data_entrada, litrosa):
        return jsonify({
            'sucesso': True,
            'litrosa': litrosa
        }), 201
    return jsonify({'erro': 'Erro ao criar abastecimento'}), 500

@abastecimentos_bp.route('/<int:id>', methods=['PUT'])
def atualizar_abastecimento(id):
    data = request.json
    custo = data.get('custo')
    custolt = data.get('custolt')
    data_entrada = data.get('data')
    litrosa = custo / custolt if custolt > 0 else 0
    
    if Abastecimento.atualizar(id, custo, custolt, data_entrada, litrosa):
        return jsonify({
            'sucesso': True,
            'litrosa': litrosa
        })
    return jsonify({'erro': 'Erro ao atualizar abastecimento'}), 500

@abastecimentos_bp.route('/<int:id>', methods=['DELETE'])
def deletar_abastecimento(id):
    if Abastecimento.deletar(id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Erro ao deletar abastecimento'}), 500

@abastecimentos_bp.route('/ultimo/custolt', methods=['GET'])
def ultimo_custolt():
    custolt = Abastecimento.obter_ultimo_custolt()
    if custolt is not None:
        return jsonify({'custolt': custolt})
    return jsonify({'custolt': None})

# ==================== ROTAS DASHBOARD ====================

@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    ganhos = Ganho.listar()
    total_semana = Ganho.total_semana_atual()
    
    # Calcular total do mês (usando mês atual)
    mes_atual = date.today().strftime('%m-%Y')
    total_mes = Ganho.total_por_mes(mes_atual)
    
    # Contar registros
    total_ganhos = len(ganhos)
    abastecimentos = Abastecimento.listar()
    total_abastecimentos = len(abastecimentos)
    
    return jsonify({
        'total_ganhos_registrados': total_ganhos,
        'total_abastecimentos_registrados': total_abastecimentos,
        'total_semana_atual': total_semana,
        'total_mes_atual': total_mes,
        'ultimos_ganhos': [
            {
                'id': g[0],
                'ganho': g[1],
                'kmrodado': g[2],
                'mediacar': g[3],
                'data': g[4],
                'lucro': g[5]
            } for g in ganhos
        ]
    })
