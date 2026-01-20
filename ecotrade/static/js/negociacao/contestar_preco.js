document.addEventListener('DOMContentLoaded', function() {
    const modalContestarPreco = document.getElementById('modal-contestar-preco');
    const contestarPrecoBtn = document.querySelectorAll('button.contestar-preco-btn');
    
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

    function prepareAndOpenModal(modal, idNegociacao, precoAtual) {        
        const negociacaoIdInput = modal.querySelector('input[name="id_negociacao"]');
        const spanPrecoAtual = modalContestarPreco.querySelector('#span-preco-atual');
        if (negociacaoIdInput) negociacaoIdInput.value = idNegociacao;
        if (spanPrecoAtual) spanPrecoAtual.innerHTML = precoAtual;

        // substituindo o placeholder 0 pelo id da negociacao a ser contestada
        const formContestarPreco = modalContestarPreco.querySelector('#form-contestar-preco');
        let actionUrl = formContestarPreco.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${idNegociacao}`);
        formContestarPreco.setAttribute('action', actionUrl);

        openModal(modal);
    }

    contestarPrecoBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let btn = e.currentTarget;
            let negociacaoId = btn.getAttribute('data-negociacao-id');
            let precoAtual = btn.getAttribute('data-preco-atual');
            prepareAndOpenModal(modalContestarPreco, negociacaoId, precoAtual);
        });
    });
});