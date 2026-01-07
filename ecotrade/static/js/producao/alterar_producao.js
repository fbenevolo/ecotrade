document.addEventListener('DOMContentLoaded', function () {
    const modalAlterarProducao = document.getElementById('modal-alterar-producao');
    const editBtns = document.querySelectorAll('button.edit-producao-btn');
    
    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };
    
    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

     if (modalAlterarProducao) {
        const closeBtn = modalAlterarProducao.querySelector('#modal-alterar-close-btn');
        const cancelBtn = modalAlterarProducao.querySelector('#modal-alterar-cancel-btn');
        closeBtn.addEventListener('click', () => closeModal(modalAlterarProducao));
        cancelBtn.addEventListener('click', () => closeModal(modalAlterarProducao));
    }
    
    function openEditProducaoModal(producaoData) {
        /* Preenchenco com os valores já existentes */
        const editCatadorInput = modalAlterarProducao.querySelector('select[name="id_catador"]');
        const editResiduoInput = modalAlterarProducao.querySelector('select[name="id_residuo"]');
        const editDataInput = modalAlterarProducao.querySelector('input[name="data"]');
        const editQuantidadeInput = modalAlterarProducao.querySelector('input[name="producao"]');
        if (editResiduoInput) editResiduoInput.value = producaoData.idResiduo;
        if (editCatadorInput) editCatadorInput.value = producaoData.idCatador;
        if (editDataInput) editDataInput.value = producaoData.data;
        if (editQuantidadeInput) editQuantidadeInput.value = producaoData.quantidade;

        // substituindo o placeholder 0 na action do form pelo id da produção a ser alterada
        const formAlterarProducao = modalAlterarProducao.querySelector('#form-alterar-producao');
        let actionUrl = formAlterarProducao.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${producaoData.idProducao}`);
        formAlterarProducao.setAttribute('action', actionUrl);

        openModal(modalAlterarProducao);
    }

    editBtns.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const data = {
                idProducao: row.getAttribute('data-id-producao'),
                idResiduo: row.getAttribute('data-tipo-residuo'),
                idCatador: row.getAttribute('data-id-catador'),
                data: row.getAttribute('data-data-producao'),
                quantidade: row.getAttribute('data-quantidade').replace(',', '.'),
            }
            openEditProducaoModal(data);
        });
    });
})