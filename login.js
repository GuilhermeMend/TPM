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
    const senha   = document.getElementById("senha").value;
    const msg     = document.getElementById("mensagem");

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

    /* LOGIN ALUNO */
    else if (tipoSelecionado === "aluno") {
        // Aluno também precisa preencher os campos (validação básica)
        // Aqui você pode adicionar lista de alunos válidos futuramente
        window.location.href = "home.html";
    }
}

// Permitir Enter para logar
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") validarLogin();
});
