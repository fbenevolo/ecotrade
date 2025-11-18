document.addEventListener('DOMContentLoaded', function() {
    const modalRemoverProducao = document.getElementById('modal-remover-producao');
    const removerProducaoBtns = document.querySelectorAll('button.delete-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    
    if (modalRemoverProducao) {
        const cancelBtn = document.getElementById('modal-remover-cancel-btn');
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalRemoverProducao);
        });
    }
    
    function openDeleteModal(producaoId, catadorNome, residuoTipo, quantidade) {
        const hiddenProducaoPkInput = modalRemoverProducao.querySelector('input[name="producao_pk"]');
        const hiddenResiduoInput = modalRemoverProducao.querySelector('input[name="residuo"]');
        const hiddenQuantidadeInput = modalRemoverProducao.querySelector('input[name="quantidade"]');

        const confirmTextCatadorNome = modalRemoverProducao.querySelector('#catador-nome');
        const confirmTextResiduoTipo = modalRemoverProducao.querySelector('#residuo-tipo');
        const confirmTextResiduoQuantidade = modalRemoverProducao.querySelector('#residuo-quantidade');
        
        if (confirmTextCatadorNome) confirmTextCatadorNome.textContent = catadorNome;
        if (confirmTextResiduoTipo) confirmTextResiduoTipo.textContent = residuoTipo;
        if (confirmTextResiduoQuantidade) confirmTextResiduoQuantidade.textContent = quantidade;

        if (hiddenProducaoPkInput) hiddenProducaoPkInput.value = producaoId;
        const row = document.querySelector(`tr[data-producao-id="${producaoId}"]`);
        if (row) {
            if (hiddenResiduoInput) hiddenResiduoInput.value = row.getAttribute('data-residuo');
            if (hiddenQuantidadeInput) hiddenQuantidadeInput.value = row.getAttribute('data-quantidade');
        }

        openModal(modalRemoverProducao);
    }

    removerProducaoBtns.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const producaoId = row.getAttribute('data-producao-id');
            const catadorNome = row.cells[0].textContent.trim();
            const residuoTipo = row.cells[2].textContent.trim();
            const quantidade = row.cells[4].textContent.trim();

            openDeleteModal(producaoId, catadorNome, residuoTipo, quantidade);
        });
    });

});