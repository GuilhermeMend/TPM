// =====================
// TURMAS (página de gestão)
// Depende de comum.js
//
// Aqui a gestão: vê as turmas e os alunos, adiciona turma, EDITA e
// EXCLUI turma, EDITA aluno (nome, RA, turma), REDEFINE a senha do aluno
// e EXCLUI aluno.
// =====================

let todasTurmas = [];   // códigos de todas as turmas (ex: "3_ano_B")
let turmaAberta = null; // turma cujo painel está aberto
let alunosAbertos = []; // alunos da turma aberta (vindos do servidor)

// Escolhe o <option> pelo texto/valor, sem montar HTML com dado do usuário
function preencherSelectDeTurmas(select, turmaSelecionada) {
    select.innerHTML = '';
    todasTurmas.forEach(turma => {
        const opcao = document.createElement('option');
        opcao.value = turma;
        opcao.textContent = formatarNomeTurma(turma);
        select.appendChild(opcao);
    });
    if (turmaSelecionada) select.value = turmaSelecionada;
}

// ---------------------------------------------------------------
// Botões das turmas
// ---------------------------------------------------------------
async function carregarTurmasBotoes() {
    const container = document.getElementById('turmas-botoes');

    try {
        const resposta = await apiFetch(`${API_BASE}/api/turmas`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.turmas.length === 0) {
            todasTurmas = [];
            container.innerHTML = '<p class="turma-alunos-vazio">Nenhuma turma cadastrada ainda.</p>';
            return;
        }

        todasTurmas = dados.turmas;
        container.innerHTML = '';

        dados.turmas.forEach(turma => {
            const btn = document.createElement('button');
            btn.className = 'btn-turma-dyn';
            btn.dataset.turma = turma;
            btn.textContent = formatarNomeTurma(turma);
            btn.onclick = () => mostrarAlunosTurma(turma, btn);
            container.appendChild(btn);
        });

    } catch (erro) {
        console.error('Erro ao carregar turmas:', erro);
        container.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as turmas.</p>';
    }
}

// Recarrega os botões e reabre a turma que estava aberta (se ainda existir)
async function recarregarTurmaAtual() {
    const painel = document.getElementById('turma-alunos-painel');
    const aberta = turmaAberta;

    await carregarTurmasBotoes();

    const btn = [...document.querySelectorAll('.btn-turma-dyn')]
        .find(b => b.dataset.turma === aberta);

    if (aberta && btn) {
        mostrarAlunosTurma(aberta, btn);
    } else {
        turmaAberta = null;
        alunosAbertos = [];
        painel.innerHTML = '<p class="turma-alunos-vazio">Selecione uma turma acima para ver os alunos.</p>';
    }
}

// ---------------------------------------------------------------
// Painel de alunos da turma
// ---------------------------------------------------------------
async function mostrarAlunosTurma(turma, btn) {
    document.querySelectorAll('.btn-turma-dyn').forEach(b => b.classList.remove('ativo'));
    if (btn) btn.classList.add('ativo');

    turmaAberta = turma;

    const painel = document.getElementById('turma-alunos-painel');
    painel.innerHTML = '<p class="turma-alunos-vazio">Carregando alunos...</p>';

    try {
        const resposta = await apiFetch(`${API_BASE}/api/turmas/${encodeURIComponent(turma)}/alunos`);
        const dados = await resposta.json();

        if (!dados.sucesso) {
            painel.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os alunos.</p>';
            return;
        }

        alunosAbertos = dados.alunos;

        // Responsável pela turma (vem da ficha cadastrada; turma antiga não tem)
        const ficha = dados.turma;
        const responsavel = ficha && ficha.professor
            ? `<p class="turma-responsavel">👤 Professor(a) responsável: <strong>${escaparHtml(ficha.professor)}</strong>${ficha.turno ? ' · ' + escaparHtml(ficha.turno) : ''}</p>`
            : '<p class="turma-responsavel sem-ficha">👤 Professor(a) responsável: não informado. Use "Editar turma" para preencher.</p>';

        const linhas = alunosAbertos.length === 0
            ? '<p class="turma-alunos-vazio">Nenhum aluno cadastrado nesta turma ainda.</p>'
            : alunosAbertos.map(a => `
                <div class="turma-aluno-item">
                    <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(a.nome_aluno)}</div>
                    <div class="turma-aluno-info">
                        <span class="turma-aluno-nome">${escaparHtml(a.nome_aluno)}${a.tem_login ? '' : '<span class="badge-sem-login">sem login</span>'}</span>
                        <span class="turma-aluno-ra">RA: ${escaparHtml(a.ra_aluno)}</span>
                    </div>
                    <div class="turma-aluno-acoes">
                        <button class="btn-linha-editar" data-id="${Number(a.id_aluno)}" onclick="abrirEditarAluno(Number(this.dataset.id))">Editar</button>
                        <button class="btn-linha-editar" data-id="${Number(a.id_aluno)}" onclick="abrirSenhaAluno(Number(this.dataset.id))">Senha</button>
                        <button class="btn-linha-excluir" data-id="${Number(a.id_aluno)}" onclick="confirmarExcluirAluno(Number(this.dataset.id))">Excluir</button>
                    </div>
                </div>
            `).join('');

        painel.innerHTML = `
            <div class="turma-painel-topo">
                <h3>${escaparHtml(formatarNomeTurma(turma))}</h3>
                <div class="turma-painel-acoes">
                    <button class="btn-linha-editar" onclick="abrirEditarTurma()">Editar turma</button>
                    <button class="btn-linha-excluir" onclick="confirmarExcluirTurma()">Excluir turma</button>
                </div>
            </div>
            ${responsavel}
            ${linhas}
        `;

    } catch (erro) {
        console.error('Erro ao carregar alunos da turma:', erro);
        painel.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os alunos.</p>';
    }
}

// ---------------------------------------------------------------
// Adicionar turma (já existia)
// ---------------------------------------------------------------
function abrirModalTurma() {
    ['turma-codigo','turma-nome','turma-prof'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    abrirModal('modal-turma');
}

async function adicionarTurma() {
    const codigo    = document.getElementById('turma-codigo').value.trim();
    const nome      = document.getElementById('turma-nome').value.trim();
    const professor = document.getElementById('turma-prof').value.trim();
    const turno     = document.getElementById('turma-turno').value;
    const cor       = document.getElementById('turma-cor').value;

    if (!codigo || !nome || !professor) {
        alert('Preencha código, nome e professor.');
        return;
    }

    const dados = await chamarApi('/api/turmas', 'POST', { codigo, nome, professor, turno, cor });
    if (!dados) return;

    fecharModal('modal-turma');
    recarregarTurmaAtual();
}

// ---------------------------------------------------------------
// Editar turma (nome, professor, turno, cor — o código não muda)
// ---------------------------------------------------------------
async function abrirEditarTurma() {
    if (!turmaAberta) return;

    const dados = await chamarApi(`/api/turmas/${encodeURIComponent(turmaAberta)}`, 'GET');
    if (!dados) return;

    const t = dados.turma;
    document.getElementById('turma-edit-codigo').value = t.codigo;
    document.getElementById('turma-edit-nome').value = t.nome || formatarNomeTurma(t.codigo);
    document.getElementById('turma-edit-prof').value = t.professor || '';
    if (t.turno) document.getElementById('turma-edit-turno').value = t.turno;
    if (t.cor) document.getElementById('turma-edit-cor').value = t.cor;

    abrirModal('modal-editar-turma');
}

async function salvarTurma() {
    const nome      = document.getElementById('turma-edit-nome').value.trim();
    const professor = document.getElementById('turma-edit-prof').value.trim();
    const turno     = document.getElementById('turma-edit-turno').value;
    const cor       = document.getElementById('turma-edit-cor').value;

    if (!nome || !professor) {
        alert('Preencha nome e professor.');
        return;
    }

    const dados = await chamarApi(
        `/api/turmas/${encodeURIComponent(turmaAberta)}`, 'PUT',
        { nome, professor, turno, cor }
    );
    if (!dados) return;

    fecharModal('modal-editar-turma');
    recarregarTurmaAtual();
}

// ---------------------------------------------------------------
// Confirmação de exclusão (modal único, usado por turma e aluno)
// ---------------------------------------------------------------
function pedirConfirmacao(mensagem, aoConfirmar) {
    document.getElementById('excluir-msg').textContent = mensagem;

    document.getElementById('btn-confirmar-exclusao').onclick = async () => {
        const ok = await aoConfirmar();
        if (ok) fecharModal('modal-excluir');
    };

    abrirModal('modal-excluir');
}

function confirmarExcluirTurma() {
    if (!turmaAberta) return;
    const turma = turmaAberta;

    pedirConfirmacao(
        `Excluir a turma ${formatarNomeTurma(turma)}? Só é possível se ela não tiver alunos nem fotos.`,
        async () => {
            const dados = await chamarApi(`/api/turmas/${encodeURIComponent(turma)}`, 'DELETE');
            if (!dados) return false;
            turmaAberta = null;
            recarregarTurmaAtual();
            return true;
        }
    );
}

// ---------------------------------------------------------------
// Aluno: editar / redefinir senha / excluir
// ---------------------------------------------------------------
let alunoEmEdicao = null;

function acharAluno(id) {
    return alunosAbertos.find(a => Number(a.id_aluno) === id);
}

function abrirEditarAluno(id) {
    const aluno = acharAluno(id);
    if (!aluno) return;

    alunoEmEdicao = aluno;
    document.getElementById('aluno-edit-nome').value = aluno.nome_aluno;
    document.getElementById('aluno-edit-ra').value = aluno.ra_aluno;
    preencherSelectDeTurmas(document.getElementById('aluno-edit-turma'), turmaAberta);

    abrirModal('modal-editar-aluno');
}

async function salvarAluno() {
    if (!alunoEmEdicao) return;

    const nome  = document.getElementById('aluno-edit-nome').value.trim();
    const ra    = document.getElementById('aluno-edit-ra').value.trim();
    const turma = document.getElementById('aluno-edit-turma').value;

    if (!nome || !ra || !turma) {
        alert('Preencha nome, RA e turma.');
        return;
    }

    const dados = await chamarApi(
        `/api/matriculas/${Number(alunoEmEdicao.id_aluno)}`, 'PUT', { nome, ra, turma }
    );
    if (!dados) return;

    fecharModal('modal-editar-aluno');
    recarregarTurmaAtual();
}

function abrirSenhaAluno(id) {
    const aluno = acharAluno(id);
    if (!aluno) return;

    alunoEmEdicao = aluno;
    document.getElementById('senha-aluno-nome').textContent = aluno.nome_aluno;
    document.getElementById('senha-aluno-aviso').textContent = aluno.tem_login
        ? 'O aluno passa a entrar com a nova senha na hora.'
        : 'Este aluno ainda não tem login. Ao salvar, o login é criado com o nome do aluno e a senha que você digitar.';
    document.getElementById('senha-aluno-nova').value = '';

    abrirModal('modal-senha-aluno');
}

async function salvarSenhaAluno() {
    if (!alunoEmEdicao) return;

    const senha = document.getElementById('senha-aluno-nova').value;

    if (senha.length < 4) {
        alert('A senha precisa ter pelo menos 4 caracteres.');
        return;
    }

    const dados = await chamarApi(
        `/api/matriculas/${Number(alunoEmEdicao.id_aluno)}/senha`, 'POST', { senha }
    );
    if (!dados) return;

    fecharModal('modal-senha-aluno');
    alert(dados.mensagem);
    recarregarTurmaAtual();
}

function confirmarExcluirAluno(id) {
    const aluno = acharAluno(id);
    if (!aluno) return;

    pedirConfirmacao(
        `Excluir ${aluno.nome_aluno}? O login, os comentários e as mensagens dele também serão apagados. Essa ação não pode ser desfeita.`,
        async () => {
            const dados = await chamarApi(`/api/matriculas/${Number(aluno.id_aluno)}`, 'DELETE');
            if (!dados) return false;
            recarregarTurmaAtual();
            return true;
        }
    );
}

document.addEventListener('DOMContentLoaded', carregarTurmasBotoes);
