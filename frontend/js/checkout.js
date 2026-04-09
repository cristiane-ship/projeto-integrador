// Checkout - Finalização de compra

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
            <div class="resumo-linha" style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>Subtotal:</span>
                <span>${formatarMoeda(subtotal)}</span>
            </div>
            <div class="resumo-linha" style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>Frete:</span>
                <span>A calcular</span>
            </div>
            <div class="resumo-linha total" style="display: flex; justify-content: space-between; padding: 12px 0; font-size: 1.2rem; font-weight: bold; color: var(--primary); border-top: 2px solid var(--border); margin-top: 8px;">
                <span>Total:</span>
                <span>${formatarMoeda(subtotal)}</span>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

async function carregarEnderecosCheckout() {
    const container = document.getElementById('enderecos-container');
    
    try {
        const enderecos = await API.listarEnderecos();
        
        if (!enderecos || enderecos.length === 0) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <p>Você não tem endereços cadastrados.</p>
                    <a href="perfil.html" class="btn-primary" style="margin-top: 8px; display: inline-block;">Cadastrar Endereço</a>
                </div>
            `;
            return;
        }
        
        // Criar radio buttons para cada endereço
        container.innerHTML = enderecos.map(end => `
            <div class="endereco-opcao" style="border: 2px solid ${enderecoSelecionado === end.id_endereco ? 'var(--primary)' : 'var(--border)'}; 
                        border-radius: var(--radius-md); padding: var(--spacing-md); margin-bottom: var(--spacing-md); cursor: pointer;"
                 onclick="selecionarEndereco(${end.id_endereco})">
                <div style="display: flex; align-items: start; gap: 12px;">
                    <input type="radio" name="endereco" value="${end.id_endereco}" 
                           ${enderecoSelecionado === end.id_endereco ? 'checked' : ''} 
                           onchange="selecionarEndereco(${end.id_endereco})">
                    <div style="flex: 1;">
                        <p><strong>${end.logradouro}, ${end.numero}</strong> ${end.complemento ? `- ${end.complemento}` : ''}</p>
                        <p>${end.bairro} - ${end.cidade}/${end.estado}</p>
                        <p>CEP: ${end.cep}</p>
                        ${end.principal ? '<span class="badge-stock" style="font-size: 0.7rem;">Principal</span>' : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
        // Selecionar o primeiro endereço ou o principal automaticamente
        const enderecoPrincipal = enderecos.find(e => e.principal) || enderecos[0];
        if (!enderecoSelecionado) {
            enderecoSelecionado = enderecoPrincipal.id_endereco;
        }
        
        // Atualizar o estilo do selecionado
        document.querySelectorAll('.endereco-opcao').forEach(el => {
            const radio = el.querySelector('input');
            if (radio && parseInt(radio.value) === enderecoSelecionado) {
                radio.checked = true;
                el.style.borderColor = 'var(--primary)';
            } else if (radio) {
                el.style.borderColor = 'var(--border)';
            }
        });
        
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

function selecionarEndereco(enderecoId) {
    enderecoSelecionado = enderecoId;
    
    // Atualizar visual
    document.querySelectorAll('.endereco-opcao').forEach(el => {
        const radio = el.querySelector('input');
        if (radio && parseInt(radio.value) === enderecoId) {
            radio.checked = true;
            el.style.borderColor = 'var(--primary)';
        } else if (radio) {
            radio.checked = false;
            el.style.borderColor = 'var(--border)';
        }
    });
}

async function finalizarPedido() {
    if (!enderecoSelecionado) {
        mostrarMensagem('Selecione um endereço de entrega', 'warning');
        return;
    }
    
    loading(true);
    
    try {
        const pedido = {
            endereco_id: enderecoSelecionado,
            transportadora_id: 1,
            valor_frete: 0
        };
        
        const result = await API.criarPedido(pedido);
        
        mostrarMensagem('Pedido realizado com sucesso!');
        
        setTimeout(() => {
            window.location.href = `pedido-confirmado.html?id=${result.pedido_id}`;
        }, 1500);
        
    } catch (error) {
        console.error('Erro detalhado:', error);
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}