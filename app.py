from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector


# Criação da aplicação Flask
app = Flask(__name__)

# Permite que o JavaScript do navegador consiga acessar o Flask
CORS(app)



# ================= CONEXÃO COM O BANCO =================

def conectar_banco():

    # Função responsável por abrir conexão com o MySQL
    return mysql.connector.connect(

        # Servidor do banco de dados
        host="localhost",

        # Usuário do MySQL
        user="root",

        # Senha do MySQL
        password="lea",

        # Nome do banco utilizado
        database="banco de dados"
    )



# ================= LOGIN DO ALUNO =================

@app.route('/login', methods=['POST'])
def login():

    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json()


    # Pega o nome enviado pelo usuário
    nome_recebido = dados.get('nome')

    # Pega a senha enviada pelo usuário
    senha_recebida = dados.get('senha')


    # Variáveis para controlar conexão e consulta
    conexao = None
    cursor = None


    try:

        # Conecta ao banco de dados
        conexao = conectar_banco()


        # Cria um cursor que retorna os dados em formato de dicionário
        cursor = conexao.cursor(dictionary=True)



        # Procura um aluno com o mesmo nome e senha
        cursor.execute(
            """
            SELECT id_aluno, nome
            FROM aluno
            WHERE nome = %s AND senha = %s
            """,
            (nome_recebido, senha_recebida)
        )


        # Guarda o resultado encontrado
        usuario_encontrado = cursor.fetchone()



        # Caso o usuário exista
        if usuario_encontrado:

            return jsonify({

                "sucesso": True,

                "mensagem": f"Bem-vindo, {usuario_encontrado['nome']}!",

                # Envia o ID do aluno para o sistema
                "usuario_id": usuario_encontrado['id_aluno']

            }), 200



        # Caso nome ou senha estejam errados
        else:

            return jsonify({

                "sucesso": False,

                "mensagem": "Usuário ou senha incorretos."

            }), 401



    # Caso aconteça algum erro no MySQL
    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro interno no servidor."

        }), 500



    # Sempre executa no final, fechando a conexão
    finally:

        if cursor:
            cursor.close()

        if conexao:
            conexao.close()




# ================= CADASTRO DO ALUNO =================

@app.route('/cadastro', methods=['POST'])
def cadastro():


    # Recebe os dados enviados pelo formulário
    dados = request.get_json()


    # Separa nome e senha recebidos
    nome = dados.get('nome')
    senha = dados.get('senha')



    # Verifica se os campos foram preenchidos
    if not nome or not senha:

        return jsonify({

            "sucesso": False,

            "mensagem": "Nome e senha são obrigatórios."

        }), 400



    conexao = None
    cursor = None



    try:

        # Abre conexão com o banco
        conexao = conectar_banco()


        # Cria cursor para executar comandos SQL
        cursor = conexao.cursor()



        # Insere um novo aluno na tabela
        cursor.execute(

            """
            INSERT INTO aluno (nome, senha)
            VALUES (%s, %s)
            """,

            (nome, senha)

        )



        # Confirma a alteração no banco
        conexao.commit()



        return jsonify({

            "sucesso": True,

            "mensagem": "Cadastro realizado com sucesso!"

        }), 201



    except mysql.connector.Error as erro:


        # Mostra o erro no terminal do Flask
        print(f"Erro no banco: {erro}")


        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao cadastrar usuário."

        }), 500



    finally:


        # Fecha o cursor
        if cursor:
            cursor.close()


        # Fecha a conexão com o banco
        if conexao:
            conexao.close()




# ================= LOGIN DA GESTÃO =================

@app.route('/login_gestao', methods=['POST'])
def login_gestao():


    # Recebe os dados enviados pelo JavaScript
    dados = request.get_json()


    nome_recebido = dados.get('nome')
    senha_recebida = dados.get('senha')



    conexao = None
    cursor = None



    try:


        conexao = conectar_banco()


        cursor = conexao.cursor(dictionary=True)



        # Procura o gestor no banco
        cursor.execute(

            """
            SELECT id_gestor, nome
            FROM gestão
            WHERE nome = %s AND senha = %s
            """,

            (nome_recebido, senha_recebida)

        )



        gestor_encontrado = cursor.fetchone()



        # Caso encontre o gestor
        if gestor_encontrado:


            return jsonify({

                "sucesso": True,

                "mensagem": f"Bem-vindo, {gestor_encontrado['nome']}!",

                "gestor_id": gestor_encontrado['id_gestor']

            }), 200



        else:


            return jsonify({

                "sucesso": False,

                "mensagem": "Usuário ou senha inválidos."

            }), 401



    except mysql.connector.Error as erro:


        print(f"Erro no banco: {erro}")


        return jsonify({

            "sucesso": False,

            "mensagem": "Erro interno no servidor."

        }), 500



    finally:


        if cursor:
            cursor.close()


        if conexao:
            conexao.close()




# ================= INICIAR SERVIDOR =================

if __name__ == "__main__":

    # Inicia o servidor Flask na porta 5000
    app.run(
        host="localhost",
        port=5000,
        debug=True
    )