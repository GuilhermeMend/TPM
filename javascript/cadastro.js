// Cadastro de aluno — só a gestão usa esta página.
// Depende de comum.js (API_BASE).

const mensagem = document.getElementById("mensagem");

// Sem login de gestão neste navegador: volta pro login
if (!sessionStorage.getItem("gestor_id")) {
    window.location.href = "login.html";
}

// Preenche o <select> com as turmas que existem no banco
async function carregarTurmas() {
    const select = document.getElementById("turma");

    try {
        const resposta = await fetch(`${API_BASE}/api/turmas`);
        const dados = await resposta.json();

        select.innerHTML = '<option value="">Escolha a turma</option>';

        (dados.turmas || []).forEach(turma => {
            const opcao = document.createElement("option");
            opcao.value = turma;
            opcao.textContent = formatarNomeTurma(turma);
            select.appendChild(opcao);
        });

    } catch (erro) {
        console.error(erro);
        select.innerHTML = '<option value="">Erro ao carregar turmas</option>';
    }
}

carregarTurmas();

document.getElementById("btnCadastro").addEventListener("click", async function () {

    const nome = document.getElementById("nome").value.trim();
    const ra = document.getElementById("ra").value.trim();
    const turma = document.getElementById("turma").value;
    const senha = document.getElementById("senha").value;

    if (!nome || !ra || !turma || !senha) {
        mensagem.textContent = "Preencha todos os campos.";
        mensagem.style.color = "red";
        return;
    }

    try {

        const resposta = await fetch(`${API_BASE}/cadastro`, {
            method: "POST",
            credentials: "include", // envia o cookie de sessão da gestão
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, ra, turma, senha })
        });

        const dados = await resposta.json();

        if (resposta.ok) {
            mensagem.textContent = "Aluno cadastrado com sucesso!";
            mensagem.style.color = "green";

            // Limpa os campos pra cadastrar o próximo (mantém a turma)
            ["nome", "ra", "senha"].forEach(id => {
                document.getElementById(id).value = "";
            });

        } else {
            mensagem.textContent = dados.mensagem || "Erro ao cadastrar.";
            mensagem.style.color = "red";

            // Sessão expirou (ex: servidor reiniciou): volta pro login
            if (resposta.status === 401) {
                setTimeout(() => { window.location.href = "login.html"; }, 1500);
            }
        }

    } catch (erro) {
        console.error(erro);
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    }
});
