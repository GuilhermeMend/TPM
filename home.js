// =====================
// Turmas e alunos (conectado ao banco de dados)
// =====================

// URL base do back-end Flask. Toda vez que precisamos de dado real
// (turmas, alunos de uma turma), fazemos fetch pra essa URL.
const API_BASE = "http://localhost:5000";

// async = a função pode "pausar" num await sem travar a página, até a
// resposta da requisição chegar.
async function carregarTurmas() {
    const container = document.getElementById('turmas-botoes');

    try {
        // Pede pro Flask (rota /api/turmas do app.py) a lista de turmas
        const resposta = await fetch(`${API_BASE}/api/turmas`);
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

// Deixa o nome da turma bonito pra exibir: "3_ano_B" -> "3 Ano B"
function formatarNomeTurma(turma) {
    return turma.replace(/_/g, ' ').replace(/\b\w/g, letra => letra.toUpperCase());
}

// Pega as duas primeiras iniciais do nome pro "avatar" redondo
function iniciaisDoNome(nome) {
    return nome.trim().split(/\s+/).slice(0, 2).map(parte => parte[0].toUpperCase()).join('');
}

async function mostrarAlunosTurma(turma, btn) {
    document.querySelectorAll('.btn-turma').forEach(b => b.classList.remove('ativo'));
    btn.classList.add('ativo');

    const painel = document.getElementById('turma-alunos-painel');
    painel.innerHTML = '<p class="turma-alunos-vazio">Carregando alunos...</p>';

    try {
        // encodeURIComponent evita problema se a turma tiver espaço/acento na URL
        const resposta = await fetch(`${API_BASE}/api/turmas/${encodeURIComponent(turma)}/alunos`);
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
                ${a.nome_aluno}
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar alunos da turma:', erro);
        painel.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os alunos.</p>';
    }
}

document.addEventListener('DOMContentLoaded', carregarTurmas);

// =====================
// Filtros da tabela de alunos
// =====================
function filtrar(btn) {
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('ativo'));
    btn.classList.add('ativo');
}

// =====================
// Confirmação de envio do contato
// =====================
function enviarMensagem() {
    const confirmacao = document.getElementById('msg-confirmacao');
    confirmacao.style.display = 'block';
    setTimeout(() => {
        confirmacao.style.display = 'none';
    }, 3500);
}

// =====================
// Destaca link ativo no nav ao rolar
// =====================
const secoes = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('nav a');

window.addEventListener('scroll', () => {
    let atual = '';
    secoes.forEach(s => {
        if (window.scrollY >= s.offsetTop - 100) {
            atual = s.id;
        }
    });
    navLinks.forEach(a => {
        a.style.color = a.getAttribute('href') === '#' + atual
            ? '#f0cc72'
            : 'rgba(255,255,255,0.7)';
    });
});