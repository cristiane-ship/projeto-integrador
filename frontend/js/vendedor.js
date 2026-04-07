// Painel do Vendedor

let produtoEditandoId = null;

async function carregarProdutosVendedor() {
    const container = document.getElementById('produtos-container');
    
    try {
        const produtos = await API.getMeusProdutos();
        
        if (produtos.length === 0) {
            container.innerHTML = '<p class="loading-spinner">Você ainda não cadastrou nenhum produto.</p>';
            return;
        }
        
        container.innerHTML = `
            <div class="products-grid">
                ${produtos.map(produto => `
                    <div class="product-card">
                        <img src="${produto.imagem_url || 'assets/img/placeholder.jpg'}" 
                             alt="${produto.nome}" 
                             class="product-image"
                             onerror="this.src='assets/img/placeholder.jpg'">
                        <div class="product-info">
                            <h3 class="product-title">${produto.nome}</h3>
                            <p class="product-price">${formatarMoeda(produto.preco)}</p>
                            <p style="font-size: 0.8rem;">Estoque: ${produto.quantidade || 0}</p>
                            <div style="display: flex; gap: 8px; margin-top: 12px;">
                                <button onclick="editarProduto(${produto.id_produto})" class="btn-secondary" style="flex: 1;">Editar</button>
                                <button onclick="excluirProduto(${produto.id_produto})" class="btn-danger" style="flex: 1;">Excluir</button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

function mostrarModalProduto() {
    produtoEditandoId = null;
    document.getElementById('modal-titulo').textContent = 'Novo Produto';
    document.getElementById('produto-form').reset();
    document.getElementById('modal-produto').classList.add('active');
}

function fecharModalProduto() {
    document.getElementById('modal-produto').classList.remove('active');
}

async function editarProduto(id) {
    produtoEditandoId = id;
    
    try {
        const produto = await API.getProduto(id);
        
        document.getElementById('modal-titulo').textContent = 'Editar Produto';
        document.getElementById('produto-nome').value = produto.nome;
        document.getElementById('produto-descricao').value = produto.descricao || '';
        document.getElementById('produto-preco').value = produto.preco;
        document.getElementById('produto-estoque').value = produto.disponivel || 0;
        document.getElementById('produto-categoria').value = produto.categoria || '';
        document.getElementById('produto-imagem').value = produto.imagem_url || '';
        
        document.getElementById('modal-produto').classList.add('active');
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    }
}

async function excluirProduto(id) {
    if (!confirm('Tem certeza que deseja excluir este produto?')) return;
    
    loading(true);
    
    try {
        await API.deletarProduto(id);
        mostrarMensagem('Produto excluído com sucesso');
        await carregarProdutosVendedor();
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

document.getElementById('produto-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const produto = {
        nome: document.getElementById('produto-nome').value,
        descricao: document.getElementById('produto-descricao').value,
        preco: parseFloat(document.getElementById('produto-preco').value),
        quantidade: parseInt(document.getElementById('produto-estoque').value),
        categoria: document.getElementById('produto-categoria').value,
        imagem_url: document.getElementById('produto-imagem').value
    };
    
    loading(true);
    
    try {
        if (produtoEditandoId) {
            await API.atualizarProduto(produtoEditandoId, produto);
            mostrarMensagem('Produto atualizado com sucesso');
        } else {
            await API.criarProduto(produto);
            mostrarMensagem('Produto criado com sucesso');
        }
        
        fecharModalProduto();
        await carregarProdutosVendedor();
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
});