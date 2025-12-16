from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from app.models import Ganho, Abastecimento, User
from datetime import date

# Blueprints
ganhos_bp = Blueprint('ganhos', __name__, url_prefix='/api/ganhos')
abastecimentos_bp = Blueprint('abastecimentos', __name__, url_prefix='/api/abastecimentos')
dashboard_bp = Blueprint('dashboard', __name__)
app_home = Blueprint('login', __name__)
app_cad = Blueprint('cadastro', __name__)

# ==================== ROTAS GANHOS ====================

@ganhos_bp.route('', methods=['GET'])
def listar_ganhos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    ganhos = Ganho.listar(user_id)
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    ganho = Ganho.obter(id, user_id)
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401

    custolt = Abastecimento.obter_ultimo_custolt(user_id)
    if custolt is None:
        custolt = data.get('custolt')
        if custolt is None:
            return jsonify({'erro': 'Custolt não fornecido e nenhum abastecimento cadastrado'}), 400
    
    # Calcular lucro
    lucro = ganho - ((kmrodado / mediacar) * custolt)
    
    if Ganho.criar(user_id, ganho, kmrodado, mediacar, data_entrada, lucro):
        # Retornar também o total da semana
        total_semana = Ganho.total_semana_atual(user_id)
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    custolt = Abastecimento.obter_ultimo_custolt(user_id)
    if custolt is None:
        custolt = data.get('custolt')
        if custolt is None:
            return jsonify({'erro': 'Custolt não fornecido'}), 400
    
    # Recalcular lucro
    lucro = ganho - ((kmrodado / mediacar) * custolt)
    
    if Ganho.atualizar(id, user_id, ganho, kmrodado, mediacar, data_entrada, lucro):
        return jsonify({
            'sucesso': True,
            'lucro': lucro
        })
    return jsonify({'erro': 'Erro ao atualizar ganho'}), 500

@ganhos_bp.route('/<int:id>', methods=['DELETE'])
def deletar_ganho(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    if Ganho.deletar(id, user_id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Erro ao deletar ganho'}), 500

@ganhos_bp.route('/total/<mes>', methods=['GET'])
def total_mes(mes):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    total = Ganho.total_por_mes(mes, user_id)
    return jsonify({'mes': mes, 'total': total})

# ==================== ROTAS ABASTECIMENTOS ====================

@abastecimentos_bp.route('', methods=['GET'])
def listar_abastecimentos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    abastecimentos = Abastecimento.listar(user_id)
    return jsonify([{
        'id': a[0],
        'custo': a[1],
        'custolt': a[2],
        'data': a[3],
        'litrosa': a[4]
    } for a in abastecimentos])

@abastecimentos_bp.route('/<int:id>', methods=['GET'])
def obter_abastecimento(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    abastecimento = Abastecimento.obter(id, user_id)
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401

    litrosa = custo / custolt if custolt > 0 else 0
    
    if Abastecimento.criar(user_id, custo, custolt, data_entrada, litrosa):
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401

    litrosa = custo / custolt if custolt > 0 else 0
    
    if Abastecimento.atualizar(id, user_id, custo, custolt, data_entrada, litrosa):
        return jsonify({
            'sucesso': True,
            'litrosa': litrosa
        })
    return jsonify({'erro': 'Erro ao atualizar abastecimento'}), 500

@abastecimentos_bp.route('/<int:id>', methods=['DELETE'])
def deletar_abastecimento(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401
    if Abastecimento.deletar(id, user_id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Erro ao deletar abastecimento'}), 500

@abastecimentos_bp.route('/ultimo/custolt', methods=['GET'])
def ultimo_custolt():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'custolt': None}), 401

    custolt = Abastecimento.obter_ultimo_custolt(user_id)
    if custolt is not None:
        return jsonify({'custolt': custolt})
    return jsonify({'custolt': None})

# ==================== ROTAS DASHBOARD ====================

@dashboard_bp.route('/app')
def index():
    # Protege a rota: exige login
    if 'user' not in session:
        flash('É necessário fazer login para acessar o dashboard')
        return redirect(url_for('login.home'))
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Não autenticado'}), 401

    ganhos = Ganho.listar(user_id)
    total_semana = Ganho.total_semana_atual(user_id)
    
    # Calcular total do mês (usando mês atual)
    mes_atual = date.today().strftime('%m-%Y')
    total_mes = Ganho.total_por_mes(mes_atual, user_id)
    
    # Contar registros
    total_ganhos = len(ganhos)
    abastecimentos = Abastecimento.listar(user_id)
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

@app_home.route("/")
def home():
    return render_template("login.html")  
@app_home.route("/login", methods=['POST'])
def do_login():
    login_val = request.form.get('usuario')
    senha = request.form.get('senha')
    if not login_val or not senha:
        flash('Preencha usuário e senha')
        return redirect(url_for('login.home'))

    user = User.autenticar(login_val, senha)
    if user:
        # salvar no session e redirecionar para dashboard
        session['user'] = user['usuario']
        session['user_id'] = user['id']
        return redirect(url_for('dashboard.index'))

    flash('Usuário ou senha inválidos')
    return redirect(url_for('login.home'))


@app_home.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash('Você saiu da sua conta')
    return redirect(url_for('login.home'))


@app_home.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Faça login para acessar o perfil')
        return redirect(url_for('login.home'))

    # Buscar dados do usuário para exibir
    conn = None
    try:
        from app.database import db
        conn = db.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT usuario, email, telefone FROM usuarios WHERE id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return render_template('profile.html', usuario=row[0], email=row[1], telefone=row[2])
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

    flash('Erro ao carregar perfil')
    return redirect(url_for('dashboard.index'))


@app_home.route('/profile', methods=['POST'])
def profile_update():
    user_id = session.get('user_id')
    if not user_id:
        flash('Faça login para atualizar perfil')
        return redirect(url_for('login.home'))

    usuario = request.form.get('usuario')
    email = request.form.get('email')
    telefone = request.form.get('telefone')

    success, msg = User.atualizar_perfil(user_id, usuario, email, telefone)
    if success:
        flash('Perfil atualizado com sucesso')
    else:
        flash(msg or 'Erro ao atualizar perfil')
    return redirect(url_for('login.profile'))


@app_home.route('/profile/password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        flash('Faça login para alterar senha')
        return redirect(url_for('login.home'))

    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    senha_nova2 = request.form.get('senha_nova2')

    if not senha_nova or senha_nova != senha_nova2:
        flash('Novas senhas não conferem')
        return redirect(url_for('login.profile'))

    success, msg = User.alterar_senha(user_id, senha_atual, senha_nova)
    if success:
        flash('Senha alterada com sucesso')
    else:
        flash(msg or 'Erro ao alterar senha')
    return redirect(url_for('login.profile'))
            
@app_cad.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")  

@app_cad.route("/cadastro", methods=['POST'])
def registro():    
    usuario = request.form.get('usuario')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    senha = request.form.get('senha')

    if not usuario or not email or not senha:
        flash('Preencha todos os campos obrigatórios')
        return redirect(url_for('cadastro.cadastro'))

    success, msg = User.criar_usuario(usuario, email, telefone, senha)
    if success:
        flash('Cadastro realizado com sucesso. Faça login.')
        return redirect(url_for('login.home'))
    else:
        flash(msg or 'Erro ao cadastrar usuário')
        return redirect(url_for('cadastro.cadastro'))