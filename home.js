const API_BASE = "http://localhost:5000";

document.addEventListener("DOMContentLoaded", () => {
    carregarTurmasBotoesHome();
    carregarFotosAluno();
});

async function carregarTurmasBotoesHome() {
    const container = document.getElementById('turmas-botoes');
    if (!container) return;

    try {
        const resposta = await fetch(`${API_BASE}/api/turmas`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.turmas.length === 0) {
            container.innerHTML = '<p class="turma-alunos-vazio">Nenhuma turma cadastrada.</p>';
            return;
        }

        container.innerHTML = '';
        dados.turmas.forEach(turma => {
            const btn = document.createElement('button');
            btn.className = 'btn-turma';
            btn.textContent = formatarNomeTurma(turma);
            btn.onclick = () => mostrarAlunosTurmaHome(turma, btn);
            container.appendChild(btn);
        });
    } catch (erro) {
        console.error('Erro ao carregar turmas:', erro);
        container.innerHTML = '<p class="turma-alunos-vazio">Erro ao carregar turmas.</p>';
    }
}

function formatarNomeTurma(turma) {
    return turma.replace(/_/g, ' ').replace(/\b\w/g, letra => letra.toUpperCase());
}

function iniciaisDoNome(nome) {
    return nome.trim().split(/\s+/).slice(0, 2).map(parte => parte[0].toUpperCase()).join('');
}

async function mostrarAlunosTurmaHome(turma, btn) {
    document.querySelectorAll('.btn-turma').forEach(b => b.classList.remove('ativo'));
    if (btn) btn.classList.add('ativo');

    const painel = document.getElementById('turma-alunos-painel');
    painel.innerHTML = '<p class="turma-alunos-vazio">Carregando alunos...</p>';

    try {
        const resposta = await fetch(`${API_BASE}/api/turmas/${encodeURIComponent(turma)}/alunos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.alunos.length === 0) {
            painel.innerHTML = '<p class="turma-alunos-vazio">Nenhum aluno nesta turma.</p>';
            return;
        }

        painel.innerHTML = `
            <div style="margin-bottom:12px;">
                <h3 style="margin:0; font-family:'Playfair Display', serif;">${formatarNomeTurma(turma)}</h3>
            </div>
            ${dados.alunos.map(a => `
                <div class="turma-aluno-item">
                    <div class="an-av" style="background:#3b82f6">${iniciaisDoNome(a.nome_aluno)}</div>
                    <span>${a.nome_aluno}</span>
                </div>
            `).join('')}
        `;
    } catch (erro) {
        console.error('Erro ao carregar alunos:', erro);
        painel.innerHTML = '<p class="turma-alunos-vazio">Erro ao carregar alunos.</p>';
    }
}

async function carregarFotosAluno() {
    const galeria = document.getElementById('foto-galeria');
    if (!galeria) return;

    galeria.innerHTML = '<p class="turma-alunos-vazio">Carregando galeria...</p>';

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.fotos.length === 0) {
            galeria.innerHTML = '<p class="turma-alunos-vazio">Nenhuma foto encontrada.</p>';
            return;
        }

        galeria.innerHTML = '';
        for (const f of dados.fotos) {
            const card = document.createElement('div');
            card.className = 'foto-card';
            card.innerHTML = `
                <img src="${API_BASE}${f.url}" alt="${f.legenda || 'Foto'}" loading="lazy">
                <div class="foto-card-corpo">
                    <p class="foto-card-legenda">${f.legenda || ''}</p>
                    <div class="comentarios-secao" id="comentarios-box-${f.id_foto}">
                        <p style="font-size:12px; color:#94a3b8;">Carregando comentários...</p>
                    </div>
                    <div class="comentario-input-wrap">
                        <input type="text" id="input-comentario-${f.id_foto}" placeholder="Escreva um comentário...">
                        <button onclick="enviarComentario(${f.id_foto})">Enviar</button>
                    </div>
                </div>
            `;
            galeria.appendChild(card);
            carregarComentarios(f.id_foto);
        }
    } catch (erro) {
        console.error('Erro ao carregar fotos:', erro);
        galeria.innerHTML = '<p class="turma-alunos-vazio">Erro ao carregar fotos.</p>';
    }
}

async function carregarComentarios(idFoto) {
    const box = document.getElementById(`comentarios-box-${idFoto}`);
    if (!box) return;

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos/${idFoto}/comentarios`);
        const dados = await resposta.json();

        if (!dados.sucesso || dados.comentarios.length === 0) {
            box.innerHTML = '<p style="font-size:12px; color:#94a3b8;">Nenhum comentário ainda.</p>';
            return;
        }

        box.innerHTML = dados.comentarios.map(c => `
            <div class="comentario-item">
                <strong>${c.nome_aluno}:</strong> <span>${c.texto}</span>
            </div>
        `).join('');
    } catch (erro) {
        console.error('Erro ao carregar comentários:', erro);
    }
}

async function enviarComentario(idFoto) {
    const input = document.getElementById(`input-comentario-${idFoto}`);
    const texto = input.value.trim();
    const alunoId = sessionStorage.getItem('usuario_id');

    if (!alunoId) {
        alert('Faça login como aluno para comentar.');
        return;
    }

    if (!texto) return;

    try {
        const resposta = await fetch(`${API_BASE}/api/fotos/${idFoto}/comentarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aluno_id: alunoId, texto })
        });
        const dados = await resposta.json();

        if (dados.sucesso) {
            input.value = '';
            carregarComentarios(idFoto);
        } else {
            alert(dados.mensagem || 'Erro ao publicar comentário.');
        }
    } catch (erro) {
        console.error('Erro ao enviar comentário:', erro);
    }
}