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
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalRemoverProducao); });
    }
    
    function openDeleteModal(idProducao, catadorNome, residuoTipo, quantidade) {
        const confirmTextCatadorNome = modalRemoverProducao.querySelector('#catador-nome');
        const confirmTextResiduoTipo = modalRemoverProducao.querySelector('#residuo-tipo');
        const confirmTextResiduoQuantidade = modalRemoverProducao.querySelector('#residuo-quantidade');
        if (confirmTextCatadorNome) confirmTextCatadorNome.textContent = catadorNome;
        if (confirmTextResiduoTipo) confirmTextResiduoTipo.textContent = residuoTipo;
        if (confirmTextResiduoQuantidade) confirmTextResiduoQuantidade.textContent = quantidade;

        // substituindo o placeholder 0 do atributo action do form pelo id da produção a ser alterada
        const formAlterarDemanda = modalRemoverProducao.querySelector('#form-remover-producao');
        let actionUrl = formAlterarDemanda.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${idProducao}`);
        formAlterarDemanda.setAttribute('action', actionUrl);

        openModal(modalRemoverProducao);
    }

    removerProducaoBtns.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            const idProducao = row.getAttribute('data-id-producao');
            const quantidade = row.getAttribute('data-quantidade');
            const tipoResiduo = row.getAttribute('data-tipo-residuo');

            // const tipoResiduo = row.cells[2].textContent.trim();
            const catadorNome = row.cells[0].textContent.trim();

            openDeleteModal(idProducao, catadorNome, tipoResiduo, quantidade);
        });
    });

});