let tipoSelecionado = "aluno";

document.getElementById("btnAluno").onclick = function () {

    tipoSelecionado = "aluno";

    this.classList.add("ativo");

    document
        .getElementById("btnAdmin")
        .classList.remove("ativo");
};

document.getElementById("btnAdmin").onclick = function () {

    tipoSelecionado = "admin";

    this.classList.add("ativo");

    document
        .getElementById("btnAluno")
        .classList.remove("ativo");
};

function validarLogin() {

    let usuario =
        document.getElementById("usuario").value;

    let senha =
        document.getElementById("senha").value;

    /* LOGIN ADMIN */

    if (
        tipoSelecionado === "admin" &&
        usuario === "admin" &&
        senha === "1234"
    ) {

        window.location.href = "gestao.html";
    }

    /* LOGIN ALUNO */

    else if (
        tipoSelecionado === "aluno"
    ) {

        window.location.href = "home.html";
    }

    else {

        document.getElementById("mensagem").innerText =
            "Usuário ou senha inválidos!";
    }
}