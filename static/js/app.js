// API Base URL
const API_BASE = '/api';
let editingId = null;
let editingType = null;
let ganhos_chart = null;
let semanas_chart = null;

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setupNavigation();
    setupForms();
    // Auto-atualizar dashboard a cada 30 segundos
    setInterval(loadDashboard, 30000);
    // initialize table paginators (after DOM elements exist)
    try {
        createTablePaginator({ tbodyId: 'ganhos-list', pageSizeSelectId: 'ganhos-page-size', paginationId: 'ganhos-pagination', infoId: 'ganhos-info' });
        createTablePaginator({ tbodyId: 'abastecimentos-list', pageSizeSelectId: 'abastecimentos-page-size', paginationId: 'abastecimentos-pagination', infoId: 'abastecimentos-info' });
    } catch (e) {
        // function may not exist yet if file loaded in different order; ignore silently
        console.warn('Paginator init skipped (will initialize on page change if needed).', e);
    }
});

// ==================== NAVEGAÇÃO ====================

function setupNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        // Skip anchor links that navigate to other pages (e.g., Perfil / Sair)
        if (btn.tagName === 'A') return;

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
        // When switching sections, close any open edit forms to avoid stale state
        closeForms();
        section.classList.add('active');
    }
}

function closeForms() {
    // Hide ganho form if present
    const ganhoForm = document.getElementById('ganho-form');
    if (ganhoForm && !ganhoForm.classList.contains('hidden')) {
        ganhoForm.classList.add('hidden');
    }
    // Hide abastecimento form if present
    const abastecimentoForm = document.getElementById('abastecimento-form');
    if (abastecimentoForm && !abastecimentoForm.classList.contains('hidden')) {
        abastecimentoForm.classList.add('hidden');
    }
    // reset editing state
    editingId = null;
    editingType = null;
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

/* ---------- Table Pagination Utility ---------- */
function createTablePaginator({ tbodyId, pageSizeSelectId, paginationId, infoId }) {
    const tbody = document.getElementById(tbodyId);
    const pageSizeSelect = document.getElementById(pageSizeSelectId);
    const pagination = document.getElementById(paginationId);
    const info = document.getElementById(infoId);

    if (!tbody || !pageSizeSelect || !pagination || !info) return;

    let rows = Array.from(tbody.querySelectorAll('tr'));
    let pageSize = parseInt(pageSizeSelect.value, 10) || 10;
    let currentPage = 1;

    function refreshRows() {
        rows = Array.from(tbody.querySelectorAll('tr'));
        render();
    }

    function render() {
        const total = rows.length;
        const totalPages = Math.max(1, Math.ceil(total / pageSize));
        if (currentPage > totalPages) currentPage = totalPages;

        // hide all rows
        rows.forEach(r => r.style.display = 'none');

        // show page rows
        const start = (currentPage - 1) * pageSize;
        const end = Math.min(total, start + pageSize);
        for (let i = start; i < end; i++) rows[i].style.display = '';

        // update info
        info.textContent = total === 0 ? 'Nenhum registro' : `Exibindo ${start + 1}-${end} de ${total}`;

        // build pagination buttons
        pagination.innerHTML = '';
        if (totalPages <= 1) return;

        const prev = document.createElement('button');
        prev.textContent = '◀';
        prev.className = 'page-btn';
        prev.disabled = currentPage === 1;
        prev.addEventListener('click', () => { currentPage = Math.max(1, currentPage - 1); render(); });
        pagination.appendChild(prev);

        const range = 3;
        const startPage = Math.max(1, currentPage - range);
        const endPage = Math.min(totalPages, currentPage + range);
        for (let p = startPage; p <= endPage; p++) {
            const b = document.createElement('button');
            b.textContent = p;
            b.className = 'page-btn' + (p === currentPage ? ' active' : '');
            b.addEventListener('click', () => { currentPage = p; render(); });
            pagination.appendChild(b);
        }

        const next = document.createElement('button');
        next.textContent = '▶';
        next.className = 'page-btn';
        next.disabled = currentPage === totalPages;
        next.addEventListener('click', () => { currentPage = Math.min(totalPages, currentPage + 1); render(); });
        pagination.appendChild(next);
    }

    pageSizeSelect.addEventListener('change', () => {
        pageSize = parseInt(pageSizeSelect.value, 10) || 10;
        currentPage = 1;
        render();
    });

    // observe tbody changes to refresh rows when rows are added/removed
    const mo = new MutationObserver(() => refreshRows());
    mo.observe(tbody, { childList: true, subtree: false });

    // initial
    refreshRows();
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
            tbody.innerHTML = '<tr><td colspan="6" class="empty-message">❌ Nenhum ganho cadastrado.</td></tr>';
            return;
        }

        tbody.innerHTML = ganhos.map(g => `
            <tr>
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
            tbody.innerHTML = '<tr><td colspan="5" class="empty-message">❌ Nenhum abastecimento cadastrado.</td></tr>';
            return;
        }

        tbody.innerHTML = abastecimentos.map(a => `
            <tr>
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
    // Utility: parse dates in 'DD-MM-YYYY' or 'DD/MM/YYYY' into numeric parts and normalized 'YYYY-MM-DD'
    function parseDateParts(s) {
        if (!s) return null;
        const sep = s.includes('-') ? '-' : (s.includes('/') ? '/' : null);
        if (!sep) return null;
        const parts = s.split(sep);
        if (parts.length !== 3) return null;
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const year = parseInt(parts[2], 10);
        if (Number.isNaN(day) || Number.isNaN(month) || Number.isNaN(year)) return null;
        const mm = String(month).padStart(2, '0');
        const dd = String(day).padStart(2, '0');
        return { day, month, year, ymd: `${year}-${mm}-${dd}` };
    }
    // Preparar dados dos últimos 7 dias
    const ultimosDias = [];
    const dados = [];
    
    for (let i = 6; i >= 0; i--) {
        const data = new Date();
        data.setDate(data.getDate() - i);
        const dataStr = data.toLocaleDateString('pt-BR', { weekday: 'short', month: 'numeric', day: 'numeric' });
        ultimosDias.push(dataStr);
        
        const targetYmd = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}-${String(data.getDate()).padStart(2, '0')}`;
        const total = ganhos
            .map(g => ({ parts: parseDateParts(g.data), lucro: Number(g.lucro) || 0 }))
            .filter(x => x.parts && x.parts.ymd === targetYmd)
            .reduce((sum, x) => sum + x.lucro, 0);
        dados.push(total);
    }

    // Gráfico de barras - Lucro Diário (visualmente igual ao por semanas)
    const ctx1 = document.getElementById('ganhos-chart');
    if (ctx1) {
        if (ganhos_chart) {
            ganhos_chart.destroy();
        }

        ganhos_chart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: ultimosDias,
                datasets: [{
                    label: 'Lucro Diário (R$)',
                    data: dados,
                    backgroundColor: '#004E89',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const val = context.parsed.y ?? context.parsed;
                                return `R$ ${Number(val).toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Gráfico por semanas do mês (barras)
    // Função utilitária para converter 'DD-MM-YYYY' para Date
    function parseDateBR(s) {
        if (!s) return null;
        const parts = s.split('-');
        if (parts.length !== 3) return null;
        // YYYY-MM-DD
        return new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
    }

    const ctx2 = document.getElementById('semanas-chart');
    if (ctx2) {
        // calcular semanas do mês atual
        const hoje = new Date();
        const month = hoje.getMonth();
        const year = hoje.getFullYear();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const numWeeks = Math.ceil(daysInMonth / 7);

        const weekLabels = Array.from({ length: numWeeks }, (_, i) => `Semana ${i + 1}`);
        const weekTotals = new Array(numWeeks).fill(0);

        const ganhosMes = ganhos.map(g => ({ parts: parseDateParts(g.data), lucro: Number(g.lucro) || 0 })).filter(x => x.parts && x.parts.year === year && x.parts.month - 1 === month);

        ganhosMes.forEach(g => {
            const day = g.parts.day;
            const weekIndex = Math.max(0, Math.min(numWeeks - 1, Math.ceil(day / 7) - 1));
            weekTotals[weekIndex] += g.lucro;
        });

        if (semanas_chart) semanas_chart.destroy();

        semanas_chart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: weekLabels,
                datasets: [{
                    label: 'Lucro por Semana (R$)',
                    data: weekTotals,
                    backgroundColor: '#004E89'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
    // Debug helper: if enabled in browser console, print day mapping
    if (window.DEBUG_DASHBOARD) {
        console.log('Daily chart dates and totals:', ultimosDias.map((label, idx) => ({ label, total: dados[idx] })));
        console.log('Weekly totals:', weekTotals);
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
