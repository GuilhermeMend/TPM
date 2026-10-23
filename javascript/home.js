// =====================
// HOME — contato
// =====================

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
