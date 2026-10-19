// Espera o clique no botão de cadastro. É "async" porque precisa
// esperar a resposta do servidor antes de continuar.
document.getElementById("btnCadastro").addEventListener("click", async function () {


    // Pega o que o usuário digitou nos campos de nome e senha
    const nome = document.getElementById("nome").value;
    const senha = document.getElementById("senha").value;

    const mensagem = document.getElementById("mensagem");


    // Validação simples: não deixa mandar pro servidor se algum
    // campo estiver vazio
    if(nome === "" || senha === ""){

        mensagem.innerHTML = "Preencha todos os campos.";
        mensagem.style.color = "red";

        return;
    }


    try {


        // Manda nome e senha pro Flask cadastrar o aluno no banco
        const resposta = await fetch("http://localhost:5000/cadastro", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },


            body: JSON.stringify({

                nome: nome,
                senha: senha

            })

        });



        const dados = await resposta.json();



        // resposta.ok é true quando o Flask devolve um status de
        // sucesso (200, 201...). Se não for ok, caiu no "else" com erro.
        if(resposta.ok){


            mensagem.innerHTML = "Cadastro realizado com sucesso!";
            mensagem.style.color = "green";


            // Espera 1 segundo (só pra dar tempo do usuário ler a
            // mensagem) e manda pra tela de login
            setTimeout(() => {

                window.location.href = "login.html";

            }, 1000);



        } else {


            // Mostra o motivo do erro que o Flask mandou (ex: nome
            // já cadastrado)
            mensagem.innerHTML = dados.mensagem;
            mensagem.style.color = "red";


        }



    } catch(erro){


        // Cai aqui se o Flask estiver desligado ou sem internet
        console.error(erro);


        mensagem.innerHTML = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";


    }


});
