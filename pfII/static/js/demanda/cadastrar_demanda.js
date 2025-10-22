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
        const cancelDemanda = document.getElementById('cancel-demand-button');
        cancelDemanda.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(cadastrarDemandaModal);
        });
    }

    function openCadastrarDemandaModal(idEmpresa) {

        const hiddenEmpresaInput = cadastrarDemandaModal.querySelector('input[name="id_empresa"]');
        hiddenEmpresaInput.value = idEmpresa;
        openModal(cadastrarDemandaModal)
    }

    openCadastrarDemanda.addEventListener('click', (e) => {
        e.preventDefault();
        
        const btn = e.currentTarget.closest('button');   
        idEmpresa = btn.getAttribute('data-id-empresa');

        openCadastrarDemandaModal(idEmpresa);
    })
});