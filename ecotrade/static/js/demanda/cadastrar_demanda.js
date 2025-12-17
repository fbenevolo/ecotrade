document,addEventListener('DOMContentLoaded', function () {
    const cadastrarDemandaModal = document.getElementById('cadastrar-demanda-modal');
    const openCadastrarDemanda = document.getElementById('cadastrar-demanda-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (cadastrarDemandaModal) {
        const cancelDemanda = document.getElementById('cancel-demanda-button');
        cancelDemanda.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(cadastrarDemandaModal);
        });
    }

    if (openCadastrarDemanda) {
        openCadastrarDemanda.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(cadastrarDemandaModal)
        })
    }
});