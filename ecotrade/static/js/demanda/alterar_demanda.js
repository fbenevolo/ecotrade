document.addEventListener('DOMContentLoaded', function () {
    const modalAlterarDemanda = document.getElementById('modal-alterar-demanda');
    const editDemandaButtons = document.querySelectorAll('button.edit-demanda-btn');

    const alterarCloseBtn = document.getElementById('modal-alterar-close-btn');
    const alterarCancelBtn = document.getElementById('modal-alterar-cancel-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    function openAlterarDemandaModal(idDemanda, tipoResiduo) {
        if (!modalAlterarDemanda) return;
        
        // substituindo o placeholder 0 pelo id da demanda a ser alterada
        const formAlterarDemanda = modalAlterarDemanda.querySelector('#form-alterar-demanda');
        let actionUrl = formAlterarDemanda.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${idDemanda}`);
        formAlterarDemanda.setAttribute('action', actionUrl);
        
        // preenchendo o tipo de resíduo no campo Residuo (readonly)
        const tipoResiduoField = modalAlterarDemanda.querySelector('input[name="nome_residuo"]');
        tipoResiduoField.value = tipoResiduo;

        openModal(modalAlterarDemanda);
    }
    
    editDemandaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const idDemanda = row.getAttribute('data-demanda-id')
            const tipoResiduo = row.getAttribute('data-tipo-residuo');
            openAlterarDemandaModal(idDemanda, tipoResiduo);
        });
    });

    if (modalAlterarDemanda) {
        alterarCloseBtn.addEventListener('click', () => closeModal(modalAlterarDemanda));
        alterarCancelBtn.addEventListener('click', () => closeModal(modalAlterarDemanda));
    }
});