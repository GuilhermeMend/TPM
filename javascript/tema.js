// =====================
// TEMA CLARO / ESCURO
// =====================
//
// Como funciona:
// 1. Guardamos a escolha do usuário no localStorage (fica salva no
//    navegador, sobrevive a recarregar a página e a fechar o site).
// 2. Um <script> inline no <head> de cada página lê essa escolha
//    ANTES da página desenhar na tela, pra não dar aquele "flash"
//    de tela clara antes de virar escura.
// 3. Este arquivo cuida só do clique no botão e do ícone (🌙/☀️).

function alternarTema() {
    const html = document.documentElement;
    const escuroAtivo = html.getAttribute('data-tema') === 'escuro';

    if (escuroAtivo) {
        html.removeAttribute('data-tema');
        localStorage.setItem('tema', 'claro');
    } else {
        html.setAttribute('data-tema', 'escuro');
        localStorage.setItem('tema', 'escuro');
    }

    atualizarIconeTema();
}

function atualizarIconeTema() {
    const botao = document.getElementById('btn-tema');
    if (!botao) return;

    const escuroAtivo = document.documentElement.getAttribute('data-tema') === 'escuro';
    // Se já está escuro, o botão oferece voltar pro claro (mostra o sol)
    botao.textContent = escuroAtivo ? '☀️' : '🌙';
}

document.addEventListener('DOMContentLoaded', atualizarIconeTema);
