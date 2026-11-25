# TPM

Site da escola com área do aluno e área da gestão. O aluno entra com RA e senha, vê as turmas, as fotos publicadas, comenta e troca mensagens com a gestão. A gestão cadastra alunos e turmas, publica fotos e responde mensagens.

- **Frontend:** HTML, CSS e JavaScript puro (pastas `html/`, `css/`, `javascript/`)
- **Backend:** Python com Flask (`Backend/app.py`), porta 5000
- **Banco de dados:** MySQL 8+ (ou MariaDB 10.4+), definido em `tcc.sql`

## O que você precisa ter instalado

- Python 3.10 ou mais novo
- MySQL (ou MariaDB) ligado na sua máquina
- VS Code com a extensão **Live Server** (o frontend precisa rodar na porta 5501)
- Git

## Como rodar

### 1. Baixar o projeto

```bash
git clone <url-do-repositorio>
cd TPM
```

### 2. Instalar as dependências

```bash
pip install -r Backend/requirements.txt
```

### 3. Criar o arquivo `.env`

Crie um arquivo chamado `.env` na **raiz** do projeto (ou dentro de `Backend/`) com o conteúdo abaixo:

```
SECRET_KEY=<texto longo e aleatório>
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=<senha do seu MySQL>
DB_NAME=banco de dados
SIGHTENGINE_USER=<chave>
SIGHTENGINE_SECRET=<chave>
```

| Variável | Para que serve |
| --- | --- |
| `SECRET_KEY` | Assina a sessão de login. Use um texto longo e aleatório. |
| `DB_HOST`, `DB_USER`, `DB_PASSWORD` | Conexão com o MySQL. |
| `DB_NAME` | Nome do banco. O `tcc.sql` cria o banco `banco de dados`. |
| `SIGHTENGINE_USER`, `SIGHTENGINE_SECRET` | Chaves da API Sightengine, usada no envio de fotos. |

Opcionais: `FLASK_DEBUG=1` liga o modo de depuração e `SESSION_COOKIE_SECURE=1` deve ser usado só quando o site estiver em HTTPS.

> **Nunca** envie o `.env` para o Git. Ele já está no `.gitignore`.

### 4. Criar o banco de dados

Rode o `tcc.sql` inteiro no MySQL. Pelo terminal:

```bash
mysql -u root -p < tcc.sql
```

Ou, no HeidiSQL: *Arquivo > Executar arquivo SQL*. O arquivo pode ser rodado mais de uma vez sem apagar nada. Ele cria as tabelas `aluno`, `gestão`, `turmas_cadastradas`, `turmas`, `fotos`, `comentarios` e `mensagens`, com algumas turmas de exemplo. Ele **não** traz nenhum usuário nem senha.

### 5. Criar o primeiro usuário da gestão

```bash
cd Backend
python criar_gestor.py
```

O script pede o nome e a senha no terminal (mínimo de 8 caracteres). A senha é guardada como hash. Os alunos são cadastrados depois, pela própria gestão, na tela `cadastro.html`.

### 6. Ligar o servidor (Flask)

Ainda dentro de `Backend/`:

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`.

### 7. Abrir o site

Abra `html/index.html` com o **Live Server** do VS Code (clique com o botão direito no arquivo > *Open with Live Server*) e acesse:

```
http://localhost:5501
```

O backend só aceita pedidos vindos de `localhost:5501` ou `127.0.0.1:5501`. Use sempre o mesmo endereço no navegador (`localhost` ou `127.0.0.1`), senão o cookie de login não funciona.

## Como usar

| Quem | Onde entra | Depois do login vai para |
| --- | --- | --- |
| Aluno | `/login`, com **RA** e senha | `home.html` |
| Gestão | `/login_gestao`, com usuário e senha | `gestao.html` |

- A sessão expira sozinha após 30 minutos sem uso.
- Abrir a tela de login (ou voltar até ela pelo navegador) encerra a sessão.
- As fotos enviadas pela gestão ficam na pasta `Backend/uploads/`, **só na máquina do servidor** (não vão para o Git).

## Estrutura do projeto

```
TPM/
├── Backend/
│   ├── app.py               # servidor Flask: login, turmas, fotos, comentários, mensagens
│   ├── criar_gestor.py      # cria ou troca a senha de um usuário da gestão
│   ├── atualizar_banco.py   # atualiza um banco ANTIGO para a estrutura nova
│   ├── migrar_senhas.py     # converte senhas em texto puro para hash (migração única)
│   ├── requirements.txt     # dependências Python
│   └── uploads/             # fotos enviadas (não versionadas)
├── html/                    # páginas (login, home, turmas, fotos, gestão, cadastro)
├── css/                     # estilos
├── javascript/              # scripts de cada página
├── uploads/                 # pasta de fotos (só o .gitkeep é versionado)
├── tcc.sql                  # estrutura do banco de dados
├── changelog.md             # histórico de mudanças
└── login.md                 # anotações sobre o fluxo de login
```

## Já tinha um banco criado antes?

Se você criou o banco com uma versão antiga do `tcc.sql`, não precisa apagar nada. Dentro de `Backend/`, com o MySQL ligado:

```bash
python atualizar_banco.py
```

Se as senhas ainda estiverem em texto puro, rode também (uma vez só):

```bash
python migrar_senhas.py
```

Os dois scripts são seguros para rodar mais de uma vez.

## Problemas comuns

| Problema | O que fazer |
| --- | --- |
| Erro de conexão com o banco | Confira se o MySQL está ligado e se `DB_USER`, `DB_PASSWORD` e `DB_NAME` do `.env` estão certos. |
| O site abre mas o login não funciona | Confirme que o Flask está rodando na porta 5000 e que o site foi aberto em `localhost:5501` (ou `127.0.0.1:5501`). |
| Sessão cai o tempo todo | Use sempre o mesmo endereço (`localhost` ou `127.0.0.1`) do início ao fim. |
| `ModuleNotFoundError` | Rode `pip install -r Backend/requirements.txt` de novo. |
| Aluno não consegue entrar | O login é por **RA**. Confirme que o aluno foi cadastrado pela gestão e que o RA está certo. |

## Segurança: o que nunca vai para o Git

- `.env` (chaves e senha do banco)
- `uploads/` e `Backend/uploads/` (fotos dos alunos)
- `__pycache__/` e `.vscode/`
- dumps do banco (`*.dump.sql`, `backup*.sql`)

Se algum desses já foi enviado por engano, veja o `.gitignore` e use `git rm -r --cached <pasta>` antes de fazer o commit.
