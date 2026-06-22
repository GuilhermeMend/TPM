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

// Hash SHA-256 das credenciais do admin — a senha real nunca fica exposta aqui
const HASH_ADMIN = "151396b07d99d5f4a1a54a72728ff751a2c127e87dc6317547e7a4f221c5dfc8";

async function hashSenha(usuario, senha) {
    const texto = usuario + senha;
    const buffer = await crypto.subtle.digest(
        "SHA-256",
        new TextEncoder().encode(texto)
    );
    return Array.from(new Uint8Array(buffer))
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
}

async function validarLogin() {

    const usuario = document.getElementById("usuario").value.trim();
    const senha = document.getElementById("senha").value;
    const msg = document.getElementById("mensagem");

    if (!usuario || !senha) {
        msg.innerText = "Preencha usuário e senha!";
        return;
    }

    /* LOGIN ADMIN */
    if (tipoSelecionado === "admin") {
        const hash = await hashSenha(usuario, senha);
        if (hash === HASH_ADMIN) {
            window.location.href = "gestao.html";
        } else {
            msg.innerText = "Usuário ou senha inválidos!";
        }
    }

    /* LOGIN ALUNO — verifica no banco de dados */
    else if (tipoSelecionado === "aluno") {
        msg.style.color = "";
        msg.innerText = "Verificando...";

        try {
            const resposta = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome: usuario, senha: senha })
            });

            const dados = await resposta.json();

            if (dados.sucesso) {
                // Salva o id do aluno para usar nas outras páginas
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