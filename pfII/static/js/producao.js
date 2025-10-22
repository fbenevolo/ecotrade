/*
Scripts referentes à página de produção de uma cooperariva
*/

document.addEventListener('DOMContentLoaded', function () {
    const modalRemoverProducao = document.getElementById('modal-remover-producao');
    const modalAprovarCatador = document.getElementById('modal-aprovar-catador');
    const modalAlterarCatador = document.getElementById('modal-alterar-catador');
    const modalExcluirCatador = document.getElementById('modal-excluir-catador');

    const removerCancelBtn = document.getElementById('modal-remover-cancel-btn');
    const deleteButtons = document.querySelectorAll('button.text-red-500');

    const confirmTextCatadorNome = modalRemoverProducao ? modalRemoverProducao.querySelector('#confirm-catador-nome') : null;
    const confirmTextResiduoTipo = modalRemoverProducao ? modalRemoverProducao.querySelector('#confirm-residuo-tipo') : null;
    const confirmTextResiduoQuantidade = modalRemoverProducao ? modalRemoverProducao.querySelector('#confirm-residuo-quantidade') : null;

    const hiddenProducaoPkInput = modalRemoverProducao ? modalRemoverProducao.querySelector('input[name="producao_pk"]') : null;
    const hiddenResiduoInput = modalRemoverProducao ? modalRemoverProducao.querySelector('input[name="residuo"]') : null;
    const hiddenQuantidadeInput = modalRemoverProducao ? modalRemoverProducao.querySelector('input[name="quantidade"]') : null;
    const hiddenActionInput = modalRemoverProducao ? modalRemoverProducao.querySelector('input[name="action"]') : null;

    const editButtons = document.querySelectorAll('button.edit-btn');
    const editModal = document.getElementById('modal-alterar-producao');
    const editForm = document.getElementById('form-alterar-producao');
    
    // Elementos do modal de aprovação de catador
    const aprovarCatadorButtons = document.querySelectorAll('button.aprovar-catador-btn');
    const aprovarCloseBtn = document.getElementById('modal-aprovar-close-btn');
    const aprovarCancelBtn = document.getElementById('modal-aprovar-cancel-btn');
    
    // Elementos do modal de alteração de catador
    const editarCatadorButtons = document.querySelectorAll('button.editar-catador-btn');
    const alterarCloseBtn = document.getElementById('modal-alterar-catador-close-btn');
    const alterarCancelBtn = document.getElementById('modal-alterar-catador-cancel-btn');
    
    // Elementos do modal de exclusão de catador
    const excluirCatadorButtons = document.querySelectorAll('button.excluir-catador-btn');
    const excluirCloseBtn = document.getElementById('modal-excluir-catador-cancel-btn');

    const editPkInput = editModal ? editForm.querySelector('input[name="producao_pk"]') : null;
    const editCatadorInput = editModal ? editForm.querySelector('select[name="id_catador"]') : null;
    const editResiduoInput = editModal ? editForm.querySelector('select[name="id_residuo"]') : null;
    const editDataInput = editModal ? editForm.querySelector('input[name="data"]') : null;
    const editQuantidadeInput = editModal ? editForm.querySelector('input[name="producao"]') : null;
    const editActionInput = editModal ? editForm.querySelector('input[name="action"]') : null;


    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalRemoverProducao) {
        removerCancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalRemoverProducao); });
        modalRemoverProducao.addEventListener('click', function (e) {
            if (e.target.id === 'modal-remover-producao') {
                closeModal(modalRemoverProducao);
            }
        });
    }

     if (editModal) {
        const closeBtn = document.getElementById('modal-alterar-close-btn');
        const cancelBtn = document.getElementById('modal-alterar-cancel-btn');
        closeBtn.addEventListener('click', () => closeModal(editModal));
        cancelBtn.addEventListener('click', () => closeModal(editModal));
    }

    // --- Lógica de modal Remoção ---
    function openDeleteModal(producaoId, catadorNome, residuoTipo, quantidade) {
        if (!modalRemoverProducao) return;

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

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');

            const producaoId = row.getAttribute('data-producao-id');
            const catadorNome = row.cells[0].textContent.trim();
            const residuoTipo = row.cells[2].textContent.trim();
            const quantidade = row.cells[3].textContent.trim();

            if (producaoId) {
                openDeleteModal(producaoId, catadorNome, residuoTipo, quantidade);
            }
        });
    });

    // --- Lógica de Edição (Update) ---
    function openEditModal(producaoData) {
        if (!editModal || !editForm) return;

        if (editPkInput) editPkInput.value = producaoData.pk;
        if (editActionInput) editActionInput.value = 'update';

        if (editCatadorInput) editCatadorInput.value = producaoData.catadorPk;
        if (editResiduoInput) editResiduoInput.value = producaoData.residuoPk;
        if (editDataInput) editDataInput.value = producaoData.data;
        if (editQuantidadeInput) editQuantidadeInput.value = producaoData.quantidade;

        openModal(editModal);
    }

    editButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');

            const data = {
                pk: row.getAttribute('data-producao-id'),
                residuoPk: row.getAttribute('data-residuo'),
                catadorPk: row.getAttribute('data-catador-pk'),
                data: row.getAttribute('data-data-producao'),
                quantidade: row.cells[3].textContent.trim(),
            };

            openEditModal(data);
        });
    });

    // --- Lógica do Modal de Aprovação de Catador ---
    function openAprovarCatadorModal(catadorData) {
        if (!modalAprovarCatador) return;
        
        // Preencher as informações do catador no modal
        const nomeDisplay = document.getElementById('catador-nome-display');
        const emailDisplay = document.getElementById('catador-email-display');
        const cooperativaDisplay = document.getElementById('catador-cooperativa-display');
        const statusDisplay = document.getElementById('catador-status-display');
        const usuarioIdInput = modalAprovarCatador.querySelector('input[name="usuario_id"]');
        
        if (nomeDisplay) nomeDisplay.textContent = catadorData.nome;
        if (emailDisplay) emailDisplay.textContent = catadorData.email;
        if (cooperativaDisplay) cooperativaDisplay.textContent = catadorData.cooperativa;
        if (statusDisplay) statusDisplay.textContent = catadorData.statusDisplay;
        if (usuarioIdInput) usuarioIdInput.value = catadorData.email;
        
        // Limpar seleções anteriores
        const radioButtons = modalAprovarCatador.querySelectorAll('input[name="acao"]');
        radioButtons.forEach(radio => radio.checked = false);
        
        openModal(modalAprovarCatador);
    }
    
    // Event listeners para os botões de aprovação
    aprovarCatadorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const catadorData = {
                nome: row.getAttribute('data-catador-nome'),
                email: row.getAttribute('data-catador-email'),
                status: row.getAttribute('data-catador-status'),
                statusDisplay: row.getAttribute('data-catador-status-display'),
                cooperativa: row.getAttribute('data-catador-cooperativa')
            };
            
            openAprovarCatadorModal(catadorData);
        });
    });
    
    // Event listeners para fechar modal de aprovação
    if (modalAprovarCatador) {
        if (aprovarCloseBtn) {
            aprovarCloseBtn.addEventListener('click', () => closeModal(modalAprovarCatador));
        }
        if (aprovarCancelBtn) {
            aprovarCancelBtn.addEventListener('click', () => closeModal(modalAprovarCatador));
        }
        
        // Fechar modal ao clicar no fundo
        modalAprovarCatador.addEventListener('click', function(e) {
            if (e.target.id === 'modal-aprovar-catador') {
                closeModal(modalAprovarCatador);
            }
        });
    }
    
    // --- Lógica do Modal de Alteração de Catador ---
    function openAlterarCatadorModal(catadorData) {
        if (!modalAlterarCatador) return;
        
        // Preencher os campos do formulário
        const nomeInput = modalAlterarCatador.querySelector('input[name="nome"]');
        const emailInput = modalAlterarCatador.querySelector('input[name="email"]');
        const catadorIdInput = modalAlterarCatador.querySelector('input[name="catador_id"]');
        
        if (nomeInput) nomeInput.value = catadorData.nome;
        if (emailInput) emailInput.value = catadorData.email;
        if (catadorIdInput) catadorIdInput.value = catadorData.email;
        
        openModal(modalAlterarCatador);
    }
    
    // Event listeners para os botões de edição
    editarCatadorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const catadorData = {
                nome: row.getAttribute('data-catador-nome'),
                email: row.getAttribute('data-catador-email')
            };
            
            openAlterarCatadorModal(catadorData);
        });
    });
    
    // Event listeners para fechar modal de alteração
    if (modalAlterarCatador) {
        if (alterarCloseBtn) {
            alterarCloseBtn.addEventListener('click', () => closeModal(modalAlterarCatador));
        }
        if (alterarCancelBtn) {
            alterarCancelBtn.addEventListener('click', () => closeModal(modalAlterarCatador));
        }
        
        // Fechar modal ao clicar no fundo
        modalAlterarCatador.addEventListener('click', function(e) {
            if (e.target.id === 'modal-alterar-catador') {
                closeModal(modalAlterarCatador);
            }
        });
    }
    
    // --- Lógica do Modal de Exclusão de Catador ---
    function openExcluirCatadorModal(catadorData) {
        if (!modalExcluirCatador) return;
        
        // Preencher as informações do catador
        const nomeDisplay = document.getElementById('excluir-catador-nome');
        const emailDisplay = document.getElementById('excluir-catador-email');
        const catadorIdInput = modalExcluirCatador.querySelector('input[name="catador_id"]');
        const confirmacaoCheckbox = modalExcluirCatador.querySelector('input[name="confirmacao"]');
        
        if (nomeDisplay) nomeDisplay.textContent = catadorData.nome;
        if (emailDisplay) emailDisplay.textContent = catadorData.email;
        if (catadorIdInput) catadorIdInput.value = catadorData.email;
        if (confirmacaoCheckbox) confirmacaoCheckbox.checked = false; // Limpar checkbox
        
        openModal(modalExcluirCatador);
    }
    
    // Event listeners para os botões de exclusão
    excluirCatadorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            const catadorData = {
                nome: row.getAttribute('data-catador-nome'),
                email: row.getAttribute('data-catador-email')
            };
            
            openExcluirCatadorModal(catadorData);
        });
    });
    
    // Event listeners para fechar modal de exclusão
    if (modalExcluirCatador) {
        if (excluirCloseBtn) {
            excluirCloseBtn.addEventListener('click', () => closeModal(modalExcluirCatador));
        }
        
        // Fechar modal ao clicar no fundo
        modalExcluirCatador.addEventListener('click', function(e) {
            if (e.target.id === 'modal-excluir-catador') {
                closeModal(modalExcluirCatador);
            }
        });
    }

    const checkModalErrors = () => {
        if (editModal && editModal.querySelector('.errorlist, .is-invalid')) {
            openModal(editModal);
        }
        if (modalAprovarCatador && modalAprovarCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalAprovarCatador);
        }
        if (modalAlterarCatador && modalAlterarCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalAlterarCatador);
        }
        if (modalExcluirCatador && modalExcluirCatador.querySelector('.errorlist, .is-invalid')) {
            openModal(modalExcluirCatador);
        }
    };
    checkModalErrors();
});
