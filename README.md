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

## Anotações de estudo
<span> uma tag usada para marcar um pequeno trecho de texto.

<section> serve para separar e organizar partes do site.
---Ela funciona como um “bloco” ou “área” da página.

<main> representa o conteúdo principal da página.
---Tudo que é mais importante do site normalmente fica dentro dele.

| Tag       | Função              |
| --------- | ------------------- |
| `<table>` | cria a tabela       |
| `<thead>` | cabeçalho da tabela |
| `<tbody>` | corpo da tabela     |
| `<tr>`    | linha               |
| `<th>`    | célula de título    |
| `<td>`    | célula normal       |

| Tag    | Função           |
| ------ | ---------------- |
| `<th>` | título da coluna |
| `<td>` | dado normal      |

<tr>
Significa:
<table row>
Ela cria uma linha da tabela.

| Parte        | Função              |
| ------------ | ------------------- |
| `<label>`    | texto do campo      |
| `for="nome"` | aponta para o input |
| `id="nome"`  | identifica o input  |
<label for="nome">Nome:</label>
<input type="text" id="nome">


<textarea>

Cria a área de texto grande.

Diferente do <input>, ela permite:

várias linhas
textos longos
comentários
mensagens


O <br> serve para quebrar linha no HTML.

No seu exemplo:

<p>Segunda a Sexta: 7h – 16h<br>Sábado: 8h – 12h</p>

o navegador mostra assim:

Segunda a Sexta: 7h – 16h
Sábado: 8h – 12h

Sem o <br> ficaria tudo na mesma linha:

Segunda a Sexta: 7h – 16h Sábado: 8h – 12h


<footer> representa o rodapé da página ou de uma seção.

Normalmente ele fica na parte de baixo do site.
O que costuma ter no <footer>?
direitos autorais
contatos
redes sociais
links
endereço
horários
informações da empresa/escola