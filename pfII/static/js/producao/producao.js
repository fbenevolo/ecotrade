document.addEventListener('DOMContentLoaded', function () {
    const modalAprovarCatador = document.getElementById('modal-aprovar-catador');
    const modalAlterarCatador = document.getElementById('modal-alterar-catador');
    const modalExcluirCatador = document.getElementById('modal-excluir-catador');

    
    // Elementos do modal de aprovação de catador
    const aprovarCatadorButtons = document.querySelectorAll('button.aprovar-catador-btn');
    const aprovarCloseBtn = document.getElementById('modal-aprovar-close-btn');
    const aprovarCancelBtn = document.getElementById('modal-aprovar-cancel-btn');
    
    // Elementos do modal de alteração de catador
    const editarCatadorButtons = document.querySelectorAll('button.editar-catador-btn');
    const alterarCloseBtn = document.getElementById('modal-alterar-catador-close-btn');
    const alterarCancelBtn = document.getElementById('modal-alterar-catador-cancel-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    // --- Lógica do Modal de Aprovação de Catador ---
    function openAprovarCatadorModal(catadorData) {
        if (!modalAprovarCatador) return;
        
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
    
    // --- Lógica do Modal de Alteração de Catador ---
    function openAlterarCatadorModal(catadorData) {
        if (!modalAlterarCatador) return;
        
        // Preencher os campos do formulário
        const nomeInput = modalAlterarCatador.querySelector('input[name="nome"]');
        const emailInput = modalAlterarCatador.querySelector('input[name="email"]');
        const catadorIdInput = modalAlterarCatador.querySelector('input[name="catador_id"]');
        
        if (nomeInput) nomeInput.value = catadorData.nome;
        if (emailInput) emailInput.value = catadorData.email;
        if (catadorIdInput) catadorIdInput.value = catadorData.email;
        
        openModal(modalAlterarCatador);
    }
    
    // Event listeners para os botões de edição
    editarCatadorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const catadorData = {
                nome: row.getAttribute('data-catador-nome'),
                email: row.getAttribute('data-catador-email')
            };
            
            openAlterarCatadorModal(catadorData);
        });
    });
    
    // Event listeners para fechar modal de alteração
    if (modalAlterarCatador) {
        if (alterarCloseBtn) {
            alterarCloseBtn.addEventListener('click', () => closeModal(modalAlterarCatador));
        }
        if (alterarCancelBtn) {
            alterarCancelBtn.addEventListener('click', () => closeModal(modalAlterarCatador));
        }
        
        // Fechar modal ao clicar no fundo
        modalAlterarCatador.addEventListener('click', function(e) {
            if (e.target.id === 'modal-alterar-catador') {
                closeModal(modalAlterarCatador);
            }
        });
    }

    const checkModalErrors = () => {
        if (modalAprovarCatador && modalAprovarCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalAprovarCatador);
        }
        if (modalAlterarCatador && modalAlterarCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalAlterarCatador);
        }
        if (modalExcluirCatador && modalExcluirCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalExcluirCatador);
        }
    };
    checkModalErrors();
});
