// =====================
// FOTOS (página de gestão)
// Depende de comum.js
// =====================

// Pega o gestor logado (salvo pelo login.js na hora do login)
function gestorLogadoId() {
    return sessionStorage.getItem('gestor_id');
}

// Busca todas as fotos publicadas (rota GET /api/fotos do app.py) e
// desenha a galeria, com o botão de excluir em cada card
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

// Envia a imagem + legenda escolhidas no formulário pro servidor
// (rota POST /api/fotos). Usa FormData porque tem arquivo junto.
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

// Mostra a confirmação de exclusão de foto no modal genérico
// (o mesmo usado pra excluir aluno/turma) e só manda o DELETE
// pro servidor se o usuário confirmar no botão
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

document.addEventListener('DOMContentLoaded', carregarFotosGestao);
