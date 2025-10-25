document.addEventListener('DOMContentLoaded', function () {
    const modalContestarPagamento = document.getElementById('modal-contestar-pgto');
    const openModalBtn = document.querySelectorAll('button.contestar-pgto-btn');
    
    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };


    if (modalContestarPagamento) {
        const closeBtn = modalContestarPagamento.querySelector('#close-btn');
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPagamento);
        });
        const cancelBtn = modalContestarPagamento.querySelector('#cancel-btn');
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPagamento);
        });
    }

    function openContestarModal(negociacaoId, antigaContestacaoId) {
        const hiddenNegociacaoIdInput = modalContestarPagamento.querySelector('input[name="id_negociacao"]');
        const hiddenAntigaContestacaoInput = modalContestarPagamento.querySelector('input[name="id_antiga_contestacao"]');

        if (hiddenNegociacaoIdInput) hiddenNegociacaoIdInput.value = negociacaoId;
        if (hiddenAntigaContestacaoInput) hiddenAntigaContestacaoInput.value = antigaContestacaoId;

        openModal(modalContestarPagamento);
    }

    openModalBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const button = e.currentTarget.closest('button');
            const negociacaoId = button.getAttribute('data-negociacao-id');
            const antigaContestacaoId = button.getAttribute('data-contestacao-id')
            openContestarModal(negociacaoId, antigaContestacaoId);
        });
    })

});