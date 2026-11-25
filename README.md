# Nosso site ^_^ 

## Como rodar

1. `pip install -r requirements.txt`
2. Crie um arquivo `.env` na raiz com:
   ```
   SECRET_KEY=<texto longo e aleatório>
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=<senha do MySQL>
   DB_NAME=<nome do banco>
   SIGHTENGINE_USER=<chave>
   SIGHTENGINE_SECRET=<chave>
   ```
3. Rode `tcc.sql` no MySQL e depois `python Backend/criar_gestor.py` (cria o 1º usuário da gestão).
4. `python app.py` (Flask na porta 5000).
5. Abra `html/index.html` com o Live Server na porta 5501, por `http://localhost:5501`.

## Estrutura do backend

```
Backend/
  app.py          cria o Flask, configura e registra os Blueprints
  config.py       .env, pasta de uploads, chaves da Sightengine
  db.py           conectar_banco()
  seguranca.py    permissões por rota, trava de login, cache
  helpers.py      funções usadas por mais de um arquivo (negar, turma_existe...)
  moderacao.py    verificação de imagem na Sightengine
  rotas/
    auth.py       login, login_gestao, logout, sessão
    alunos.py     cadastro, editar/excluir aluno, redefinir senha
    turmas.py     turmas, alunos da turma, estatísticas
    fotos.py      fotos e comentários
    mensagens.py  mensagens aluno <-> gestão
```

Rota nova: crie a função no Blueprint certo com `@bp.route(...)` e, se precisar
de permissão, adicione o NOME DA FUNÇÃO na lista certa em `seguranca.py`
(rota que não está em nenhuma lista exige login de aluno ou gestão).
