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

        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalConfirmarPagamento); });
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalConfirmarPagamento); });
    }
    
    btnConfirmarPgto.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(modalConfirmarPagamento);

        });
    }); 
});