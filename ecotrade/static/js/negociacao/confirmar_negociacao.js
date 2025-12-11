document.addEventListener('DOMContentLoaded', function () {
    const modalConfirmarPreco = document.getElementById('modal-confirmar-negociacao');
    const modalSairNegociacao = document.getElementById('modal-sair-negociacao');
        
    const confirmarPrecoBtn = document.querySelector('button.confirmar-negociacao-btn');
    const sairNegociacaoBtn = document.querySelector('button.sair-negociacao-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };


    function prepareAndOpenModal(modal, negociacaoId, acao, tipoUsuario) {
        if (!modal) return;
        
        const hiddenIdInput = modal.querySelector('input[name="id_negociacao"]');
        const hiddenOpcoesInput = modal.querySelector('input[name="opcoes"]');
        const hiddenTipoUsuarioInput = modal.querySelector('input[name="tipo_usuario"]');
        
        if (hiddenIdInput) hiddenIdInput.value = negociacaoId;
        if (hiddenOpcoesInput) hiddenOpcoesInput.value = acao; 
        if (hiddenTipoUsuarioInput) hiddenTipoUsuarioInput.value = tipoUsuario;

        openModal(modal);
    }

    if (modalConfirmarPreco) {
        const cancelConfirmarBtn = document.getElementById('cancel-confirmar-btn');
        cancelConfirmarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalConfirmarPreco);
        });
        modalConfirmarPreco.addEventListener('click', (e) => {
            if (e.target.id === 'modal-confirmar-negociacao') {
                closeModal(modalConfirmarPreco);
            }
        });
    }

    if (modalSairNegociacao) {
        const cancelSairBtn = document.getElementById('cancel-sair-btn');
        cancelSairBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalSairNegociacao);
        });
        modalSairNegociacao.addEventListener('click', (e) => {
            if (e.target.id === 'modal-sair-negociacao') {
                closeModal(modalSairNegociacao);
            }
        });
    }

    if (confirmarPrecoBtn) {
        confirmarPrecoBtn.addEventListener('click', (e) => {
            e.preventDefault();
            let btn = e.currentTarget; 
            let negociacaoId = btn.getAttribute('data-negociacao-id');
            let tipoUsuario = btn.getAttribute('data-tipo-usuario');
            prepareAndOpenModal(modalConfirmarPreco, negociacaoId, 'confirmar', tipoUsuario); 
        });

        sairNegociacaoBtn.addEventListener('click', (e) => {
            e.preventDefault();
            let btn = e.currentTarget;
            let negociacaoId = btn.getAttribute('data-negociacao-id');
            let tipoUsuario = btn.getAttribute('data-tipo-usuario');
            prepareAndOpenModal(modalSairNegociacao, negociacaoId, 'cancelar', tipoUsuario);
        });
    }


});