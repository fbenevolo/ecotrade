document.addEventListener('DOMContentLoaded', function () {
    const modalExcluirDemanda = document.getElementById('modal-excluir-demanda');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    
    const openModalBtn = document.querySelectorAll('button.delete-demanda-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    function openExcluirDemandaModal(demandaId) {
        const hiddenDemandaIdInput = modalExcluirDemanda.querySelector('input[name="id_demanda"]');
        hiddenDemandaIdInput.value = demandaId;
        openModal(modalExcluirDemanda);

    }

    openModalBtn.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const demandaId = row.getAttribute('data-demanda-id');

            openExcluirDemandaModal(demandaId);
        });
    })

    if (modalExcluirDemanda) {
        modalCancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalExcluirDemanda);
        })
    }
});