// API Base URL
const API_BASE = '/api';
let editingId = null;
let editingType = null;
let ganhos_chart = null;
let pie_chart = null;

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setupNavigation();
    setupForms();
    // Auto-atualizar dashboard a cada 30 segundos
    setInterval(loadDashboard, 30000);
});

// ==================== NAVEGAÇÃO ====================

function setupNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            showSection(section);
            
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            if (section === 'ganhos') {
                loadGanhos();
            } else if (section === 'abastecimentos') {
                loadAbastecimentos();
            } else if (section === 'dashboard') {
                loadDashboard();
            } else if (section === 'relatorios') {
                // Inicializar mês atual
                const hoje = new Date();
                const mes = String(hoje.getMonth() + 1).padStart(2, '0');
                const ano = hoje.getFullYear();
                document.getElementById('mes-filtro').value = `${ano}-${mes}`;
            }
        });
    });
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(s => s.classList.remove('active'));
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }
}

// ==================== FORMS ====================

function toggleForm(formId) {
    const form = document.getElementById(formId);
    form.classList.toggle('hidden');
    if (!form.classList.contains('hidden')) {
        form.reset();
        editingId = null;
        editingType = null;
        if (formId === 'ganho-form') {
            carregarCustolt();
        }
    }
}

function setupForms() {
    // Form Ganho
    const ganhoForm = document.getElementById('ganho-form');
    if (ganhoForm) {
        ganhoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            salvarGanho();
        });
    }

    // Auto-calcular litros
    const custo = document.getElementById('abastecimento-custo');
    const custolt = document.getElementById('abastecimento-custolt');
    const litrosa = document.getElementById('abastecimento-litrosa');

    if (custo && custolt && litrosa) {
        [custo, custolt].forEach(input => {
            input.addEventListener('input', () => {
                if (custo.value && custolt.value) {
                    litrosa.value = (parseFloat(custo.value) / parseFloat(custolt.value)).toFixed(2);
                }
            });
        });
    }

    // Form Abastecimento
    const abastecimentoForm = document.getElementById('abastecimento-form');
    if (abastecimentoForm) {
        abastecimentoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            salvarAbastecimento();
        });
    }
}

// ==================== GANHOS ====================

async function carregarCustolt() {
    try {
        const response = await fetch(`${API_BASE}/abastecimentos/ultimo/custolt`);
        const data = await response.json();
        
        const custoltField = document.getElementById('custolt-field');
        const custoltInput = document.getElementById('ganho-custolt');
        const custoltInfo = document.getElementById('custolt-info');

        if (data.custolt !== null) {
            custoltField.style.display = 'none';
            custoltInput.value = data.custolt;
            custoltInfo.innerHTML = `ℹ️ Usando custo por litro do último abastecimento: R$ ${data.custolt.toFixed(2)}/L`;
            custoltInfo.classList.add('show');
        } else {
            custoltField.style.display = 'block';
            custoltInfo.innerHTML = `⚠️ Nenhum abastecimento registrado. Digite o custo por litro:`;
            custoltInfo.classList.add('show');
        }
    } catch (error) {
        console.error('Erro ao carregar custolt:', error);
    }
}

async function salvarGanho() {
    const valor = parseFloat(document.getElementById('ganho-valor').value);
    const km = parseInt(document.getElementById('ganho-km').value);
    const media = parseFloat(document.getElementById('ganho-media').value);
    const data = document.getElementById('ganho-data').value;
    const custolt = parseFloat(document.getElementById('ganho-custolt').value);

    if (!valor || !km || !media || !custolt) {
        alert('Preencha todos os campos obrigatórios');
        return;
    }

    const payload = {
        ganho: valor,
        kmrodado: km,
        mediacar: media,
        data: data,
        custolt: custolt
    };

    try {
        const method = editingId ? 'PUT' : 'POST';
        const url = editingId ? `${API_BASE}/ganhos/${editingId}` : `${API_BASE}/ganhos`;

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.sucesso) {
            alert(`Ganho ${editingId ? 'atualizado' : 'cadastrado'} com sucesso!`);
            document.getElementById('ganho-form').classList.add('hidden');
            loadGanhos();
            loadDashboard();
        } else {
            alert('Erro: ' + (result.erro || 'Falha ao salvar ganho'));
        }
    } catch (error) {
        console.error('Erro ao salvar ganho:', error);
        alert('Erro ao salvar ganho');
    }
}

async function loadGanhos() {
    try {
        const response = await fetch(`${API_BASE}/ganhos`);
        const ganhos = await response.json();

        const tbody = document.getElementById('ganhos-list');
        if (ganhos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-message">❌ Nenhum ganho cadastrado.</td></tr>';
            return;
        }

        tbody.innerHTML = ganhos.map(g => `
            <tr>
                <td>${g.id}</td>
                <td>${g.data}</td>
                <td>R$ ${g.ganho.toFixed(2)}</td>
                <td>${g.kmrodado}</td>
                <td>${g.mediacar.toFixed(1)}</td>
                <td>R$ ${g.lucro.toFixed(2)}</td>
                <td>
                    <button class="btn btn-edit" onclick="editarGanho(${g.id})">Editar</button>
                    <button class="btn btn-danger" onclick="deletarGanho(${g.id})">Deletar</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar ganhos:', error);
    }
}

async function editarGanho(id) {
    try {
        const response = await fetch(`${API_BASE}/ganhos/${id}`);
        const ganho = await response.json();

        document.getElementById('ganho-valor').value = ganho.ganho;
        document.getElementById('ganho-km').value = ganho.kmrodado;
        document.getElementById('ganho-media').value = ganho.mediacar;
        document.getElementById('ganho-data').value = ganho.data;

        editingId = id;
        editingType = 'ganho';

        const form = document.getElementById('ganho-form');
        form.classList.remove('hidden');
        form.scrollIntoView({ behavior: 'smooth' });

        carregarCustolt();
    } catch (error) {
        console.error('Erro ao carregar ganho:', error);
        alert('Erro ao carregar dados do ganho');
    }
}

async function deletarGanho(id) {
    if (!confirm('Tem certeza que deseja deletar este ganho?')) return;

    try {
        const response = await fetch(`${API_BASE}/ganhos/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.sucesso) {
            alert('Ganho deletado com sucesso!');
            loadGanhos();
            loadDashboard();
        } else {
            alert('Erro ao deletar ganho');
        }
    } catch (error) {
        console.error('Erro ao deletar ganho:', error);
    }
}

// ==================== ABASTECIMENTOS ====================

async function salvarAbastecimento() {
    const custo = parseFloat(document.getElementById('abastecimento-custo').value);
    const custolt = parseFloat(document.getElementById('abastecimento-custolt').value);
    const data = document.getElementById('abastecimento-data').value;

    if (!custo || !custolt) {
        alert('Preencha todos os campos obrigatórios');
        return;
    }

    const payload = {
        custo: custo,
        custolt: custolt,
        data: data
    };

    try {
        const method = editingId ? 'PUT' : 'POST';
        const url = editingId ? `${API_BASE}/abastecimentos/${editingId}` : `${API_BASE}/abastecimentos`;

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.sucesso) {
            alert(`Abastecimento ${editingId ? 'atualizado' : 'cadastrado'} com sucesso!`);
            document.getElementById('abastecimento-form').classList.add('hidden');
            loadAbastecimentos();
        } else {
            alert('Erro: ' + (result.erro || 'Falha ao salvar abastecimento'));
        }
    } catch (error) {
        console.error('Erro ao salvar abastecimento:', error);
        alert('Erro ao salvar abastecimento');
    }
}

async function loadAbastecimentos() {
    try {
        const response = await fetch(`${API_BASE}/abastecimentos`);
        const abastecimentos = await response.json();

        const tbody = document.getElementById('abastecimentos-list');
        if (abastecimentos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-message">❌ Nenhum abastecimento cadastrado.</td></tr>';
            return;
        }

        tbody.innerHTML = abastecimentos.map(a => `
            <tr>
                <td>${a.id}</td>
                <td>${a.data}</td>
                <td>R$ ${a.custo.toFixed(2)}</td>
                <td>R$ ${a.custolt.toFixed(2)}</td>
                <td>${a.litrosa ? a.litrosa.toFixed(2) + 'L' : 'N/A'}</td>
                <td>
                    <button class="btn btn-edit" onclick="editarAbastecimento(${a.id})">Editar</button>
                    <button class="btn btn-danger" onclick="deletarAbastecimento(${a.id})">Deletar</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar abastecimentos:', error);
    }
}

async function editarAbastecimento(id) {
    try {
        const response = await fetch(`${API_BASE}/abastecimentos/${id}`);
        const abastecimento = await response.json();

        document.getElementById('abastecimento-custo').value = abastecimento.custo;
        document.getElementById('abastecimento-custolt').value = abastecimento.custolt;
        document.getElementById('abastecimento-litrosa').value = abastecimento.litrosa || '';
        document.getElementById('abastecimento-data').value = abastecimento.data;

        editingId = id;
        editingType = 'abastecimento';

        const form = document.getElementById('abastecimento-form');
        form.classList.remove('hidden');
        form.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Erro ao carregar abastecimento:', error);
        alert('Erro ao carregar dados do abastecimento');
    }
}

async function deletarAbastecimento(id) {
    if (!confirm('Tem certeza que deseja deletar este abastecimento?')) return;

    try {
        const response = await fetch(`${API_BASE}/abastecimentos/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.sucesso) {
            alert('Abastecimento deletado com sucesso!');
            loadAbastecimentos();
        } else {
            alert('Erro ao deletar abastecimento');
        }
    } catch (error) {
        console.error('Erro ao deletar abastecimento:', error);
    }
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        // Atualizar stats
        document.getElementById('total-semana').textContent = `R$ ${data.total_semana_atual.toFixed(2)}`;
        document.getElementById('total-mes').textContent = `R$ ${data.total_mes_atual.toFixed(2)}`;
        document.getElementById('total-abastecimentos').textContent = data.total_abastecimentos_registrados;

        // Calcular ganhos de hoje
        const hoje = new Date().toLocaleDateString('pt-BR');
        const ganhos_hoje = data.ultimos_ganhos
            .filter(g => g.data === hoje)
            .reduce((sum, g) => sum + g.lucro, 0);
        document.getElementById('ganhos-hoje').textContent = `R$ ${ganhos_hoje.toFixed(2)}`;

        // Atualizar últimos ganhos
        const tbody = document.getElementById('recent-ganhos');
        if (data.ultimos_ganhos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-message">Nenhum ganho registrado ainda</td></tr>';
        } else {
            tbody.innerHTML = data.ultimos_ganhos.map(g => `
                <tr>
                    <td>${g.data}</td>
                    <td>R$ ${g.ganho.toFixed(2)}</td>
                    <td>${g.kmrodado}</td>
                    <td><strong>R$ ${g.lucro.toFixed(2)}</strong></td>
                </tr>
            `).join('');
        }

        // Carregar dados para gráficos
        carregarGraficos(data.ultimos_ganhos);

        // Atualizar timestamp
        const agora = new Date().toLocaleTimeString('pt-BR');
        document.querySelector('.last-sync').textContent = `Última sincronização: ${agora}`;
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

// ==================== GRÁFICOS ====================

function carregarGraficos(ganhos) {
    // Preparar dados dos últimos 7 dias
    const ultimosDias = [];
    const dados = [];
    
    for (let i = 6; i >= 0; i--) {
        const data = new Date();
        data.setDate(data.getDate() - i);
        const dataStr = data.toLocaleDateString('pt-BR', { weekday: 'short', month: 'numeric', day: 'numeric' });
        ultimosDias.push(dataStr);
        
        const dataFormatada = data.toLocaleDateString('pt-BR');
        const total = ganhos
            .filter(g => g.data === dataFormatada)
            .reduce((sum, g) => sum + g.lucro, 0);
        dados.push(total);
    }

    // Gráfico de linha
    const ctx1 = document.getElementById('ganhos-chart');
    if (ctx1) {
        if (ganhos_chart) {
            ganhos_chart.destroy();
        }

        ganhos_chart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: ultimosDias,
                datasets: [{
                    label: 'Lucro Diário (R$)',
                    data: dados,
                    borderColor: '#FF6B35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Gráfico de pizza
    const ctx2 = document.getElementById('pie-chart');
    if (ctx2 && dados.length > 0) {
        if (pie_chart) {
            pie_chart.destroy();
        }

        pie_chart = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ultimosDias,
                datasets: [{
                    data: dados,
                    backgroundColor: [
                        '#FF6B35',
                        '#004E89',
                        '#06A77D',
                        '#F77F00',
                        '#D62828',
                        '#8338EC',
                        '#FFBE0B'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// ==================== RELATÓRIOS ====================

async function gerarRelatorioMes() {
    const mesInput = document.getElementById('mes-filtro').value;
    
    if (!mesInput) {
        alert('Selecione um mês');
        return;
    }

    const [ano, mes] = mesInput.split('-');
    const mesFormatado = `${mes}-${ano}`;

    try {
        const response = await fetch(`${API_BASE}/ganhos/total/${mesFormatado}`);
        const data = await response.json();

        // Buscar ganhos do mês
        const ganhos = await fetch(`${API_BASE}/ganhos`).then(r => r.json());
        const ganhosMes = ganhos.filter(g => g.data.endsWith(`-${mes}-${ano}`));

        // Calcular estatísticas
        const total = ganhosMes.reduce((sum, g) => sum + g.lucro, 0);
        const media = ganhosMes.length > 0 ? total / ganhosMes.length : 0;

        // Atualizar HTML
        document.getElementById('relatorio-total').textContent = `R$ ${total.toFixed(2)}`;
        document.getElementById('relatorio-count').textContent = ganhosMes.length;
        document.getElementById('relatorio-media').textContent = `R$ ${media.toFixed(2)}`;

        // Preencher tabela
        const tbody = document.getElementById('relatorio-ganhos');
        tbody.innerHTML = ganhosMes.map(g => `
            <tr>
                <td>${g.data}</td>
                <td>R$ ${g.ganho.toFixed(2)}</td>
                <td>${g.kmrodado}</td>
                <td>R$ ${g.lucro.toFixed(2)}</td>
            </tr>
        `).join('');

        // Exibir container
        document.getElementById('relatorio-container').style.display = 'block';
    } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        alert('Erro ao gerar relatório');
    }
}
