# Changelog

# 18/11/2026

### Alterado
- Login do aluno agora é feito com "RA" e "Senha"(antes era nome e senha).
    -Backend/app.py: a rota '/login' recebe 'ra' e busca o aluno em 'turmas.ra_aluno', ligado ao login pela coluna 'id_login'. A resposta passa a incluir o 'nome do aluno.
    -Javascript/login.js: envia {ra, senha}, pega o nome exibido na home a partir da resposta do servidor e troca o placeholder do campo ao alternar entre Aluno e Gestão
    -Html/login.html: o campo vem com o placeholder "Digite seu RA".
- A mensagem de erro do login do aluno agora é "RA ou senha incorretos."
- README.md e login.md: fluxo de login atualizado.

### Observações
- O login da gestão continua por usuário e senha.
- Não precisa alterar o banco de dados (tcc.sql).
- Alunos sem login (como os de exemplo do tcc.sql).

# Changelog

# 19/11/2026

### Alterado
- Gitignore: adicionado um principal que está por fora do Backend.
    - Gitignore da raiz: bloquea .env, uploads, __pycache__ e dumps do banco.

# Changelog

# 25/11/2026

### Alterado
- Backend/app.py dividido em Blueprints (de 2.310 para 61 linhas). Ele agora só cria o Flask, configura e registra os Blueprints.
    - Backend/rotas/auth.py: /login, /login_gestao, /logout e /api/sessao.
    - Backend/rotas/alunos.py: /cadastro, editar/excluir aluno e redefinir senha (/api/matriculas/...).
    - Backend/rotas/turmas.py: /api/turmas, alunos da turma e /api/estatisticas.
    - Backend/rotas/fotos.py: /uploads, /api/fotos e comentários.
    - Backend/rotas/mensagens.py: /api/mensagens/... e /api/alunos.
    - Backend/config.py, db.py, seguranca.py, helpers.py e moderacao.py: o que não é rota (configurações do .env, conexão com o MySQL, permissões e trava de login, funções compartilhadas e Sightengine).
- Os arquivos continuam conectados: o app.py registra todos os Blueprints e a trava de login/permissões (seguranca.py) vale para todas as rotas, como antes.
- README.md: adicionada a estrutura do backend.

### Observações
- Nenhuma URL mudou, então o front (HTML/JS) não precisa de alteração.
- Não precisa alterar o banco de dados (tcc.sql).
- Rota nova: criar no Blueprint certo com @bp.route e, se precisar de permissão, colocar o nome da função na lista certa em seguranca.py.
