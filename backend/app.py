from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from routes import register_routes
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS para desenvolvimento
CORS(app, origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:5000'])

# Registrar rotas da API
register_routes(app)

# Servir frontend (opcional - em produção)
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    print(f"🚀 Servidor rodando em http://localhost:{Config.PORT}")
    print(f"📁 Frontend disponível em http://localhost:{Config.PORT}")
    app.run(debug=True, port=Config.PORT)