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
        const cancelBtn = modalContestarPagamento.querySelector('#cancel-btn');
        
        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalContestarPagamento); });
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalContestarPagamento); });
    }

    openModalBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(modalContestarPagamento);
        });
    })

});