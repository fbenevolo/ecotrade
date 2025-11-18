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
        const editPkHiddenInput = modalAlterarProducao.querySelector('input[name="producao_pk"]');
        const editCatadorInput = modalAlterarProducao.querySelector('select[name="id_catador"]');
        const editResiduoInput = modalAlterarProducao.querySelector('select[name="id_residuo"]');
        const editDataInput = modalAlterarProducao.querySelector('input[name="data"]');
        const editQuantidadeInput = modalAlterarProducao.querySelector('input[name="producao"]');

        if (editPkHiddenInput) editPkHiddenInput.value = producaoData.pk;
        if (editCatadorInput) editCatadorInput.value = producaoData.catadorPk;
        if (editResiduoInput) editResiduoInput.value = producaoData.residuoPk;
        if (editDataInput) editDataInput.value = producaoData.data;
        if (editQuantidadeInput) editQuantidadeInput.value = producaoData.quantidade;

        openModal(modalAlterarProducao);
    }

    editBtns.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const data = {
                pk: row.getAttribute('data-producao-id'),
                residuoPk: row.getAttribute('data-residuo'),
                catadorPk: row.getAttribute('data-catador-pk'),
                data: row.getAttribute('data-data-producao'),
                quantidade: row.getAttribute('data-quantidade').replace(',', '.'),
            }
            openEditProducaoModal(data);
        });
    });
})