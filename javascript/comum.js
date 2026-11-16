// =====================
// CÓDIGO COMPARTILHADO (turmas, fotos, home, gestão)
// =====================

// URL base do back-end Flask.
// Usa o MESMO endereço da página (localhost ou 127.0.0.1): o cookie de login
// só é guardado/enviado se site e API tiverem o mesmo nome de host.
const API_BASE = `http://${window.location.hostname || "localhost"}:5000`;

// "3_ano_B" -> "3 Ano B"
function formatarNomeTurma(turma) {
    return turma.replace(/_/g, ' ').replace(/\b\w/g, letra => letra.toUpperCase());
}

// Duas primeiras iniciais do nome, pro avatar redondo
function iniciaisDoNome(nome) {
    // escaparHtml: as iniciais vão pra dentro de innerHTML
    return escaparHtml(nome.trim().split(/\s+/).slice(0, 2).map(parte => parte[0].toUpperCase()).join(''));
}

// Modais: a classe "aberto" é o que o CSS usa pra mostrar/esconder
function abrirModal(id) {
    document.getElementById(id).classList.add('aberto');
}

function fecharModal(id) {
    document.getElementById(id).classList.remove('aberto');
}

// Fecha o modal ao clicar no fundo escurecido
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
        if (e.target === this) this.classList.remove('aberto');
    });
});

// Evita que texto digitado por alguém vire HTML na tela (ex: "<b>oi</b>")
function escaparHtml(texto) {
    return String(texto ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// "2026-10-23T14:05:00" -> "23/10/2026 14:05"
function formatarDataHora(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('pt-BR') + ' ' +
        d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

// =====================
// LOGIN / SESSÃO
// =====================

// fetch que sempre envia o cookie de sessão (credentials: 'include').
// Sem isso o navegador não manda o cookie pro Flask (outra porta) e o
// servidor acha que ninguém está logado.
function apiFetch(url, opcoes = {}) {
    return fetch(url, { credentials: 'include', ...opcoes });
}

// Botão "Sair": apaga a sessão no servidor e a cópia local, e volta pro login
async function sair() {
    try {
        await apiFetch(`${API_BASE}/logout`, { method: 'POST' });
    } catch (erro) {
        console.error('Erro ao sair:', erro);
    }
    sessionStorage.clear();
    window.location.replace('login.html');
}

// Guarda de página: quem exige login declara <body data-acesso="aluno">
// ou <body data-acesso="gestao">. A página fica escondida até o Flask
// confirmar a sessão; se não houver login do tipo certo, volta pro login.
// (A segurança de verdade está no servidor — as rotas /api checam a sessão
// por conta própria. Isto aqui só evita mostrar tela que a pessoa não pode usar.)
(function protegerPagina() {
    const tipo = document.body && document.body.dataset.acesso;
    if (!tipo) return;

    function voltarAoLogin() {
        sessionStorage.clear();
        window.location.replace('login.html');
    }

    apiFetch(`${API_BASE}/api/sessao`)
        .then(resposta => resposta.json().then(dados => ({ ok: resposta.ok, dados })))
        .then(({ ok, dados }) => {
            if (!ok || !dados.sucesso || dados.tipo !== tipo) {
                voltarAoLogin();
                return;
            }

            // Mantém o nome/id de exibição em sincronia com o servidor
            if (tipo === 'gestao') {
                sessionStorage.setItem('gestor_id', dados.id);
                sessionStorage.setItem('gestor_nome', dados.nome);
            } else {
                sessionStorage.setItem('usuario_id', dados.id);
                sessionStorage.setItem('usuario_nome', dados.nome);
            }
            document.body.style.visibility = '';
        })
        .catch(voltarAoLogin);
})();
