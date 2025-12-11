document.addEventListener('DOMContentLoaded', function() {
    const modalConfirmarPagamento = document.getElementById('modal-confirmar-pagamento');
    const btnConfirmarPgto = document.querySelectorAll('button.confirmar-pgto-btn');

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    if (modalConfirmarPagamento) {
        const closeBtn = modalConfirmarPagamento.querySelector('#close-btn');
        const cancelBtn = modalConfirmarPagamento.querySelector('#cancel-btn')

        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalConfirmarPagamento);
        });


        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalConfirmarPagamento);
        });
    }

    function openModalConfirmarPgto(idNegociacao, opcao) {
        const hiddenIdNegociacaoInput = modalConfirmarPagamento.querySelector('input[name="id_negociacao"]');
        if (hiddenIdNegociacaoInput) hiddenIdNegociacaoInput.value = idNegociacao; 

        openModal(modalConfirmarPagamento);
    }

    btnConfirmarPgto.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const btn = e.currentTarget.closest('button');
            const idNegociacao = btn.getAttribute('data-id-negociacao');
            openModalConfirmarPgto(idNegociacao);

        });
    }); 
});