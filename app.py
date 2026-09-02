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



# ================= LISTAR TURMAS =================
#
# Rota: GET /api/turmas
# Pra que serve: devolve a lista de nomes de turma que existem de verdade
# na tabela `turmas` (ex: ["3_ano_B"]). É o que o front (home.js/gestao.js)
# usa pra criar um botão pra cada turma.
#
# DISTINCT: como cada linha da tabela `turmas` é 1 aluno, o mesmo valor de
# turma se repete várias vezes (um por aluno). DISTINCT tira as repetições
# e deixa só os nomes de turma únicos.

@app.route('/api/turmas', methods=['GET'])
def listar_turmas():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # Busca os nomes de turma distintos cadastrados na tabela turmas
        cursor.execute("SELECT DISTINCT turma FROM turmas ORDER BY turma")

        linhas = cursor.fetchall()
        # cada "linha" é um dicionário tipo {'turma': '3_ano_B'} — aqui a
        # gente pega só o valor da chave 'turma' de cada um e joga numa lista
        turmas_lista = [linha['turma'] for linha in linhas]

        return jsonify({

            "sucesso": True,

            "turmas": turmas_lista

        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao buscar turmas."

        }), 500

    finally:

        # sempre fecha cursor/conexão, mesmo se deu erro acima —
        # senão fica conexão aberta "penduradas" no banco
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()



# ================= LISTAR ALUNOS DE UMA TURMA =================
#
# Rota: GET /api/turmas/<turma>/alunos
# Exemplo real: GET /api/turmas/3_ano_B/alunos
# Pra que serve: devolve todos os alunos daquela turma específica —
# id_aluno, ra_aluno e nome_aluno. Tanto a página do aluno (home.js) quanto
# a da gestão (gestao.js) chamam essa MESMA rota; a diferença de mostrar
# ou não o RA acontece só no front, na hora de montar o HTML — o back
# manda o RA sempre, e cada página decide se usa ou ignora esse dado.
#
# <turma> na URL vira o parâmetro `turma` da função automaticamente
# (é o "conversor de rota" do Flask).

@app.route('/api/turmas/<turma>/alunos', methods=['GET'])
def listar_alunos_da_turma(turma):

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # %s é um placeholder — o mysql-connector troca ele pelo valor de
        # forma segura (evita SQL Injection). NUNCA monte a query colando
        # a variável direto na string (tipo f"... = '{turma}'").
        cursor.execute(
            """
            SELECT id_aluno, ra_aluno, nome_aluno
            FROM turmas
            WHERE turma = %s
            ORDER BY nome_aluno
            """,
            (turma,)
        )

        alunos_lista = cursor.fetchall()

        return jsonify({

            "sucesso": True,

            "alunos": alunos_lista

        }), 200

    except mysql.connector.Error as erro:

        print(f"Erro no banco: {erro}")

        return jsonify({

            "sucesso": False,

            "mensagem": "Erro ao buscar alunos da turma."

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