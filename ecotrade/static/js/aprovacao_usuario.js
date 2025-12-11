document.addEventListener('DOMContentLoaded', function () {
    const ativarUsuarioModal = document.querySelector('#modal-aprovar-usuario')
    const ativarContaBtns = document.querySelectorAll('#ativar-conta-btn');
    const deactivateButton = document.querySelector('#deactivate-button');
    const deactivateModal = document.querySelector('#deactivate-modal');
    const cancelButton = document.querySelector('#cancel-button');
    const deleteButton = document.querySelector('#delete-button');
    const deleteModal = document.querySelector('#delete-modal');
    const cancelDeleteButton = document.querySelector('#cancel-delete-button');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (ativarUsuarioModal) {
        const closeBtn = ativarUsuarioModal.querySelector('#modal-aprovar-close-btn');
        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(ativarUsuarioModal); });
        
        const cancelBtn = ativarUsuarioModal.querySelector('#modal-aprovar-cancel-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(ativarUsuarioModal); });
    }

    function openAtivarUsuarioModal(usuarioId, usuarioNome, statusAtual) {
        const usuarioIdHiddenInput = ativarUsuarioModal.querySelector('input[name="usuario_id"]');
        const emailDisplay = ativarUsuarioModal.querySelector('#nome-display');
        const nomeDisplay = ativarUsuarioModal.querySelector('#email-display');
        const statusDisplay = ativarUsuarioModal.querySelector('#status-display');

        usuarioIdHiddenInput.value = usuarioId;
        emailDisplay.innerHTML = usuarioId;
        nomeDisplay.innerHTML = usuarioNome;
        statusDisplay.innerHTML = statusAtual;  
        
        openModal(ativarUsuarioModal)
    }

    ativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const btn = e.currentTarget.closest('button');
            const usuarioId = btn.getAttribute('data-usuario-email');
            const usuarioNome = btn.getAttribute('data-usuario-nome');
            const statusAtual = btn.getAttribute('data-usuario-status');
            openAtivarUsuarioModal(usuarioId, usuarioNome, statusAtual);
        })
    });

    if (deactivateButton) {
        deactivateButton.addEventListener('click', () => {
            deactivateModal.classList.remove('hidden');
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            deactivateModal.classList.add('hidden');
        });
    }

    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            deleteModal.classList.remove('hidden');
        });
    }

    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', () => {
            deleteModal.classList.add('hidden');
        });
    }
});
