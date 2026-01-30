document.addEventListener('DOMContentLoaded', function () {
    
    /* Modais */
    const confirmarPrecoModal = document.getElementById('modal-confirmar-negociacao');
    const sairNegociacaoModal = document.getElementById('modal-sair-negociacao');
        
    /* Botões para abrir modal */
    const confirmarPrecoBtn = document.querySelector('button.confirmar-negociacao-btn');
    const sairNegociacaoBtn = document.querySelector('button.sair-negociacao-btn');

    /* Funções de abrir e fechar modal */
    const closeModal = (modal) => { if (modal) modal.classList.add('hidden'); };
    const openModal = (modal) => { if (modal) modal.classList.remove('hidden'); };


    // function prepareAndOpenModal(modal, negociacaoId, acao, tipoUsuario) {
    //     if (!modal) return;
        
    //     const hiddenIdInput = modal.querySelector('input[name="id_negociacao"]');
    //     const hiddenOpcoesInput = modal.querySelector('input[name="opcoes"]');
    //     const hiddenTipoUsuarioInput = modal.querySelector('input[name="tipo_usuario"]');
        
    //     if (hiddenIdInput) hiddenIdInput.value = negociacaoId;
    //     if (hiddenOpcoesInput) hiddenOpcoesInput.value = acao; 
    //     if (hiddenTipoUsuarioInput) hiddenTipoUsuarioInput.value = tipoUsuario;

    //     openModal(modal);
    // }

    /* Lógiva de fechamento de modais  */
    if (confirmarPrecoModal) {
        const cancelConfirmarBtn = document.getElementById('cancel-confirmar-btn');
        cancelConfirmarBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(confirmarPrecoModal); });
    }

    if (sairNegociacaoModal) {
        const cancelSairBtn = document.getElementById('cancel-sair-btn');
        cancelSairBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(sairNegociacaoModal); });
    }

    /* Lógica de abertura de modais */
    if (confirmarPrecoBtn) {
        confirmarPrecoBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(confirmarPrecoModal); 
        });

        sairNegociacaoBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(sairNegociacaoModal);
        });
    }


});