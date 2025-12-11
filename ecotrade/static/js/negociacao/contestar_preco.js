document.addEventListener('DOMContentLoaded', function() {
    const modalContestarPreco = document.getElementById('modal-contestar-preco');
    const contestarPrecoBtn = document.querySelectorAll('button.contestar-preco-btn');
    // Funções genéricas de modal
    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalContestarPreco) {
        const closeContestarBtn = modalContestarPreco ? modalContestarPreco.querySelector('#close-btn') : null;
        closeContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPreco);
        });


        const cancelContestarBtn = modalContestarPreco ? modalContestarPreco.querySelector('#cancel-btn') : null;
        cancelContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPreco);
        });
    }

    function prepareAndOpenModal(modal, negociacaoId, precoAtual, acao, tipoUsuario) {
        if (!modal) return;
        
        const hiddenIdInput = modal.querySelector('input[name="id_negociacao"]');
        const hiddenOpcoesInput = modal.querySelector('input[name="opcoes"]');
        const hiddenTipoUsuarioInput = modal.querySelector('input[name="tipo_usuario"]');
        const spanPrecoAtual = modalContestarPreco.querySelector('#span-preco-atual');

        if (hiddenIdInput) hiddenIdInput.value = negociacaoId;
        if (spanPrecoAtual) spanPrecoAtual.innerHTML = precoAtual;
        if (hiddenOpcoesInput) hiddenOpcoesInput.value = acao; 
        if (hiddenTipoUsuarioInput) hiddenTipoUsuarioInput.value = tipoUsuario;

        openModal(modal);
    }

    contestarPrecoBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let btn = e.currentTarget;
            let negociacaoId = btn.getAttribute('data-negociacao-id');
            let tipoUsuario = btn.getAttribute('data-tipo-usuario');
            let precoAtual = btn.getAttribute('data-preco-atual');
            prepareAndOpenModal(modalContestarPreco, negociacaoId, precoAtual, 'contestar', tipoUsuario);
        });
    });
});