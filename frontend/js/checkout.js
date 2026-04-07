
async function carregarResumoPedido() {
    const container = document.getElementById('resumo-pedido');
    
    try {
        const carrinho = await API.getCarrinho();
        const items = carrinho.items || [];
        let subtotal = 0;
        
        items.forEach(item => {
            subtotal += item.quantidade * item.preco;
        });
        
        container.innerHTML = `
            <div class="resumo-linha">
                <span>Subtotal:</span>
                <span>${formatarMoeda(subtotal)}</span>
            </div>
            <div class="resumo-linha">
                <span>Frete:</span>
                <span>A calcular</span>
            </div>
            <div class="resumo-linha total">
                <span>Total:</span>
                <span>${formatarMoeda(subtotal)}</span>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

async function carregarEnderecos() {
    // Por enquanto, simular endereço padrão
    const container = document.getElementById('enderecos-container');
    
    container.innerHTML = `
        <div class="endereco-card" style="border: 2px solid var(--primary); padding: var(--spacing-md); border-radius: var(--radius-md); margin-bottom: var(--spacing-md);">
            <input type="radio" name="endereco" value="1" checked>
            <label>Endereço Principal - Rua Exemplo, 123 - Centro - São Paulo/SP - CEP: 00000-000</label>
        </div>
    `;
}

function mostrarModalEndereco() {
    const modal = document.getElementById('modal-endereco');
    modal.classList.add('active');
}

function fecharModalEndereco() {
    const modal = document.getElementById('modal-endereco');
    modal.classList.remove('active');
}

async function finalizarPedido() {
    loading(true);
    
    try {
        // Simular pedido (endereço fixo por enquanto)
        const pedido = {
            endereco_id: 1,
            transportadora_id: 1,
            valor_frete: 0
        };
        
        const result = await API.criarPedido(pedido);
        
        mostrarMensagem('Pedido realizado com sucesso!');
        
        setTimeout(() => {
            window.location.href = `pedido-confirmado.html?id=${result.pedido_id}`;
        }, 1500);
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}