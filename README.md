# SYP Shop - Guia de Instalação e Execução

### 📋 Pré-requisitos

- Python 3.8 ou superior
- MySQL Server 8.0 ou superior
- Pip (gerenciador de pacotes Python)

### 🚀 Instalação e Execução

### 1. Instalar dependências do Python

### Entrar na pasta do backend
cd backend

### Instalar todos os pacotes necessários
pip install Flask flask-cors PyJWT mysql-connector-python python-dotenv bcrypt

2. Configurar o banco de dados
Certifique-se que o MySQL está rodando e execute:
mysql -u root -p

Dentro do MySQL, execute os comandos SQL para criar o banco e as tabelas.

3. Configurar variáveis de ambiente
Crie o arquivo backend/.env com o seguinte conteúdo:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=syp_ecommerce
PORT=5000

4. Rodar o backend
### Dentro da pasta backend
python app.py
O servidor irá rodar em http://localhost:5000

5. Rodar o frontend
Abra o arquivo frontend/index.html no navegador ou use o Live Server do VS Code.

✅ Verificando se funcionou
Abra no navegador: http://localhost:5000/api/produtos



📦 Lista de pacotes instalados
Pacote	Versão
Flask	2.3.3
flask-cors	4.0.0
PyJWT	2.8.0
mysql-connector-python	8.1.0
python-dotenv	1.0.0
bcrypt	4.0.1

⚠️ Resolução de problemas
Erro: 'pip' não é reconhecido

python -m pip install Flask flask-cors PyJWT mysql-connector-python python-dotenv bcrypt
Erro: MySQL não conecta

Verifique se o MySQL está rodando: sudo systemctl status mysql (Linux) ou Services (Windows)

Confirme a senha no arquivo .env

Erro: porta 5000 já está em uso

Altere a porta no arquivo .env: PORT=5001

### Comando único para instalar tudo

cd backend && pip install Flask flask-cors PyJWT mysql-connector-python python-dotenv bcrypt && python app.py

