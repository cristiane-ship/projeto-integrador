 
const API = {
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
            ...options.headers
        };
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${endpoint}`, config);
            
            if (response.status === 401) {
                logout();
                throw new Error('Sessão expirada. Faça login novamente.');
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error(`Erro na API (${endpoint}):`, error);
            throw error;
        }
    },
    
    // Produtos
    listarProdutos(filtros = {}) {
        const params = new URLSearchParams(filtros).toString();
        return this.request(`/produtos${params ? `?${params}` : ''}`);
    },
    
    getProduto(id) {
        return this.request(`/produtos/${id}`);
    },
    
    criarProduto(produto) {
        return this.request('/produtos', {
            method: 'POST',
            body: JSON.stringify(produto)
        });
    },
    
    atualizarProduto(id, produto) {
        return this.request(`/produtos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(produto)
        });
    },
    
    deletarProduto(id) {
        return this.request(`/produtos/${id}`, {
            method: 'DELETE'
        });
    },
    
    listarCategorias() {
        return this.request('/produtos/categorias');
    },
    
    // Carrinho
    getCarrinho() {
        return this.request('/carrinho');
    },
    
    adicionarAoCarrinho(produto_id, quantidade = 1) {
        return this.request('/carrinho/items', {
            method: 'POST',
            body: JSON.stringify({ produto_id, quantidade })
        });
    },
    
    atualizarItemCarrinho(item_id, quantidade) {
        return this.request(`/carrinho/items/${item_id}`, {
            method: 'PUT',
            body: JSON.stringify({ quantidade })
        });
    },
    
    removerItemCarrinho(item_id) {
        return this.request(`/carrinho/items/${item_id}`, {
            method: 'DELETE'
        });
    },
    
    // Pedidos
    criarPedido(pedido) {
        return this.request('/pedidos', {
            method: 'POST',
            body: JSON.stringify(pedido)
        });
    },
    
    listarPedidos() {
        return this.request('/pedidos');
    },
    
    getPedido(id) {
        return this.request(`/pedidos/${id}`);
    },
    
    // Vendedor
    getMeusProdutos() {
        return this.request('/vendedor/produtos');
    },
    // Endereços
listarEnderecos() {
    return this.request('/enderecos');
},

criarEndereco(endereco) {
    return this.request('/enderecos', {
        method: 'POST',
        body: JSON.stringify(endereco)
    });
},

atualizarEndereco(id, endereco) {
    return this.request(`/enderecos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(endereco)
    });
},

deletarEndereco(id) {
    return this.request(`/enderecos/${id}`, {
        method: 'DELETE'
    });
}
};