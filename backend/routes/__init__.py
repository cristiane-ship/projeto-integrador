from routes.auth import auth_bp
from routes.produtos import produtos_bp
from routes.carrinho import carrinho_bp
from routes.pedidos import pedidos_bp
from routes.vendedor import vendedor_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(vendedor_bp)