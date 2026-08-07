login.md:
| Comando           | Função               |
| ----------------- | -------------------- |
| `display: flex`   | ativa Flexbox        |
| `justify-content` | mexe horizontalmente |
| `align-items`     | mexe verticalmente   |

O que mudou:
login.js — removeu o hash hardcoded completamente. Agora o admin também faz fetch para o Flask, consultando o banco igual ao aluno.
app.py — adicionou a rota /login_gestao que consulta a tabela gestão com as colunas id_gestor, nome, senha.
O fluxo agora é:
Aluno → /login → tabela aluno → redireciona para home.html
Gestão → /login_gestao → tabela gestão → redireciona para gestao.html
As credenciais que vão funcionar são exatamente as do banco: nome prof / senha admin.