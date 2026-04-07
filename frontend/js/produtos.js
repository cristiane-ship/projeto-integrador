 
// Listagem de Produtos
async function carregarProdutos(filtros = {}) {
    const container = document.getElementById('products-grid');
    if (!container) return;
    
    try {
        const produtos = await API.listarProdutos(filtros);
        
        if (produtos.length === 0) {
            container.innerHTML = '<p class="loading-spinner">Nenhum produto encontrado.</p>';
            return;
        }
        
        container.innerHTML = produtos.map(produto => `
            <div class="product-card">
                <img src="${produto.imagem_url || 'assets/img/placeholder.jpg'}" 
                     alt="${produto.nome}" 
                     class="product-image"
                     onerror="this.src='assets/img/placeholder.jpg'">
                <div class="product-info">
                    <h3 class="product-title">${produto.nome}</h3>
                    <p class="product-price">${formatarMoeda(produto.preco)}</p>
                    <p class="product-vendedor" style="font-size: 0.8rem; color: var(--text-secondary);">
                        Vendido por: ${produto.vendedor_nome}
                    </p>
                    <div style="display: flex; gap: 8px; margin-top: 12px;">
                        <a href="produto.html?id=${produto.id_produto}" class="btn-secondary" style="flex: 1; text-align: center; padding: 8px;">Ver</a>
                        <button onclick="adicionarAoCarrinho(${produto.id_produto})" class="btn-primary" style="flex: 1; padding: 8px;">Comprar</button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = '<p class="loading-spinner">Erro ao carregar produtos. Tente novamente.</p>';
        console.error(error);
    }
}

async function adicionarAoCarrinho(produtoId) {
    if (!isAuthenticated()) {
        mostrarMensagem('Faça login para adicionar produtos ao carrinho', 'warning');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
        return;
    }
    
    loading(true);
    
    try {
        await API.adicionarAoCarrinho(produtoId, 1);
        mostrarMensagem('Produto adicionado ao carrinho!');
        atualizarContadorCarrinho();
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

async function carregarDetalheProduto() {
    const urlParams = new URLSearchParams(window.location.search);
    const produtoId = urlParams.get('id');
    
    if (!produtoId) {
        window.location.href = 'index.html';
        return;
    }
    
    try {
        const produto = await API.getProduto(produtoId);
        
        document.getElementById('produto-nome').textContent = produto.nome;
        document.getElementById('produto-preco').textContent = formatarMoeda(produto.preco);
        document.getElementById('produto-descricao').textContent = produto.descricao || 'Sem descrição';
        document.getElementById('produto-vendedor').textContent = produto.vendedor_nome;
        document.getElementById('produto-disponivel').textContent = `${produto.disponivel} unidades disponíveis`;
        
        const img = document.getElementById('produto-imagem');
        img.src = produto.imagem_url || 'assets/img/placeholder.jpg';
        img.onerror = () => { img.src = 'assets/img/placeholder.jpg'; };
        
        document.getElementById('btn-comprar').onclick = () => adicionarAoCarrinho(produto.id_produto);
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar produto', 'error');
    }
}

async function atualizarContadorCarrinho() {
    if (!isAuthenticated()) return;
    
    try {
        const carrinho = await API.getCarrinho();
        const totalItens = carrinho.items?.reduce((sum, item) => sum + item.quantidade, 0) || 0;
        const cartCount = document.getElementById('cart-count');
        if (cartCount) cartCount.textContent = totalItens;
    } catch (error) {
        console.error('Erro ao carregar carrinho:', error);
    }
}