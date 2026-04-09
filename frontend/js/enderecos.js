async function carregarEnderecos() {
    const container = document.getElementById('lista-enderecos');
    
    try {
        const enderecos = await API.listarEnderecos();
        
        if (enderecos.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Nenhum endereço cadastrado.</p>';
            return;
        }
        
        container.innerHTML = enderecos.map(end => `
            <div class="endereco-item" style="border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--spacing-md); margin-bottom: var(--spacing-md); ${end.principal ? 'border-left: 4px solid var(--primary);' : ''}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <p><strong>${end.logradouro}, ${end.numero}</strong> ${end.complemento ? `- ${end.complemento}` : ''}</p>
                        <p>${end.bairro} - ${end.cidade}/${end.estado}</p>
                        <p>CEP: ${end.cep}</p>
                        ${end.principal ? '<span class="badge-stock" style="margin-top: 8px; display: inline-block;">Principal</span>' : ''}
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="editarEndereco(${end.id_endereco})" class="btn-outline" style="padding: 4px 12px;">✏️</button>
                        <button onclick="deletarEndereco(${end.id_endereco})" class="btn-danger" style="padding: 4px 12px;">🗑️</button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

function mostrarModalEndereco() {
    document.getElementById('modal-titulo').textContent = 'Novo Endereço';
    document.getElementById('endereco-id').value = '';
    document.getElementById('endereco-form').reset();
    document.getElementById('modal-endereco').classList.add('active');
}

function fecharModalEndereco() {
    document.getElementById('modal-endereco').classList.remove('active');
}

async function editarEndereco(id) {
    try {
        const enderecos = await API.listarEnderecos();
        const endereco = enderecos.find(e => e.id_endereco === id);
        
        if (!endereco) return;
        
        document.getElementById('modal-titulo').textContent = 'Editar Endereço';
        document.getElementById('endereco-id').value = endereco.id_endereco;
        document.getElementById('cep').value = endereco.cep;
        document.getElementById('logradouro').value = endereco.logradouro;
        document.getElementById('numero').value = endereco.numero;
        document.getElementById('complemento').value = endereco.complemento || '';
        document.getElementById('bairro').value = endereco.bairro;
        document.getElementById('cidade').value = endereco.cidade;
        document.getElementById('estado').value = endereco.estado;
        document.getElementById('principal').checked = endereco.principal;
        
        document.getElementById('modal-endereco').classList.add('active');
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    }
}

async function deletarEndereco(id) {
    if (!confirm('Tem certeza que deseja excluir este endereço?')) return;
    
    loading(true);
    
    try {
        await API.deletarEndereco(id);
        mostrarMensagem('Endereço excluído com sucesso');
        await carregarEnderecos();
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

// Salvar endereço
document.getElementById('endereco-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const enderecoId = document.getElementById('endereco-id').value;
    const endereco = {
        cep: document.getElementById('cep').value,
        logradouro: document.getElementById('logradouro').value,
        numero: document.getElementById('numero').value,
        complemento: document.getElementById('complemento').value,
        bairro: document.getElementById('bairro').value,
        cidade: document.getElementById('cidade').value,
        estado: document.getElementById('estado').value,
        principal: document.getElementById('principal').checked
    };
    
    loading(true);
    
    try {
        if (enderecoId) {
            await API.atualizarEndereco(enderecoId, endereco);
            mostrarMensagem('Endereço atualizado com sucesso');
        } else {
            await API.criarEndereco(endereco);
            mostrarMensagem('Endereço adicionado com sucesso');
        }
        
        fecharModalEndereco();
        await carregarEnderecos();
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
});

// Buscar CEP via ViaCEP API
async function buscarCep() {
    const cep = document.getElementById('cep').value.replace(/\D/g, '');
    
    if (cep.length !== 8) {
        mostrarMensagem('CEP inválido. Digite 8 números.', 'warning');
        return;
    }
    
    loading(true);
    
    try {
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await response.json();
        
        if (data.erro) {
            mostrarMensagem('CEP não encontrado', 'error');
            return;
        }
        
        document.getElementById('logradouro').value = data.logradouro || '';
        document.getElementById('bairro').value = data.bairro || '';
        document.getElementById('cidade').value = data.localidade || '';
        document.getElementById('estado').value = data.uf || '';
        
        mostrarMensagem('CEP encontrado!', 'success');
        
    } catch (error) {
        mostrarMensagem('Erro ao buscar CEP', 'error');
    } finally {
        loading(false);
    }
}