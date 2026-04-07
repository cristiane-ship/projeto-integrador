async function carregarCarrinho() {
    const container = document.getElementById('carrinho-itens');
    if (!container) return;
    
    try {
        const carrinho = await API.getCarrinho();
        const items = carrinho.items || [];
        
        if (items.length === 0) {
            container.innerHTML = `
                <div class="carrinho-vazio">
                    <p>🛒 Seu carrinho está vazio</p>
                    <a href="index.html" class="btn-primary" style="margin-top: 16px; display: inline-block;">Continuar Comprando</a>
                </div>
            `;
            document.getElementById('subtotal').textContent = formatarMoeda(0);
            document.getElementById('total').textContent = formatarMoeda(0);
            return;
        }
        
        let subtotal = 0;
        
        container.innerHTML = items.map(item => {
            const subtotalItem = item.quantidade * item.preco;
            subtotal += subtotalItem;
            
            return `
                <div class="carrinho-item" data-item-id="${item.id_item_carrinho}">
                    <img src="${item.imagem_url || 'assets/img/placeholder.jpg'}" 
                         alt="${item.nome}" 
                         class="carrinho-item-imagem"
                         onerror="this.src='assets/img/placeholder.jpg'">
                    <div class="carrinho-item-info">
                        <h3>${item.nome}</h3>
                        <p class="carrinho-item-preco">${formatarMoeda(item.preco)}</p>
                    </div>
                    <div style="display: flex; gap: 16px; align-items: center;">
                        <div class="carrinho-item-quantidade">
                            <button onclick="atualizarQuantidade(${item.id_item_carrinho}, ${item.quantidade - 1})">-</button>
                            <span>${item.quantidade}</span>
                            <button onclick="atualizarQuantidade(${item.id_item_carrinho}, ${item.quantidade + 1})">+</button>
                        </div>
                        <button class="carrinho-item-remover" onclick="removerItem(${item.id_item_carrinho})">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('subtotal').textContent = formatarMoeda(subtotal);
        document.getElementById('total').textContent = formatarMoeda(subtotal);
        
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">Erro ao carregar carrinho: ${error.message}</div>`;
    }
}

async function atualizarQuantidade(itemId, novaQuantidade) {
    if (novaQuantidade < 1) {
        await removerItem(itemId);
        return;
    }
    
    loading(true);
    
    try {
        await API.atualizarItemCarrinho(itemId, novaQuantidade);
        await carregarCarrinho();
        await atualizarContadorCarrinho();
        mostrarMensagem('Quantidade atualizada');
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

async function removerItem(itemId) {
    loading(true);
    
    try {
        await API.removerItemCarrinho(itemId);
        await carregarCarrinho();
        await atualizarContadorCarrinho();
        mostrarMensagem('Item removido do carrinho');
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

function irParaCheckout() {
    window.location.href = 'checkout.html';
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