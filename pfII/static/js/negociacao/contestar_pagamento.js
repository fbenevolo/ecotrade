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
        const closeBtn = document.getElementById('close-btn');
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPagamento);
        });
        const cancelBtn = document.getElementById('cancel-btn');
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalContestarPagamento);
        });
    }

    function openContestarModal(negociacaoId) {

        const hiddenNegociacaoIdInput = modalContestarPagamento.querySelector('input[name="id_negociacao"]');
        if (hiddenNegociacaoIdInput) hiddenNegociacaoIdInput.value = negociacaoId;

        openModal(modalContestarPagamento);
    }

    openModalBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const button = e.currentTarget.closest('button');
            const negociacaoId = button.getAttribute('data-negociacao-id');
            openContestarModal(negociacaoId);
        });
    })

});