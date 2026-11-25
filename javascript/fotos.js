// =====================
// FOTOS — GALERIA E COMENTÁRIOS (página do aluno)
// Depende de comum.js
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
        const resposta = await apiFetch(`${API_BASE}/api/fotos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.fotos.length === 0) {
            galeria.innerHTML = '<p class="turma-alunos-vazio">Nenhuma foto publicada ainda.</p>';
            return;
        }

        galeria.innerHTML = dados.fotos.map(f => `
            <div class="foto-card" data-id="${f.id_foto}" data-legenda="${escaparHtml(f.legenda || '')}" data-url="${escaparHtml(API_BASE + f.url)}" onclick="abrirFotoDoCard(this)">
                <img src="${escaparHtml(API_BASE + f.url)}" alt="${escaparHtml(f.legenda || 'Foto do anuário')}" loading="lazy">
                <div class="foto-card-corpo">
                    <span class="foto-turma-badge ${f.turma ? '' : 'geral'}">${f.turma ? escaparHtml(formatarNomeTurma(f.turma)) : 'Todas as turmas'}</span>
                    <p class="foto-card-legenda">${escaparHtml(f.legenda || '(sem legenda)')}</p>
                    <span class="foto-card-meta">💬 ${f.total_comentarios} comentário(s)</span>
                </div>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar fotos:', erro);
        galeria.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as fotos.</p>';
    }
}

// Lê os dados do card pelos atributos data-* (nada de texto do usuário
// dentro de um onclick, que era uma brecha de XSS)
function abrirFotoDoCard(card) {
    abrirFoto(Number(card.dataset.id), card.dataset.legenda, card.dataset.url);
}

// Abre o modal com a foto ampliada e já carrega os comentários dela
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
        const resposta = await apiFetch(`${API_BASE}/api/fotos/${idFoto}/comentarios`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.comentarios.length === 0) {
            lista.innerHTML = '<p class="turma-alunos-vazio">Nenhum comentário ainda. Seja o primeiro!</p>';
            return;
        }

        lista.innerHTML = dados.comentarios.map(c => `
            <div class="comentario-item">
                <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(c.nome_aluno)}</div>
                <div class="comentario-corpo">
                    <span class="comentario-nome">${escaparHtml(c.nome_aluno)}</span>
                    <p class="comentario-texto">${escaparHtml(c.texto)}</p>
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
        const resposta = await apiFetch(`${API_BASE}/api/fotos/${fotoAbertaId}/comentarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: texto })
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

document.addEventListener('DOMContentLoaded', carregarFotos);
