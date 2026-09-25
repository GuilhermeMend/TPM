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

// URL base do back-end (Flask). Toda vez que o front precisa de um dado
// que só existe no banco (turmas, alunos de uma turma...), ele faz uma
// requisição pra essa URL em vez de usar os arrays de exemplo acima.
const API_BASE = "http://localhost:5000";

// =====================
// RENDER TURMAS (botões)
// =====================

// Função "guarda-chuva": atualiza tudo que depende de turma nessa página.
// atualizarStats() e popularSelectTurma() continuam usando o array de
// exemplo `turmas` (não mexi neles). Só os botões de turma (carregarTurmasBotoes)
// é que agora vêm do banco de dados de verdade.
function renderTurmas() {
    atualizarStats();
    popularSelectTurma();
    carregarTurmasBotoes();
}

// async = essa função pode "pausar" enquanto espera algo demorado (tipo uma
// requisição de rede) sem travar o resto da página. Toda vez que tem um
// "await" dentro dela, o JS espera aquela linha terminar antes de seguir.
async function carregarTurmasBotoes() {
    const container = document.getElementById('turmas-botoes');

    try {
        // fetch() faz a requisição HTTP pro Flask (rota /api/turmas do app.py).
        // await pausa aqui até a resposta chegar.
        const resposta = await fetch(`${API_BASE}/api/turmas`);

        // .json() transforma o corpo da resposta (que vem como texto) em
        // objeto/array do JavaScript. Também é assíncrono, por isso o await.
        const dados = await resposta.json();

        // dados.sucesso vem do jsonify({"sucesso": True/False, ...}) do app.py
        if (!dados.sucesso || dados.turmas.length === 0) {
            container.innerHTML = '<p class="turma-alunos-vazio">Nenhuma turma cadastrada ainda.</p>';
            return;
        }

        container.innerHTML = '';

        // Cria um botão pra cada turma que veio do banco
        dados.turmas.forEach(turma => {
            const btn = document.createElement('button');
            btn.className = 'btn-turma-dyn';
            btn.textContent = formatarNomeTurma(turma);
            // Ao clicar, chama mostrarAlunosTurma passando o nome exato da
            // turma como está no banco (ex: "3_ano_B") — é isso que vai na
            // URL da próxima requisição.
            btn.onclick = () => mostrarAlunosTurma(turma, btn);
            container.appendChild(btn);
        });

    } catch (erro) {
        // cai aqui se o Flask estiver desligado, sem internet, etc.
        console.error('Erro ao carregar turmas:', erro);
        container.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as turmas.</p>';
    }
}

// Deixa o nome da turma bonito pra exibir: "3_ano_B" -> "3 Ano B"
function formatarNomeTurma(turma) {
    return turma.replace(/_/g, ' ').replace(/\b\w/g, letra => letra.toUpperCase());
}

// Pega as duas primeiras iniciais do nome pro "avatar" redondo
function iniciaisDoNome(nome) {
    return nome.trim().split(/\s+/).slice(0, 2).map(parte => parte[0].toUpperCase()).join('');
}

// =====================
// MOSTRAR ALUNOS DA TURMA SELECIONADA
// =====================

async function mostrarAlunosTurma(turma, btn) {
    // marca visualmente qual botão está selecionado no momento
    document.querySelectorAll('.btn-turma-dyn').forEach(b => b.classList.remove('ativo'));
    if (btn) btn.classList.add('ativo');

    const painel = document.getElementById('turma-alunos-painel');
    painel.innerHTML = '<p class="turma-alunos-vazio">Carregando alunos...</p>';

    try {
        // encodeURIComponent evita problema se o nome da turma tiver espaço,
        // acento ou caractere especial dentro da URL
        const resposta = await fetch(`${API_BASE}/api/turmas/${encodeURIComponent(turma)}/alunos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.alunos.length === 0) {
            painel.innerHTML = '<p class="turma-alunos-vazio">Nenhum aluno cadastrado nesta turma ainda.</p>';
            return;
        }

        // PÁGINA DE GESTÃO: aqui pode mostrar o RA do aluno (a.ra_aluno),
        // diferente da página do aluno (home.js), que só mostra o nome.
        painel.innerHTML = `
            <div class="turma-painel-topo">
                <h3>${formatarNomeTurma(turma)}</h3>
            </div>
            ${dados.alunos.map(a => `
                <div class="turma-aluno-item">
                    <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(a.nome_aluno)}</div>
                    <div class="turma-aluno-info">
                        <span class="turma-aluno-nome">${a.nome_aluno}</span>
                        <span class="turma-aluno-ra">RA: ${a.ra_aluno}</span>
                    </div>
                </div>
            `).join('')}
        `;

    } catch (erro) {
        console.error('Erro ao carregar alunos da turma:', erro);
        painel.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os alunos.</p>';
    }
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
// FOTOS — GALERIA (GESTÃO)
// =====================

// Pega o gestor logado (salvo pelo login.js na hora do login)
function gestorLogadoId() {
    return sessionStorage.getItem('gestor_id');
}

async function carregarFotosGestao() {
    const galeria = document.getElementById('foto-galeria');
    if (!galeria) return;

    galeria.innerHTML = '<p class="turma-alunos-vazio">Carregando fotos...</p>';

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.fotos.length === 0) {
            galeria.innerHTML = '<p class="turma-alunos-vazio">Nenhuma foto publicada ainda.</p>';
            return;
        }

        galeria.innerHTML = dados.fotos.map(f => `
            <div class="foto-card">
                <img src="${API_BASE}${f.url}" alt="${f.legenda || 'Foto do anuário'}" loading="lazy">
                <div class="foto-card-corpo">
                    <p class="foto-card-legenda">${f.legenda || '(sem legenda)'}</p>
                    <span class="foto-card-meta">${f.total_comentarios} comentário(s)</span>
                    <button class="btn-linha-excluir" onclick="confirmarExclusaoFoto(${f.id_foto})">
                        Excluir
                    </button>
                </div>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar fotos:', erro);
        galeria.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as fotos.</p>';
    }
}

async function publicarFoto() {
    const inputArquivo = document.getElementById('foto-arquivo');
    const legenda = document.getElementById('foto-legenda').value.trim();
    const msg = document.getElementById('foto-msg');

    if (!inputArquivo.files || inputArquivo.files.length === 0) {
        alert('Escolha uma imagem para publicar.');
        return;
    }

    // FormData porque estamos enviando um arquivo, não JSON puro
    const formData = new FormData();
    formData.append('imagem', inputArquivo.files[0]);
    formData.append('legenda', legenda);
    formData.append('gestor_id', gestorLogadoId());

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos`, {
            method: 'POST',
            body: formData
        });
        const dados = await resposta.json();

        if (!dados.sucesso) {
            alert(dados.mensagem || 'Não foi possível publicar a foto.');
            return;
        }

        inputArquivo.value = '';
        document.getElementById('foto-legenda').value = '';

        msg.style.color = '#16a34a';
        msg.textContent = '✓ Foto publicada com sucesso!';
        msg.style.display = 'block';
        setTimeout(() => { msg.style.display = 'none'; }, 3000);

        carregarFotosGestao();

    } catch (erro) {
        console.error('Erro ao publicar foto:', erro);
        alert('Erro ao conectar com o servidor.');
    }
}

function confirmarExclusaoFoto(idFoto) {
    document.getElementById('excluir-msg').innerHTML =
        'Tem certeza que deseja excluir esta foto?<br>Os comentários dela também serão apagados.';

    const btn = document.getElementById('btn-confirmar-exclusao');
    btn.onclick = async () => {
        try {
            const resposta = await fetch(`${API_BASE}/api/fotos/${idFoto}`, { method: 'DELETE' });
            const dados = await resposta.json();

            if (!dados.sucesso) {
                alert(dados.mensagem || 'Não foi possível excluir a foto.');
                return;
            }

            fecharModal('modal-excluir');
            carregarFotosGestao();

        } catch (erro) {
            console.error('Erro ao excluir foto:', erro);
            alert('Erro ao conectar com o servidor.');
        }
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
carregarFotosGestao();
