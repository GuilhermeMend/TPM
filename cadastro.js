document.getElementById("btnCadastro").addEventListener("click", async function () {


    const nome = document.getElementById("nome").value;
    const senha = document.getElementById("senha").value;

    const mensagem = document.getElementById("mensagem");


    if(nome === "" || senha === ""){

        mensagem.innerHTML = "Preencha todos os campos.";
        mensagem.style.color = "red";

        return;
    }


    try {


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



        if(resposta.ok){


            mensagem.innerHTML = "Cadastro realizado com sucesso!";
            mensagem.style.color = "green";


            setTimeout(() => {

                window.location.href = "login.html";

            }, 1000);



        } else {


            mensagem.innerHTML = dados.mensagem;
            mensagem.style.color = "red";


        }



    } catch(erro){


        console.error(erro);


        mensagem.innerHTML = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";


    }


});
