function validarLogin() {

    let usuario = document.getElementById("usuario").value;
    let senha = document.getElementById("senha").value;

    if (usuario === "admin" && senha === "1234") {

        window.location.href = "home.html";

    } else {

        document.getElementById("mensagem").innerText =
            "Usuário ou senha inválidos !";
    }
}