// =====================
// GESTÃO — painel, caixa de entrada e envio de mensagens
// Depende de comum.js
// =====================

// Números do painel (vêm do banco, rota /api/estatisticas)
async function carregarEstatisticas() {
    try {
        const resposta = await apiFetch(`${API_BASE}/api/estatisticas`);
        const dados = await resposta.json();
        if (!dados.sucesso) return;

        document.getElementById('stat-turmas').textContent = dados.total_turmas;
        document.getElementById('stat-alunos').textContent = dados.total_alunos;
    } catch (erro) {
        console.error('Erro ao carregar estatísticas:', erro);
    }
}

carregarEstatisticas();

// Gestor logado (salvo pelo login.js na hora do login)
function gestorLogadoId() {
    return sessionStorage.getItem('gestor_id');
}

// Mostra uma mensagem de status (verde = ok, vermelho = erro) por 3,5 s
function mostrarStatus(texto, ok) {
    const el = document.getElementById('msg-confirmacao');
    el.textContent = texto;
    el.style.color = ok ? '#16a34a' : '#dc2626';
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3500);
}

// =====================
// FORMULÁRIO: remetente e lista de destinatários
// =====================
function preencherRemetente() {
    const campo = document.getElementById('av-remetente');
    const nome = sessionStorage.getItem('gestor_nome');
    if (campo && nome) campo.value = nome;
}

async function carregarDestinatarios() {
    const select = document.getElementById('av-dest');

    try {
        const resposta = await apiFetch(`${API_BASE}/api/alunos`);
        const dados = await resposta.json();
        if (!dados.sucesso) return;

        dados.alunos.forEach(a => {
            const opcao = document.createElement('option');
            opcao.value = a.id_aluno;
            opcao.textContent = a.nome;
            select.appendChild(opcao);
        });
    } catch (erro) {
        console.error('Erro ao carregar alunos:', erro);
    }
}

// =====================
// ENVIAR MENSAGEM PRA ALUNO(S)
// =====================
async function enviarAviso() {
    const assunto = document.getElementById('av-assunto').value.trim();
    const texto   = document.getElementById('av-msg').value.trim();
    const alunoId = document.getElementById('av-dest').value; // "" = todos

    if (!gestorLogadoId()) {
        mostrarStatus('Faça login como gestão para enviar mensagens.', false);
        return;
    }

    if (!assunto || !texto) {
        mostrarStatus('Preencha o assunto e a mensagem.', false);
        return;
    }

    try {
        const resposta = await apiFetch(`${API_BASE}/api/mensagens/para-aluno`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                aluno_id: alunoId || null,
                assunto: assunto,
                texto: texto
            })
        });
        const dados = await resposta.json();

        if (!dados.sucesso) {
            mostrarStatus(dados.mensagem || 'Não foi possível enviar.', false);
            return;
        }

        document.getElementById('av-assunto').value = '';
        document.getElementById('av-msg').value     = '';
        document.getElementById('av-dest').value    = '';
        mostrarStatus('✓ ' + dados.mensagem, true);
        if (abaAtual === 'enviadas') carregarEnviadas();

    } catch (erro) {
        console.error('Erro ao enviar mensagem:', erro);
        mostrarStatus('Erro ao conectar com o servidor.', false);
    }
}

// =====================
// CAIXA DE ENTRADA
// =====================
function atualizarBadges(naoLidas) {
    ['badge-nav', 'badge-caixa'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = naoLidas > 0 ? naoLidas : '';
    });
}

async function carregarCaixaEntrada() {
    const lista = document.getElementById('caixa-lista');

    try {
        const resposta = await apiFetch(`${API_BASE}/api/mensagens/gestao`);
        const dados = await resposta.json();

        if (!dados.sucesso) {
            lista.innerHTML = '<p class="msg-vazia">Não foi possível carregar as mensagens.</p>';
            return;
        }

        if (dados.mensagens.length === 0) {
            lista.innerHTML = '<p class="msg-vazia">Nenhuma mensagem recebida ainda.</p>';
            atualizarBadges(0);
            return;
        }

        lista.innerHTML = dados.mensagens.map(m => `
            <div class="msg-item ${m.lida ? '' : 'nao-lida'}" data-id="${m.id_mensagem}" data-lida="${m.lida ? 1 : 0}" onclick="abrirMensagem(this)">
                <div class="msg-cabecalho">
                    <span class="msg-assunto">${escaparHtml(m.assunto)}</span>
                    <span class="msg-meta">${escaparHtml(m.nome_aluno)} · ${formatarDataHora(m.data_envio)}</span>
                </div>
                <p class="msg-texto">${escaparHtml(m.texto)}</p>
                <div class="msg-acoes">
                    <button class="btn-responder" data-aluno="${Number(m.id_aluno)}" data-assunto="${escaparHtml(m.assunto)}" onclick="event.stopPropagation(); responderDoBotao(this)">↩ Responder</button>
                </div>
            </div>
        `).join('');

        atualizarBadges(dados.mensagens.filter(m => !m.lida).length);

    } catch (erro) {
        console.error('Erro ao carregar mensagens:', erro);
        lista.innerHTML = '<p class="msg-vazia">Erro ao conectar com o servidor.</p>';
    }
}

// Abre/fecha a mensagem e, se ainda não foi lida, marca como lida
async function abrirMensagem(item) {
    item.classList.toggle('aberta');

    if (item.dataset.lida === '1') return;

    item.dataset.lida = '1';
    item.classList.remove('nao-lida');

    try {
        await apiFetch(`${API_BASE}/api/mensagens/${item.dataset.id}/lida`, { method: 'PATCH' });
        atualizarBadges(document.querySelectorAll('.msg-item.nao-lida').length);
    } catch (erro) {
        console.error('Erro ao marcar como lida:', erro);
    }
}

// Lê aluno/assunto dos atributos data-* do botão (texto do usuário nunca
// vai dentro de um onclick — era uma brecha de XSS)
function responderDoBotao(botao) {
    responder(botao.dataset.aluno, botao.dataset.assunto);
}

// Leva pro formulário já com o aluno e o assunto preenchidos
function responder(alunoId, assunto) {
    document.getElementById('av-dest').value = alunoId;
    document.getElementById('av-assunto').value = 'Re: ' + assunto.replace(/^Re: /, '');
    document.getElementById('avisos').scrollIntoView({ behavior: 'smooth' });
    document.getElementById('av-msg').focus();
}

// =====================
// ABAS (Recebidas / Enviadas)
// =====================
let abaAtual = 'recebidas';

function trocarAba(aba) {
    abaAtual = aba;
    document.getElementById('aba-recebidas').classList.toggle('ativa', aba === 'recebidas');
    document.getElementById('aba-enviadas').classList.toggle('ativa', aba === 'enviadas');
    if (aba === 'recebidas') carregarCaixaEntrada();
    else carregarEnviadas();
}

async function carregarEnviadas() {
    const lista = document.getElementById('caixa-lista');
    lista.innerHTML = '<p class="msg-vazia">Carregando mensagens...</p>';

    try {
        const resposta = await apiFetch(`${API_BASE}/api/mensagens/gestao/enviadas`);
        const dados = await resposta.json();

        if (!dados.sucesso) {
            lista.innerHTML = '<p class="msg-vazia">Não foi possível carregar as mensagens.</p>';
            return;
        }

        if (dados.mensagens.length === 0) {
            lista.innerHTML = '<p class="msg-vazia">Nenhuma mensagem enviada ainda.</p>';
            return;
        }

        lista.innerHTML = dados.mensagens.map(m => `
            <div class="msg-item" onclick="this.classList.toggle('aberta')">
                <div class="msg-cabecalho">
                    <span class="msg-assunto">${escaparHtml(m.assunto)}${(!m.para_todos && m.lida) ? '<span class="msg-lida-tag">✓ Lida</span>' : ''}</span>
                    <span class="msg-meta">Para: ${m.para_todos ? '📢 Todos os alunos' : escaparHtml(m.nome_aluno)} · ${formatarDataHora(m.data_envio)}</span>
                </div>
                <p class="msg-texto">${escaparHtml(m.texto)}</p>
            </div>
        `).join('');

    } catch (erro) {
        console.error('Erro ao carregar enviadas:', erro);
        lista.innerHTML = '<p class="msg-vazia">Erro ao conectar com o servidor.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    preencherRemetente();
    carregarDestinatarios();
    carregarCaixaEntrada();
});
