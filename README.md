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