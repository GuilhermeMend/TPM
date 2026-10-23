// =====================
// TURMAS (página de gestão)
// Depende de comum.js
// =====================

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

// Modal "Adicionar turma" (ainda só em memória, não grava no banco)
const turmasExemplo = [];

function abrirModalTurma() {
    ['turma-codigo','turma-nome','turma-prof'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    abrirModal('modal-turma');
}

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
    if (turmasExemplo.find(t => t.codigo === codigo)) {
        alert('Já existe uma turma com esse código.');
        return;
    }

    turmasExemplo.push({ codigo, nome, prof, turno, cor });
    fecharModal('modal-turma');
}

document.addEventListener('DOMContentLoaded', carregarTurmasBotoes);
