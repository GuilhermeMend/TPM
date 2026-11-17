// =====================
// FOTOS (página de gestão)
// Depende de comum.js
//
// A gestão publica fotos para TODAS as turmas ou só para uma turma,
// filtra a galeria por turma, exclui fotos e apaga comentários impróprios.
// =====================

// Preenche os dois <select> de turma (o do formulário e o do filtro)
async function carregarTurmasDasFotos() {
    try {
        const resposta = await apiFetch(`${API_BASE}/api/turmas`);
        const dados = await resposta.json();
        if (!dados.sucesso) return;

        ['foto-turma', 'filtro-turma'].forEach(id => {
            const select = document.getElementById(id);
            if (!select) return;

            dados.turmas.forEach(turma => {
                const opcao = document.createElement('option');
                opcao.value = turma;
                opcao.textContent = formatarNomeTurma(turma);
                select.appendChild(opcao);
            });
        });

    } catch (erro) {
        console.error('Erro ao carregar turmas:', erro);
    }
}

// Busca as fotos (rota GET /api/fotos do app.py, com ?turma= se houver filtro)
// e desenha a galeria, com os botões de comentários e de excluir em cada card
async function carregarFotosGestao() {
    const galeria = document.getElementById('foto-galeria');
    if (!galeria) return;

    const filtro = document.getElementById('filtro-turma');
    const turma = filtro ? filtro.value : '';
    const consulta = turma ? `?turma=${encodeURIComponent(turma)}` : '';

    galeria.innerHTML = '<p class="turma-alunos-vazio">Carregando fotos...</p>';

    try {
        const resposta = await apiFetch(`${API_BASE}/api/fotos${consulta}`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.fotos.length === 0) {
            galeria.innerHTML = '<p class="turma-alunos-vazio">Nenhuma foto publicada ainda.</p>';
            return;
        }

        galeria.innerHTML = dados.fotos.map(f => `
            <div class="foto-card">
                <img src="${escaparHtml(API_BASE + f.url)}" alt="${escaparHtml(f.legenda || 'Foto do anuário')}" loading="lazy">
                <div class="foto-card-corpo">
                    <span class="foto-turma-badge ${f.turma ? '' : 'geral'}">${f.turma ? escaparHtml(formatarNomeTurma(f.turma)) : 'Todas as turmas'}</span>
                    <p class="foto-card-legenda">${escaparHtml(f.legenda || '(sem legenda)')}</p>
                    <span class="foto-card-meta">${Number(f.total_comentarios)} comentário(s)</span>
                    <div class="foto-card-acoes">
                        <button class="btn-linha-editar" data-id="${Number(f.id_foto)}" data-legenda="${escaparHtml(f.legenda || '')}" onclick="abrirComentariosGestao(this)">
                            Comentários
                        </button>
                        <button class="btn-linha-excluir" data-id="${Number(f.id_foto)}" onclick="confirmarExclusaoFoto(Number(this.dataset.id))">
                            Excluir
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar fotos:', erro);
        galeria.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar as fotos.</p>';
    }
}

// Envia a imagem + legenda + turma escolhidas no formulário pro servidor
// (rota POST /api/fotos). Usa FormData porque tem arquivo junto.
async function publicarFoto() {
    const inputArquivo = document.getElementById('foto-arquivo');
    const legenda = document.getElementById('foto-legenda').value.trim();
    const turma = document.getElementById('foto-turma').value; // vazio = todas
    const msg = document.getElementById('foto-msg');

    if (!inputArquivo.files || inputArquivo.files.length === 0) {
        alert('Escolha uma imagem para publicar.');
        return;
    }

    const formData = new FormData();
    formData.append('imagem', inputArquivo.files[0]);
    formData.append('legenda', legenda);
    formData.append('turma', turma);

    try {
        const resposta = await apiFetch(`${API_BASE}/api/fotos`, {
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

// Mostra a confirmação de exclusão de foto no modal genérico
// e só manda o DELETE pro servidor se o usuário confirmar no botão
function confirmarExclusaoFoto(idFoto) {
    document.getElementById('excluir-msg').innerHTML =
        'Tem certeza que deseja excluir esta foto?<br>Os comentários dela também serão apagados.';

    const btn = document.getElementById('btn-confirmar-exclusao');
    btn.onclick = async () => {
        const dados = await chamarApi(`/api/fotos/${idFoto}`, 'DELETE');
        if (!dados) return;

        fecharModal('modal-excluir');
        carregarFotosGestao();
    };

    abrirModal('modal-excluir');
}

// ---------------------------------------------------------------
// Comentários da foto: a gestão lê e apaga os que forem impróprios
// ---------------------------------------------------------------
let fotoComentariosId = null;

function abrirComentariosGestao(botao) {
    fotoComentariosId = Number(botao.dataset.id);
    document.getElementById('comentarios-titulo').textContent =
        'Comentários — ' + (botao.dataset.legenda || 'foto');

    carregarComentariosGestao();
    abrirModal('modal-comentarios');
}

async function carregarComentariosGestao() {
    const lista = document.getElementById('gestao-comentarios-lista');
    lista.innerHTML = '<p class="turma-alunos-vazio">Carregando comentários...</p>';

    try {
        const resposta = await apiFetch(`${API_BASE}/api/fotos/${fotoComentariosId}/comentarios`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.comentarios.length === 0) {
            lista.innerHTML = '<p class="turma-alunos-vazio">Nenhum comentário nesta foto.</p>';
            return;
        }

        lista.innerHTML = dados.comentarios.map(c => `
            <div class="gestao-comentario">
                <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(c.nome_aluno)}</div>
                <div class="gestao-comentario-corpo">
                    <span class="gestao-comentario-nome">${escaparHtml(c.nome_aluno)}<span class="gestao-comentario-data">${escaparHtml(formatarDataHora(c.data_comentario))}</span></span>
                    <p class="gestao-comentario-texto">${escaparHtml(c.texto)}</p>
                </div>
                <button class="btn-linha-excluir" data-id="${Number(c.id_comentario)}" onclick="apagarComentario(Number(this.dataset.id))">
                    Apagar
                </button>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar comentários:', erro);
        lista.innerHTML = '<p class="turma-alunos-vazio">Não foi possível carregar os comentários.</p>';
    }
}

async function apagarComentario(idComentario) {
    if (!confirm('Apagar este comentário?')) return;

    const dados = await chamarApi(`/api/comentarios/${idComentario}`, 'DELETE');
    if (!dados) return;

    carregarComentariosGestao();
    carregarFotosGestao(); // atualiza o contador no card
}

document.addEventListener('DOMContentLoaded', () => {
    carregarTurmasDasFotos();
    carregarFotosGestao();
});
