// =====================
// Filtros da tabela de alunos
// =====================
function filtrar(btn) {
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('ativo'));
    btn.classList.add('ativo');
}

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

// =====================
// Destaca link ativo no nav ao rolar
// =====================
const secoes = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('nav a');

window.addEventListener('scroll', () => {
    let atual = '';
    secoes.forEach(s => {
        if (window.scrollY >= s.offsetTop - 100) {
            atual = s.id;
        }
    });
    navLinks.forEach(a => {
        a.style.color = a.getAttribute('href') === '#' + atual
            ? '#f0cc72'
            : 'rgba(255,255,255,0.7)';
    });
});