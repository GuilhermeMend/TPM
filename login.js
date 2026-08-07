let tipoSelecionado = "aluno";

document.getElementById("btnAluno").onclick = function () {
    tipoSelecionado = "aluno";
    this.classList.add("ativo");
    document.getElementById("btnAdmin").classList.remove("ativo");
};

document.getElementById("btnAdmin").onclick = function () {
    tipoSelecionado = "admin";
    this.classList.add("ativo");
    document.getElementById("btnAluno").classList.remove("ativo");
};

async function validarLogin() {
    const usuario = document.getElementById("usuario").value.trim();
    const senha = document.getElementById("senha").value;
    const msg = document.getElementById("mensagem");

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
            const resposta = await fetch("http://localhost:5000/login_gestao", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome: usuario, senha: senha })
            });

            const dados = await resposta.json();

            if (dados.sucesso) {
                sessionStorage.setItem("gestor_id", dados.gestor_id);
                sessionStorage.setItem("gestor_nome", usuario);
                window.location.href = "gestao.html";
            } else {
                msg.style.color = "red";
                msg.innerText = dados.mensagem || "Usuário ou senha inválidos!";
            }

        } catch (erro) {
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

// Permitir Enter para logar
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") validarLogin();
});