// =====================
// HOME — caixa de entrada e contato com a gestão
// Depende de comum.js
// =====================

// Aluno logado (salvo pelo login.js na hora do login)
function alunoLogadoId() {
    return sessionStorage.getItem('usuario_id');
}

// Preenche o nome no formulário de contato
function preencherNomeContato() {
    const campo = document.getElementById('ct-nome');
    const nome = sessionStorage.getItem('usuario_nome');
    if (campo && nome) campo.value = nome;
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
// ENVIAR MENSAGEM PRA GESTÃO
// =====================
async function enviarMensagem() {
    const assunto = document.getElementById('ct-assunto').value;
    const texto = document.getElementById('ct-texto').value.trim();

    if (!alunoLogadoId()) {
        mostrarStatus('Faça login como aluno para enviar mensagens.', false);
        return;
    }

    if (!assunto || !texto) {
        mostrarStatus('Escolha um assunto e escreva a mensagem.', false);
        return;
    }

    try {
        const resposta = await fetch(`${API_BASE}/api/mensagens/para-gestao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aluno_id: alunoLogadoId(), assunto: assunto, texto: texto })
        });
        const dados = await resposta.json();

        if (!dados.sucesso) {
            mostrarStatus(dados.mensagem || 'Não foi possível enviar.', false);
            return;
        }

        document.getElementById('ct-assunto').value = '';
        document.getElementById('ct-texto').value = '';
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
    if (!lista) return;

    if (!alunoLogadoId()) {
        lista.innerHTML = '<p class="msg-vazia">Faça login como aluno para ver suas mensagens.</p>';
        return;
    }

    try {
        const resposta = await fetch(`${API_BASE}/api/mensagens/aluno/${alunoLogadoId()}`);
        const dados = await resposta.json();

        if (!dados.sucesso) {
            lista.innerHTML = '<p class="msg-vazia">Não foi possível carregar as mensagens.</p>';
            return;
        }

        if (dados.mensagens.length === 0) {
            lista.innerHTML = '<p class="msg-vazia">Nenhuma mensagem por enquanto.</p>';
            atualizarBadges(0);
            return;
        }

        lista.innerHTML = dados.mensagens.map(m => `
            <div class="msg-item ${m.lida ? '' : 'nao-lida'}" data-id="${m.id_mensagem}" data-lida="${m.lida ? 1 : 0}" onclick="abrirMensagem(this)">
                <div class="msg-cabecalho">
                    <span class="msg-assunto">${escaparHtml(m.assunto)}${m.para_todos ? ' · 📢 Aviso geral' : ''}</span>
                    <span class="msg-meta">${escaparHtml(m.nome_gestor || 'Gestão')} · ${formatarDataHora(m.data_envio)}</span>
                </div>
                <p class="msg-texto">${escaparHtml(m.texto)}</p>
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
        await fetch(`${API_BASE}/api/mensagens/${item.dataset.id}/lida`, { method: 'PATCH' });
        atualizarBadges(document.querySelectorAll('.msg-item.nao-lida').length);
    } catch (erro) {
        console.error('Erro ao marcar como lida:', erro);
    }
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

    if (!alunoLogadoId()) {
        lista.innerHTML = '<p class="msg-vazia">Faça login como aluno para ver suas mensagens.</p>';
        return;
    }

    lista.innerHTML = '<p class="msg-vazia">Carregando mensagens...</p>';

    try {
        const resposta = await fetch(`${API_BASE}/api/mensagens/aluno/${alunoLogadoId()}/enviadas`);
        const dados = await resposta.json();

        if (!dados.sucesso) {
            lista.innerHTML = '<p class="msg-vazia">Não foi possível carregar as mensagens.</p>';
            return;
        }

        if (dados.mensagens.length === 0) {
            lista.innerHTML = '<p class="msg-vazia">Você ainda não enviou mensagens.</p>';
            return;
        }

        lista.innerHTML = dados.mensagens.map(m => `
            <div class="msg-item" onclick="this.classList.toggle('aberta')">
                <div class="msg-cabecalho">
                    <span class="msg-assunto">${escaparHtml(m.assunto)}${m.lida ? '<span class="msg-lida-tag">✓ Lida pela gestão</span>' : ''}</span>
                    <span class="msg-meta">Para: Gestão · ${formatarDataHora(m.data_envio)}</span>
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
    preencherNomeContato();
    carregarCaixaEntrada();
});
