let conversaAtual = null;

async function carregarConversas() {
    const container = document.getElementById('conversas-container');
    
    try {
        // Simular conversas por enquanto (backend será implementado depois)
        const conversasSimuladas = [
            {
                id: 1,
                nome: "Suporte SYP",
                ultima_mensagem: "Olá! Como podemos ajudar?",
                data: new Date().toISOString(),
                nao_lidas: 0
            },
            {
                id: 2,
                nome: "João Vendedor",
                ultima_mensagem: "Seu produto foi enviado!",
                data: new Date().toISOString(),
                nao_lidas: 1
            }
        ];
        
        if (conversasSimuladas.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: var(--spacing-xl); color: var(--text-secondary);">Nenhuma conversa ainda</p>';
            return;
        }
        
        container.innerHTML = conversasSimuladas.map(conv => `
            <div class="conversa-item" onclick="selecionarConversa(${conv.id})" 
                 style="padding: var(--spacing-md); border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.3s;"
                 onmouseover="this.style.background='var(--bg-light)'" 
                 onmouseout="this.style.background='transparent'">
                <div style="display: flex; justify-content: space-between; margin-bottom: var(--spacing-xs);">
                    <strong>${conv.nome}</strong>
                    <span style="font-size: 0.75rem; color: var(--text-secondary);">${formatarData(conv.data)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.875rem; color: var(--text-secondary);">${conv.ultima_mensagem}</span>
                    ${conv.nao_lidas > 0 ? `<span style="background: var(--primary); color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.7rem;">${conv.nao_lidas}</span>` : ''}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

async function selecionarConversa(conversaId) {
    conversaAtual = conversaId;
    
    // Atualizar header
    const header = document.getElementById('conversa-header');
    header.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3>${conversaId === 1 ? 'Suporte SYP' : 'João Vendedor'}</h3>
            <span class="badge-stock">Online</span>
        </div>
    `;
    
    // Mostrar área de input
    document.getElementById('mensagem-input-area').style.display = 'block';
    
    // Carregar mensagens
    await carregarMensagens(conversaId);
}

async function carregarMensagens(conversaId) {
    const container = document.getElementById('mensagens-container');
    
    // Simular mensagens
    const mensagensSimuladas = {
        1: [
            { id: 1, remetente: "Suporte SYP", conteudo: "Olá! Bem-vindo ao SYP Shop!", data: new Date(), enviada_por_mim: false },
            { id: 2, remetente: "Você", conteudo: "Olá! Preciso de ajuda com um pedido", data: new Date(), enviada_por_mim: true },
            { id: 3, remetente: "Suporte SYP", conteudo: "Claro! Em que posso ajudar?", data: new Date(), enviada_por_mim: false }
        ],
        2: [
            { id: 1, remetente: "João Vendedor", conteudo: "Olá! Seu pedido foi enviado hoje", data: new Date(), enviada_por_mim: false },
            { id: 2, remetente: "Você", conteudo: "Ótimo! Obrigado pelo aviso", data: new Date(), enviada_por_mim: true }
        ]
    };
    
    const mensagens = mensagensSimuladas[conversaId] || [];
    
    if (mensagens.length === 0) {
        container.innerHTML = '<div class="alert alert-info" style="text-align: center;">Nenhuma mensagem ainda</div>';
        return;
    }
    
    container.innerHTML = mensagens.map(msg => `
        <div style="display: flex; justify-content: ${msg.enviada_por_mim ? 'flex-end' : 'flex-start'}; margin-bottom: var(--spacing-md);">
            <div style="max-width: 70%; background: ${msg.enviada_por_mim ? 'var(--primary)' : 'var(--bg-light)'}; 
                        color: ${msg.enviada_por_mim ? 'white' : 'var(--text-primary)'}; 
                        padding: var(--spacing-sm) var(--spacing-md); border-radius: ${msg.enviada_por_mim ? '12px 4px 12px 12px' : '4px 12px 12px 12px'};">
                <p style="margin-bottom: var(--spacing-xs);">${msg.conteudo}</p>
                <span style="font-size: 0.7rem; opacity: 0.7;">${formatarHora(msg.data)}</span>
            </div>
        </div>
    `).join('');
    
    // Rolar para o final
    container.scrollTop = container.scrollHeight;
}

function formatarHora(data) {
    return new Date(data).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

async function enviarMensagem() {
    const input = document.getElementById('nova-mensagem');
    const conteudo = input.value.trim();
    
    if (!conteudo || !conversaAtual) return;
    
    // Limpar input
    input.value = '';
    
    // Adicionar mensagem localmente (simulação)
    const container = document.getElementById('mensagens-container');
    const novaMensagem = `
        <div style="display: flex; justify-content: flex-end; margin-bottom: var(--spacing-md);">
            <div style="max-width: 70%; background: var(--primary); color: white; 
                        padding: var(--spacing-sm) var(--spacing-md); border-radius: 12px 4px 12px 12px;">
                <p style="margin-bottom: var(--spacing-xs);">${conteudo}</p>
                <span style="font-size: 0.7rem; opacity: 0.7;">Agora</span>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', novaMensagem);
    container.scrollTop = container.scrollHeight;
    
    // Simular resposta automática (apenas para demonstração)
    setTimeout(() => {
        const resposta = `
            <div style="display: flex; justify-content: flex-start; margin-bottom: var(--spacing-md);">
                <div style="max-width: 70%; background: var(--bg-light); color: var(--text-primary); 
                            padding: var(--spacing-sm) var(--spacing-md); border-radius: 4px 12px 12px 12px;">
                    <p style="margin-bottom: var(--spacing-xs);">Mensagem recebida! Em breve responderemos.</p>
                    <span style="font-size: 0.7rem; opacity: 0.7;">Agora</span>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', resposta);
        container.scrollTop = container.scrollHeight;
    }, 1000);
}

// Permitir enviar com Enter
document.getElementById('nova-mensagem')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        enviarMensagem();
    }
});