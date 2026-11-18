# Changelog

#18/11/2026

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