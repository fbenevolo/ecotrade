document.addEventListener('DOMContentLoaded', function () {
    const modalAprovarCatador = document.getElementById('modal-aprovar-catador');
    
    // Elementos do modal de aprovação de catador
    const aprovarCatadorButtons = document.querySelectorAll('button.aprovar-catador-btn');
    const aprovarCloseBtn = document.getElementById('modal-aprovar-close-btn');
    const aprovarCancelBtn = document.getElementById('modal-aprovar-cancel-btn');
    
    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    // --- Lógica do Modal de Aprovação de Catador ---
    function openAprovarCatadorModal(catadorData) {
        // Preencher as informações do catador no modal
        const nomeDisplay = document.getElementById('catador-nome-display');
        const emailDisplay = document.getElementById('catador-email-display');
        const cooperativaDisplay = document.getElementById('catador-cooperativa-display');
        const statusDisplay = document.getElementById('catador-status-display');
        const usuarioIdInput = modalAprovarCatador.querySelector('input[name="usuario_id"]');
        if (nomeDisplay) nomeDisplay.textContent = catadorData.nome;
        if (emailDisplay) emailDisplay.textContent = catadorData.email;
        if (cooperativaDisplay) cooperativaDisplay.textContent = catadorData.cooperativa;
        if (statusDisplay) statusDisplay.textContent = catadorData.statusDisplay;
        if (usuarioIdInput) usuarioIdInput.value = catadorData.email;


        // substituindo o placeholder 0 pelo id da demanda a ser alterada
        const formAprovarCatador = modalAprovarCatador.querySelector('#form-aprovar-catador');
        let actionUrl = formAprovarCatador.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${catadorData.email}`);
        formAprovarCatador.setAttribute('action', actionUrl);

        // Limpar seleções anteriores
        const radioButtons = modalAprovarCatador.querySelectorAll('input[name="acao"]');
        radioButtons.forEach(radio => radio.checked = false);
        
        openModal(modalAprovarCatador);
    }
    
    // Event listeners para os botões de aprovação
    aprovarCatadorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const catadorData = {
                nome: row.getAttribute('data-catador-nome'),
                email: row.getAttribute('data-catador-email'),
                status: row.getAttribute('data-catador-status'),
                statusDisplay: row.getAttribute('data-catador-status-display'),
                cooperativa: row.getAttribute('data-catador-cooperativa')
            };
            
            openAprovarCatadorModal(catadorData);
        });
    });
    
    // Event listeners para fechar modal de aprovação
    if (modalAprovarCatador) {
        if (aprovarCloseBtn) {
            aprovarCloseBtn.addEventListener('click', () => closeModal(modalAprovarCatador));
        }
        if (aprovarCancelBtn) {
            aprovarCancelBtn.addEventListener('click', () => closeModal(modalAprovarCatador));
        }
        
        // Fechar modal ao clicar no fundo
        modalAprovarCatador.addEventListener('click', function(e) {
            if (e.target.id === 'modal-aprovar-catador') {
                closeModal(modalAprovarCatador);
            }
        });
    }
});
