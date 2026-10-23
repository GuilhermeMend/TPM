// =====================
// GESTÃO — painel e comunicados
// =====================

// Números do painel (ainda de exemplo, não vêm do banco)
const totalTurmasExemplo = 6;
const totalAlunosExemplo = 8;

document.getElementById('stat-turmas').textContent = totalTurmasExemplo;
document.getElementById('stat-alunos').textContent = totalAlunosExemplo;

// =====================
// ENVIAR AVISO
// =====================

// Simula o envio de um comunicado: só mostra a mensagem de
// confirmação e limpa o formulário (não manda nada pro servidor —
// essa parte ainda não está conectada ao banco)
function enviarAviso() {
    const assunto = document.getElementById('av-assunto').value.trim();
    const msg     = document.getElementById('av-msg').value.trim();

    if (!assunto || !msg) {
        alert('Preencha o assunto e a mensagem do comunicado.');
        return;
    }

    const confirmacao = document.getElementById('msg-confirmacao');
    confirmacao.style.display = 'block';

    // Limpar campos
    document.getElementById('av-remetente').value = '';
    document.getElementById('av-assunto').value   = '';
    document.getElementById('av-msg').value       = '';

    setTimeout(() => { confirmacao.style.display = 'none'; }, 3500);
}
