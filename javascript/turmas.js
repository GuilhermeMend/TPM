// =====================
// TURMAS E ALUNOS (página do aluno)
// Depende de comum.js
// =====================

async function carregarTurmas() {
    const container = document.getElementById('turmas-botoes');

    try {
        // Pede pro Flask (rota /api/turmas do app.py) a lista de turmas
        const resposta = await apiFetch(`${API_BASE}/api/turmas`);
        // Converte a resposta (JSON em texto) pra objeto/array do JS
        const dados = await resposta.json();

        if (!dados.sucesso || dados.turmas.length === 0) {
            container.innerHTML = '<p class="turma-alunos-vazio">Nenhuma turma cadastrada ainda.</p>';
            return;
        }

        container.innerHTML = '';
        // Cria um botão pra cada turma que veio do banco
        dados.turmas.forEach(turma => {
            const btn = document.createElement('button');
            btn.className = 'btn-turma';
            btn.textContent = formatarNomeTurma(turma);
            btn.onclick = () => mostrarAlunosTurma(turma, btn);
            container.appendChild(btn);
        });

    } catch (erro) {
        // cai aqui se o Flask estiver desligado, por exemplo
        console.error('Erro ao carregar turmas:', erro);
        container.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as turmas.</p>';
    }
}

// Mostra a lista de alunos da turma clicada. Também cuida do visual
// do botão (tira "ativo" de todos e coloca só no que foi clicado).
async function mostrarAlunosTurma(turma, btn) {
    document.querySelectorAll('.btn-turma').forEach(b => b.classList.remove('ativo'));
    btn.classList.add('ativo');

    const painel = document.getElementById('turma-alunos-painel');
    painel.innerHTML = '<p class="turma-alunos-vazio">Carregando alunos...</p>';

    try {
        // encodeURIComponent evita problema se a turma tiver espaço/acento na URL
        const resposta = await apiFetch(`${API_BASE}/api/turmas/${encodeURIComponent(turma)}/alunos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.alunos.length === 0) {
            painel.innerHTML = '<p class="turma-alunos-vazio">Nenhum aluno cadastrado nesta turma ainda.</p>';
            return;
        }

        // PÁGINA DO ALUNO: mostramos só o nome de cada colega, de propósito
        // sem o RA (a.ra_aluno existe na resposta da API, mas não usamos
        // aqui). Quem precisa ver o RA é a gestão (gestao.js).
        painel.innerHTML = dados.alunos.map(a => `
            <div class="turma-aluno-item">
                <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(a.nome_aluno)}</div>
                ${escaparHtml(a.nome_aluno)}
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar alunos da turma:', erro);
        painel.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os alunos.</p>';
    }
}

document.addEventListener('DOMContentLoaded', carregarTurmas);
