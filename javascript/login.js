// Guarda se o tipo de login escolhido é "aluno" ou "admin" (gestão).
// Começa em "aluno" porque é a opção que já vem marcada na tela.
let tipoSelecionado = "aluno";

// Clique no botão "Aluno" — troca o tipo selecionado e o estilo visual
// do botão ativo (classe "ativo")
document.getElementById("btnAluno").onclick = function () {
    tipoSelecionado = "aluno";
    this.classList.add("ativo");
    document.getElementById("btnAdmin").classList.remove("ativo");
};

// Clique no botão "Admin" — mesma lógica, só que pro lado da gestão
document.getElementById("btnAdmin").onclick = function () {
    tipoSelecionado = "admin";
    this.classList.add("ativo");
    document.getElementById("btnAluno").classList.remove("ativo");
};

// Função principal de login. É assíncrona porque precisa esperar
// a resposta do servidor Flask antes de continuar.
async function validarLogin() {
    const usuario = document.getElementById("usuario").value.trim();
    const senha = document.getElementById("senha").value;
    const msg = document.getElementById("mensagem");

    // Validação simples no próprio navegador, antes de gastar uma
    // requisição com o servidor
    if (!usuario || !senha) {
        msg.style.color = "red";
        msg.innerText = "Preencha usuário e senha!";
        return;
    }

    msg.style.color = "";
    msg.innerText = "Verificando...";

    /* LOGIN ADMIN — consulta tabela gestão no banco */
    if (tipoSelecionado === "admin") {
        try {
            // Manda usuário e senha pro Flask verificar no banco
            const resposta = await fetch("http://localhost:5000/login_gestao", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome: usuario, senha: senha })
            });

            const dados = await resposta.json();

            if (dados.sucesso) {
                // Login certo: guarda o id e o nome do gestor no
                // sessionStorage (fica disponível enquanto a aba
                // estiver aberta) e manda pra tela de gestão
                sessionStorage.setItem("gestor_id", dados.gestor_id);
                sessionStorage.setItem("gestor_nome", usuario);
                window.location.href = "gestao.html";
            } else {
                // Login errado: mostra a mensagem que o Flask mandou
                msg.style.color = "red";
                msg.innerText = dados.mensagem || "Usuário ou senha inválidos!";
            }

        } catch (erro) {
            // Cai aqui se o Flask estiver desligado, ou sem internet
            msg.style.color = "red";
            msg.innerText = "Erro ao conectar com o servidor. Verifique se o app.py está rodando.";
            console.error(erro);
        }
    }

    /* LOGIN ALUNO — consulta tabela aluno no banco */
    else if (tipoSelecionado === "aluno") {
        try {
            const resposta = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome: usuario, senha: senha })
            });

            const dados = await resposta.json();

            if (dados.sucesso) {
                sessionStorage.setItem("usuario_id", dados.usuario_id);
                sessionStorage.setItem("usuario_nome", usuario);
                window.location.href = "home.html";
            } else {
                msg.style.color = "red";
                msg.innerText = dados.mensagem || "Usuário ou senha incorretos.";
            }

        } catch (erro) {
            msg.style.color = "red";
            msg.innerText = "Erro ao conectar com o servidor. Verifique se o app.py está rodando.";
            console.error(erro);
        }
    }
}

// Permitir Enter para logar — assim o usuário não precisa clicar
// no botão, só apertar Enter depois de digitar a senha
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") validarLogin();
});
