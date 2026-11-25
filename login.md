| Comando           | Função               |
| ----------------- | -------------------- |
| `display: flex`   | ativa Flexbox        |
| `justify-content` | mexe horizontalmente |
| `align-items`     | mexe verticalmente   |

## Fluxo de login

- Aluno  → `/login` → tabela `aluno` → `home.html`
- Gestão → `/login_gestao` → tabela `gestão` → `gestao.html`

As senhas ficam como hash no banco. Para criar o primeiro usuário da gestão:
`python Backend/criar_gestor.py`.

Abrir a tela de login (ou usar o Voltar do navegador até ela) encerra a sessão.
O login também expira sozinho após 30 minutos sem uso.
