// =====================
// CÓDIGO COMPARTILHADO (turmas, fotos, home, gestão)
// =====================

// URL base do back-end Flask
const API_BASE = "http://localhost:5000";

// "3_ano_B" -> "3 Ano B"
function formatarNomeTurma(turma) {
    return turma.replace(/_/g, ' ').replace(/\b\w/g, letra => letra.toUpperCase());
}

// Duas primeiras iniciais do nome, pro avatar redondo
function iniciaisDoNome(nome) {
    return nome.trim().split(/\s+/).slice(0, 2).map(parte => parte[0].toUpperCase()).join('');
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
