function realizarCadastro() {

    const nome           = document.getElementById("nome").value.trim();
    const usuario        = document.getElementById("usuario").value.trim();
    const email          = document.getElementById("email").value.trim();
    const senha          = document.getElementById("senha").value;
    const confirmarSenha = document.getElementById("confirmarSenha").value;
    const msg            = document.getElementById("mensagem");

    // --- Validações ---

    if (!nome || !usuario || !email || !senha || !confirmarSenha) {
        mostrarMensagem("Preencha todos os campos!", "erro");
        return;
    }

    if (usuario.length < 3) {
        mostrarMensagem("Usuário deve ter pelo menos 3 caracteres.", "erro");
        return;
    }

    // Validação básica de e-mail
    if (!email.includes("@") || !email.includes(".")) {
        mostrarMensagem("Digite um e-mail válido.", "erro");
        return;
    }

    if (senha.length < 6) {
        mostrarMensagem("A senha deve ter pelo menos 6 caracteres.", "erro");
        return;
    }

    if (senha !== confirmarSenha) {
        mostrarMensagem("As senhas não coincidem!", "erro");
        return;
    }

    // --- Cadastro OK ---
    // Aqui você pode salvar no localStorage ou enviar para um servidor futuramente
    // Por enquanto, salva localmente e redireciona para o login

    const dados = { nome, usuario, email };
    localStorage.setItem("cadastro_" + usuario, JSON.stringify(dados));

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