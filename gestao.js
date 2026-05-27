// =====================
// DADOS INICIAIS
// =====================

const coresTurma = [
    'linear-gradient(135deg,#1d4ed8,#60a5fa)',
    'linear-gradient(135deg,#7c3aed,#a855f7)',
    'linear-gradient(135deg,#059669,#34d399)',
    'linear-gradient(135deg,#dc2626,#f87171)',
    'linear-gradient(135deg,#d97706,#fbbf24)',
    'linear-gradient(135deg,#0891b2,#22d3ee)',
    'linear-gradient(135deg,#db2777,#f472b6)',
];

const avatarCores = [
    '#3b82f6','#8b5cf6','#ec4899','#f59e0b',
    '#10b981','#ef4444','#06b6d4','#0ea5e9'
];

let turmas = [
    { id: 1, codigo: '1A', nome: '1º Ano A', prof: 'Prof. Ana Lima',       turno: 'Manhã', cor: coresTurma[0] },
    { id: 2, codigo: '2B', nome: '2º Ano B', prof: 'Prof. Carlos Mendes',  turno: 'Tarde', cor: coresTurma[1] },
    { id: 3, codigo: '3A', nome: '3º Ano A', prof: 'Prof. Beatriz Souza',  turno: 'Manhã', cor: coresTurma[2] },
    { id: 4, codigo: '3B', nome: '3º Ano B', prof: 'Prof. Roberto Alves',  turno: 'Tarde', cor: coresTurma[3] },
    { id: 5, codigo: '4A', nome: '4º Ano A', prof: 'Prof. Luciana Ferraz', turno: 'Manhã', cor: coresTurma[4] },
    { id: 6, codigo: '4B', nome: '4º Ano B', prof: 'Prof. Marcos Teixeira',turno: 'Tarde', cor: coresTurma[5] },
];

let alunos = [
    { id: 1, nome: 'Maria Oliveira',  iniciais: 'MO', cor: avatarCores[0], matricula: '2026001', turma: '3A', status: 'ativo',    turno: 'Manhã' },
    { id: 2, nome: 'João Pereira',    iniciais: 'JP', cor: avatarCores[1], matricula: '2026002', turma: '3A', status: 'destaque', turno: 'Manhã' },
    { id: 3, nome: 'Pedro Ferreira',  iniciais: 'PF', cor: avatarCores[2], matricula: '2026003', turma: '3B', status: 'ativo',    turno: 'Tarde' },
    { id: 4, nome: 'Ana Costa',       iniciais: 'AC', cor: avatarCores[3], matricula: '2026004', turma: '2B', status: 'destaque', turno: 'Manhã' },
    { id: 5, nome: 'Lucas Martins',   iniciais: 'LM', cor: avatarCores[4], matricula: '2026005', turma: '4B', status: 'ativo',    turno: 'Tarde' },
    { id: 6, nome: 'Juliana Santos',  iniciais: 'JS', cor: avatarCores[5], matricula: '2026006', turma: '2B', status: 'ativo',    turno: 'Tarde' },
    { id: 7, nome: 'Gabriel Araújo',  iniciais: 'GA', cor: avatarCores[6], matricula: '2026007', turma: '1A', status: 'destaque', turno: 'Manhã' },
    { id: 8, nome: 'Beatriz Lima',    iniciais: 'BL', cor: avatarCores[7], matricula: '2026008', turma: '2B', status: 'ativo',    turno: 'Tarde' },
];

let filtroAtual = 'todos';
let proximoIdAluno = 9;
let proximoIdTurma = 7;

// =====================
// RENDER TURMAS
// =====================

function renderTurmas() {
    const container = document.getElementById('cards-turmas');
    container.innerHTML = '';

    turmas.forEach(t => {
        const alunosDaTurma = alunos.filter(a => a.turma === t.codigo);
        const avataresHtml = alunosDaTurma.slice(0, 4).map(a =>
            `<div class="av" style="background:${a.cor}">${a.iniciais[0]}</div>`
        ).join('');
        const mais = alunosDaTurma.length > 4
            ? `<span class="av-mais">+${alunosDaTurma.length - 4}</span>` : '';

        const card = document.createElement('div');
        card.className = 'card card-turma';
        card.innerHTML = `
            <div class="card-topo" style="background:${t.cor}">
                <span class="card-num">${t.codigo}</span>
                <span class="card-tag">${t.nome}</span>
            </div>
            <div class="card-corpo">
                <h3>${t.nome} — ${t.turno}</h3>
                <p>${t.prof}</p>
                <div class="aluno-avatares">
                    ${avataresHtml}${mais || (alunosDaTurma.length === 0 ? '<span class="av-mais" style="margin-left:0">Sem alunos</span>' : '')}
                </div>
            </div>
            <div class="card-acoes">
                <button class="btn-excluir-card" onclick="confirmarExclusaoTurma(${t.id}, '${t.nome}')">
                    🗑 Excluir turma
                </button>
            </div>
        `;
        container.appendChild(card);
    });

    atualizarStats();
    popularSelectTurma();
}

// =====================
// RENDER ALUNOS
// =====================

function renderAlunos() {
    const tbody = document.getElementById('tabela-alunos');
    tbody.innerHTML = '';

    const lista = filtroAtual === 'todos'
        ? alunos
        : alunos.filter(a => a.status === filtroAtual);

    if (lista.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center; padding:32px; color:#94a3b8; font-size:14px;">
                    Nenhum aluno encontrado.
                </td>
            </tr>`;
        return;
    }

    lista.forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="aluno-nome-cell">
                    <div class="an-av" style="background:${a.cor}">${a.iniciais}</div>
                    ${a.nome}
                </div>
            </td>
            <td>${a.matricula}</td>
            <td>${a.turma}</td>
            <td><span class="badge ${a.status}">${a.status === 'ativo' ? 'Ativo' : 'Destaque'}</span></td>
            <td>${a.turno}</td>
            <td>
                <button class="btn-linha-excluir" onclick="confirmarExclusaoAluno(${a.id}, '${a.nome}')">
                    Excluir
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    atualizarStats();
}

// =====================
// STATS
// =====================

function atualizarStats() {
    document.getElementById('stat-turmas').textContent = turmas.length;
    document.getElementById('stat-alunos').textContent = alunos.length;
}

// =====================
// FILTROS
// =====================

function filtrar(btn, tipo) {
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('ativo'));
    btn.classList.add('ativo');
    filtroAtual = tipo;
    renderAlunos();
}

// =====================
// POPULAR SELECT DE TURMA NO MODAL
// =====================

function popularSelectTurma() {
    const sel = document.getElementById('novo-turma');
    if (!sel) return;
    sel.innerHTML = '';
    turmas.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.codigo;
        opt.textContent = `${t.codigo} — ${t.nome}`;
        sel.appendChild(opt);
    });
}

// =====================
// MODAIS
// =====================

function abrirModal(id) {
    document.getElementById(id).classList.add('aberto');
}

function fecharModal(id) {
    document.getElementById(id).classList.remove('aberto');
}

// Fechar modal ao clicar fora
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
        if (e.target === this) this.classList.remove('aberto');
    });
});

function abrirModalAluno() {
    popularSelectTurma();
    // Limpar campos
    ['novo-nome','novo-matricula'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    abrirModal('modal-aluno');
}

function abrirModalTurma() {
    ['turma-codigo','turma-nome','turma-prof'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    abrirModal('modal-turma');
}

// =====================
// ADICIONAR ALUNO
// =====================

function adicionarAluno() {
    const nome     = document.getElementById('novo-nome').value.trim();
    const matricula= document.getElementById('novo-matricula').value.trim();
    const turma    = document.getElementById('novo-turma').value;
    const status   = document.getElementById('novo-status').value;
    const turno    = document.getElementById('novo-turno').value;

    if (!nome || !matricula) {
        alert('Preencha nome e matrícula.');
        return;
    }

    // Iniciais (até 2 letras das palavras)
    const partes = nome.split(' ').filter(p => p.length > 0);
    const iniciais = partes.length >= 2
        ? (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
        : nome.substring(0, 2).toUpperCase();

    const cor = avatarCores[proximoIdAluno % avatarCores.length];

    alunos.push({ id: proximoIdAluno++, nome, iniciais, cor, matricula, turma, status, turno });

    fecharModal('modal-aluno');
    renderAlunos();
    renderTurmas();
}

// =====================
// ADICIONAR TURMA
// =====================

function adicionarTurma() {
    const codigo = document.getElementById('turma-codigo').value.trim().toUpperCase();
    const nome   = document.getElementById('turma-nome').value.trim();
    const prof   = document.getElementById('turma-prof').value.trim();
    const turno  = document.getElementById('turma-turno').value;
    const cor    = document.getElementById('turma-cor').value;

    if (!codigo || !nome || !prof) {
        alert('Preencha código, nome e professor.');
        return;
    }

    if (turmas.find(t => t.codigo === codigo)) {
        alert('Já existe uma turma com esse código.');
        return;
    }

    turmas.push({ id: proximoIdTurma++, codigo, nome, prof, turno, cor });

    fecharModal('modal-turma');
    renderTurmas();
}

// =====================
// EXCLUIR ALUNO
// =====================

function confirmarExclusaoAluno(id, nome) {
    document.getElementById('excluir-msg').innerHTML =
        `Tem certeza que deseja excluir o aluno <strong>${nome}</strong>?<br>Essa ação não pode ser desfeita.`;

    const btn = document.getElementById('btn-confirmar-exclusao');
    btn.onclick = () => {
        alunos = alunos.filter(a => a.id !== id);
        fecharModal('modal-excluir');
        renderAlunos();
        renderTurmas();
    };

    abrirModal('modal-excluir');
}

// =====================
// EXCLUIR TURMA
// =====================

function confirmarExclusaoTurma(id, nome) {
    document.getElementById('excluir-msg').innerHTML =
        `Tem certeza que deseja excluir a turma <strong>${nome}</strong>?<br>Os alunos desta turma não serão excluídos.`;

    const btn = document.getElementById('btn-confirmar-exclusao');
    btn.onclick = () => {
        turmas = turmas.filter(t => t.id !== id);
        fecharModal('modal-excluir');
        renderTurmas();
        renderAlunos();
    };

    abrirModal('modal-excluir');
}

// =====================
// ENVIAR AVISO
// =====================

function enviarAviso() {
    const assunto = document.getElementById('av-assunto').value.trim();
    const msg     = document.getElementById('av-msg').value.trim();

    if (!assunto || !msg) {
        alert('Preencha o assunto e a mensagem do comunicado.');
        return;
    }

    const confirmacao = document.getElementById('msg-confirmacao');
    confirmacao.style.display = 'block';

    // Limpar campos
    document.getElementById('av-remetente').value = '';
    document.getElementById('av-assunto').value   = '';
    document.getElementById('av-msg').value       = '';

    setTimeout(() => { confirmacao.style.display = 'none'; }, 3500);
}

// =====================
// DESTACA LINK ATIVO NO NAV
// =====================

const secoes  = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('nav a');

window.addEventListener('scroll', () => {
    let atual = '';
    secoes.forEach(s => {
        if (window.scrollY >= s.offsetTop - 100) atual = s.id;
    });
    navLinks.forEach(a => {
        a.style.color = a.getAttribute('href') === '#' + atual
            ? '#f0cc72'
            : 'rgba(255,255,255,0.7)';
    });
});

// =====================
// INICIALIZAR
// =====================

renderTurmas();
renderAlunos();
