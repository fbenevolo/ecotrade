document.addEventListener('DOMContentLoaded', function () {
    
    /* Modais */
    const desativarContaModal = document.getElementById('modal-desativar-conta');
    const ativarContaModal = document.getElementById('modal-aprovar-usuario');
    
    /* Botões de ativação */
    const desativarContaBtns = document.querySelectorAll('.modal-desativar-conta-btn');
    const ativarContaBtns = document.querySelectorAll('.ativar-conta-btn');

    const closeModal = (modal) => { if (modal) modal.classList.add('hidden'); };
    const openModal = (modal) => { if (modal) modal.classList.remove('hidden'); };


    /* Lógica de fechamento de Modais */
    if (desativarContaModal) {
        var cancelBtn = desativarContaModal.querySelector('.close-desativar-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(desativarContaModal); })
    }
    if (ativarContaModal) {
        var cancelBtn = ativarContaModal.querySelector('.cancel-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(ativarContaModal); })
    }

    /* Preenchimento dinâmico de informações do form Aprovar Usuario */
    function preencheInfoAprovacaoUsuario(email, nome, statusAtual) {
        const emailDisplay = ativarContaModal.querySelector('#nome-display');
        const nomeDisplay = ativarContaModal.querySelector('#email-display');
        const statusDisplay = ativarContaModal.querySelector('#status-display');

        emailDisplay.innerHTML = email;
        nomeDisplay.innerHTML = nome;
        statusDisplay.innerHTML = statusAtual;
    }

    /* Lógica de abertura de modais */
    desativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(desativarContaModal);
        });
    });

    ativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const btn = e.target.closest('button');
            const email = btn.getAttribute('data-usuario-email');
            const nome = btn.getAttribute('data-usuario-nome');
            const statusAtual = btn.getAttribute('data-usuario-status');
            preencheInfoAprovacaoUsuario(email, nome, statusAtual)

            openModal(ativarContaModal);
        });
    });
});