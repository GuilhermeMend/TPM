// Cadastro de aluno — só a gestão usa esta página.
// Depende de comum.js (API_BASE).

const mensagem = document.getElementById("mensagem");

// =====================
// SELETOR DE TURMA
// =====================
// O <select id="turma"> fica escondido e continua guardando o valor
// (o resto do código lê dele). O que aparece na tela é o menu abaixo:
// um botão + lista, no mesmo estilo dos campos do formulário.

const seletor = document.getElementById("seletor-turma");
const seletorBotao = document.getElementById("seletor-botao");
const seletorTexto = document.getElementById("seletor-texto");
const seletorLista = document.getElementById("seletor-lista");
const selectEscondido = document.getElementById("turma");

let itensSeletor = [];   // <li> de cada turma
let itemAtivo = -1;      // item destacado pelo teclado

function abrirSeletor() {
    if (itensSeletor.length === 0) return;
    seletor.classList.add("aberto");
    seletorBotao.setAttribute("aria-expanded", "true");

    // Começa destacando a turma já escolhida (ou a primeira)
    const escolhido = itensSeletor.findIndex(li => li.dataset.valor === selectEscondido.value);
    destacarItem(escolhido >= 0 ? escolhido : 0);
}

function fecharSeletor() {
    seletor.classList.remove("aberto");
    seletorBotao.setAttribute("aria-expanded", "false");
    seletorBotao.removeAttribute("aria-activedescendant");
    itemAtivo = -1;
}

function destacarItem(indice) {
    itensSeletor.forEach((li, i) => li.classList.toggle("destaque", i === indice));
    itemAtivo = indice;

    if (indice >= 0) {
        itensSeletor[indice].scrollIntoView({ block: "nearest" });
        seletorBotao.setAttribute("aria-activedescendant", itensSeletor[indice].id);
    }
}

function escolherTurma(valor) {
    selectEscondido.value = valor;

    itensSeletor.forEach(li => {
        const escolhido = li.dataset.valor === valor;
        li.classList.toggle("selecionado", escolhido);
        li.setAttribute("aria-selected", escolhido ? "true" : "false");
    });

    seletorTexto.textContent = valor ? formatarNomeTurma(valor) : "Escolha a turma";
    seletorBotao.classList.toggle("preenchido", Boolean(valor));
    seletorBotao.classList.remove("erro");
    fecharSeletor();
}

function mostrarMensagemNoSeletor(texto) {
    seletorTexto.textContent = texto;
    seletorLista.innerHTML = "";
    itensSeletor = [];
}

seletorBotao.addEventListener("click", () => {
    seletor.classList.contains("aberto") ? fecharSeletor() : abrirSeletor();
});

// Fecha ao clicar fora
document.addEventListener("click", (e) => {
    if (!seletor.contains(e.target)) fecharSeletor();
});

// Teclado: setas, Enter/Espaço, Esc, Home/End
seletorBotao.addEventListener("keydown", (e) => {
    const aberto = seletor.classList.contains("aberto");

    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!aberto) { abrirSeletor(); return; }
        const passo = e.key === "ArrowDown" ? 1 : -1;
        destacarItem((itemAtivo + passo + itensSeletor.length) % itensSeletor.length);
    } else if (e.key === "Home" && aberto) {
        e.preventDefault(); destacarItem(0);
    } else if (e.key === "End" && aberto) {
        e.preventDefault(); destacarItem(itensSeletor.length - 1);
    } else if ((e.key === "Enter" || e.key === " ") && aberto && itemAtivo >= 0) {
        e.preventDefault();
        escolherTurma(itensSeletor[itemAtivo].dataset.valor);
    } else if (e.key === "Escape" && aberto) {
        e.preventDefault(); fecharSeletor();
    } else if (e.key === "Tab") {
        fecharSeletor();
    }
});

// Preenche o menu (e o <select> escondido) com as turmas que existem no banco
async function carregarTurmas() {
    try {
        const resposta = await apiFetch(`${API_BASE}/api/turmas`);
        const dados = await resposta.json();
        const turmas = dados.turmas || [];

        selectEscondido.innerHTML = '<option value="">Escolha a turma</option>';
        seletorLista.innerHTML = "";
        itensSeletor = [];

        if (turmas.length === 0) {
            mostrarMensagemNoSeletor("Nenhuma turma cadastrada");
            return;
        }

        turmas.forEach((turma, i) => {
            const opcao = document.createElement("option");
            opcao.value = turma;
            opcao.textContent = formatarNomeTurma(turma);
            selectEscondido.appendChild(opcao);

            const li = document.createElement("li");
            li.id = `opcao-turma-${i}`;
            li.setAttribute("role", "option");
            li.setAttribute("aria-selected", "false");
            li.dataset.valor = turma;
            li.textContent = formatarNomeTurma(turma);
            li.addEventListener("click", () => escolherTurma(turma));
            li.addEventListener("mousemove", () => destacarItem(i));
            seletorLista.appendChild(li);
            itensSeletor.push(li);
        });

        escolherTurma("");
        seletorTexto.textContent = "Escolha a turma";

    } catch (erro) {
        console.error(erro);
        mostrarMensagemNoSeletor("Erro ao carregar turmas");
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
        // Marca o menu de turma em vermelho se foi ele que ficou vazio
        if (!turma) seletorBotao.classList.add("erro");
        return;
    }

    try {

        const resposta = await apiFetch(`${API_BASE}/cadastro`, {
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
