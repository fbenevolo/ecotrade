document.addEventListener('DOMContentLoaded', function () {
    const modalAlterarDemanda = document.getElementById('modal-alterar-demanda');
    const editDemandaButtons = document.querySelectorAll('button.edit-demanda-btn');

    const alterarCloseBtn = document.getElementById('modal-alterar-close-btn');
    const alterarCancelBtn = document.getElementById('modal-alterar-cancel-btn');

    const alterarPkInput = modalAlterarDemanda ? modalAlterarDemanda.querySelector('input[name="id_demanda"]') : null;
    const alterarResiduoInput = modalAlterarDemanda ? modalAlterarDemanda.querySelector('select[name="id_residuo"]') : null;
    const alterarQuantidadeInput = modalAlterarDemanda ? modalAlterarDemanda.querySelector('input[name="quantidade"]') : null;
    const alterarDisplayDemanda = modalAlterarDemanda ? modalAlterarDemanda.querySelector('#demanda-tipo-display') : null;

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    function openAlterarDemandaModal(demandaData) {
        if (!modalAlterarDemanda) return;
        
        if (alterarDisplayDemanda) alterarDisplayDemanda.textContent = demandaData.tipoResiduo;
        if (alterarPkInput) alterarPkInput.value = demandaData.pk;
        
        if (alterarResiduoInput) alterarResiduoInput.value = demandaData.residuoPk;
        if (alterarQuantidadeInput) alterarQuantidadeInput.value = demandaData.quantidade;
        
        openModal(modalAlterarDemanda);
    }
    
    // Listener de Abertura (Tabela)
    editDemandaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const demandaData = {
                pk: row.getAttribute('data-demanda-id'),
                tipoResiduo: row.getAttribute('data-tipo-residuo'),
                residuoPk: row.getAttribute('data-residuo-id'),
                quantidade: row.getAttribute('data-quantidade'),
            };

            console.log(demandaData);
            
            openAlterarDemandaModal(demandaData);
        });
    });

    if (modalAlterarDemanda) {
        alterarCloseBtn.addEventListener('click', () => closeModal(modalAlterarDemanda));
        alterarCancelBtn.addEventListener('click', () => closeModal(modalAlterarDemanda));
        modalAlterarDemanda.addEventListener('click', (e) => {
            if (e.target.id === 'modal-alterar-demanda') {
                closeModal(modalAlterarDemanda);
            }
        });
    }
});