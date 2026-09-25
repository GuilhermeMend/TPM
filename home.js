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
document.addEventListener('DOMContentLoaded', carregarFotos);

// =====================
// FOTOS — GALERIA E COMENTÁRIOS (ALUNO)
// =====================

// Guarda qual foto está aberta no modal no momento, pra saber onde
// publicar o comentário quando o aluno clicar em "Comentar"
let fotoAbertaId = null;

// Pega o aluno logado (salvo pelo login.js na hora do login)
function alunoLogadoId() {
    return sessionStorage.getItem('usuario_id');
}

async function carregarFotos() {
    const galeria = document.getElementById('foto-galeria');
    if (!galeria) return;

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.fotos.length === 0) {
            galeria.innerHTML = '<p class="turma-alunos-vazio">Nenhuma foto publicada ainda.</p>';
            return;
        }

        galeria.innerHTML = dados.fotos.map(f => `
            <div class="foto-card" onclick="abrirFoto(${f.id_foto}, '${(f.legenda || '').replace(/'/g, "\\'")}', '${API_BASE}${f.url}')">
                <img src="${API_BASE}${f.url}" alt="${f.legenda || 'Foto do anuário'}" loading="lazy">
                <div class="foto-card-corpo">
                    <p class="foto-card-legenda">${f.legenda || '(sem legenda)'}</p>
                    <span class="foto-card-meta">💬 ${f.total_comentarios} comentário(s)</span>
                </div>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar fotos:', erro);
        galeria.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as fotos.</p>';
    }
}

function abrirFoto(idFoto, legenda, url) {
    fotoAbertaId = idFoto;
    document.getElementById('foto-modal-legenda').textContent = legenda || 'Foto';
    document.getElementById('foto-modal-img').src = url;
    document.getElementById('comentario-texto').value = '';
    carregarComentarios(idFoto);
    abrirModal('modal-foto');
}

async function carregarComentarios(idFoto) {
    const lista = document.getElementById('comentarios-lista');
    lista.innerHTML = '<p class="turma-alunos-vazio">Carregando comentários...</p>';

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos/${idFoto}/comentarios`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.comentarios.length === 0) {
            lista.innerHTML = '<p class="turma-alunos-vazio">Nenhum comentário ainda. Seja o primeiro!</p>';
            return;
        }

        lista.innerHTML = dados.comentarios.map(c => `
            <div class="comentario-item">
                <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(c.nome_aluno)}</div>
                <div class="comentario-corpo">
                    <span class="comentario-nome">${c.nome_aluno}</span>
                    <p class="comentario-texto">${c.texto}</p>
                </div>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar comentários:', erro);
        lista.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os comentários.</p>';
    }
}

async function enviarComentario() {
    const campo = document.getElementById('comentario-texto');
    const texto = campo.value.trim();

    if (!fotoAbertaId) return;

    if (!alunoLogadoId()) {
        alert('Faça login como aluno para comentar.');
        return;
    }

    if (!texto) {
        alert('Escreva um comentário antes de enviar.');
        return;
    }

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos/${fotoAbertaId}/comentarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aluno_id: alunoLogadoId(), texto: texto })
        });
        const dados = await resposta.json();

        if (!dados.sucesso) {
            alert(dados.mensagem || 'Não foi possível publicar o comentário.');
            return;
        }

        campo.value = '';
        carregarComentarios(fotoAbertaId);
        carregarFotos(); // atualiza o contador de comentários no card

    } catch (erro) {
        console.error('Erro ao enviar comentário:', erro);
        alert('Erro ao conectar com o servidor.');
    }
}

// =====================
// MODAIS (usado pela foto + comentários)
// =====================

function abrirModal(id) {
    document.getElementById(id).classList.add('aberto');
}

function fecharModal(id) {
    document.getElementById(id).classList.remove('aberto');
}

document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
        if (e.target === this) this.classList.remove('aberto');
    });
});

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