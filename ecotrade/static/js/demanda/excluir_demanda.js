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

    function openExcluirDemandaModal(idDemanda) {
         // substituindo o placeholder 0 pelo id da demanda a ser excluida
        const formExcluirDemanda = modalExcluirDemanda.querySelector('#form-excluir-demanda');
        let actionUrl = formExcluirDemanda.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${idDemanda}`);
        formExcluirDemanda.setAttribute('action', actionUrl);

        openModal(modalExcluirDemanda);
    }

    openModalBtn.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const idDemanda = row.getAttribute('data-id-demanda');

            openExcluirDemandaModal(idDemanda);
        });
    })

    if (modalExcluirDemanda) {
        modalCancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalExcluirDemanda);
        })
    }
});