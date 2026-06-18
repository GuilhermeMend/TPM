function realizarCadastro() {

    const nome           = document.getElementById("nome").value.trim();
    const senha          = document.getElementById("senha").value;
    const msg            = document.getElementById("mensagem");

    // --- Validações ---

    if (!nome || !senha || !confirmarSenha) {
        mostrarMensagem("Preencha todos os campos!", "erro");
        return;
    }
    if (senha.length < 6) {
        mostrarMensagem("A senha deve ter pelo menos 6 caracteres.", "erro");
        return;
    }

    // --- Cadastro OK ---
    // Aqui você pode salvar no localStorage ou enviar para um servidor futuramente
    // Por enquanto, salva localmente e redireciona para o login

    //const dados = { nome, senha, };

   // localStorage.setItem("cadastro_" + usuario, JSON.stringify(dados));

    mostrarMensagem("Cadastro realizado! Redirecionando...", "sucesso");

    // Redireciona para o login após 1.5 segundos
    setTimeout(function () {
        window.location.href = "login.html";
    }, 1500);
}

function mostrarMensagem(texto, tipo) {
    const msg = document.getElementById("mensagem");
    msg.innerText = texto;
    msg.style.color = tipo === "sucesso" ? "rgb(74, 222, 128)" : "rgb(252, 165, 165)";
}

// Permitir Enter para cadastrar
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") realizarCadastro();
});