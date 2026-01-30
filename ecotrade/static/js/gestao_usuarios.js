document.addEventListener('DOMContentLoaded', function () {
    
    /* Modais */
    const desativarContaModal = document.getElementById('modal-desativar-conta');
    const ativarContaModal = document.getElementById('modal-aprovar-usuario');
    const reativarContaModal = document.getElementById('modal-reativar-conta')

    /* Botões de ativação */
    const desativarContaBtns = document.querySelectorAll('.modal-desativar-conta-btn');
    const ativarContaBtns = document.querySelectorAll('.ativar-conta-btn');
    const reativarContaBtns = document.querySelectorAll('.reativar-conta-btn');

    const closeModal = (modal) => { if (modal) modal.classList.add('hidden'); };
    const openModal = (modal) => { if (modal) modal.classList.remove('hidden'); };


    /* Lógica de fechamento de Modais */
    if (desativarContaModal) {
        var cancelBtn = desativarContaModal.querySelector('.close-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(desativarContaModal); })
    }

    if (ativarContaModal) {
        var cancelBtn = ativarContaModal.querySelector('.cancel-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(ativarContaModal); })

        var closeBtn = ativarContaModal.querySelector('.close-btn');
        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(ativarContaModal); });
    }

    /* Preenchimento dinâmico de informações do form Aprovar Usuario */
    function preencheInfoAprovacaoUsuario(email, nome, statusAtual) {
        var emailDisplay = ativarContaModal.querySelector('#nome-display');
        const nomeDisplay = ativarContaModal.querySelector('#email-display');
        const statusDisplay = ativarContaModal.querySelector('#status-display');

        emailDisplay.innerHTML = email;
        nomeDisplay.innerHTML = nome;
        statusDisplay.innerHTML = statusAtual;
    }

    /* Preenchimento dinâmico de email no modal Desativar Usuario */
    function preencherEmailDesativarUsuario(email) {
        const emailDisplay = desativarContaModal.querySelector('#email-display'); 
        emailDisplay.innerHTML = email
    }

    /* Lógica de abertura de modais */
    desativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            var btn = e.target.closest('button');
            var email = btn.getAttribute('data-usuario-email');
            preencherEmailDesativarUsuario(email);
            openModal(desativarContaModal);
        });
    });

    ativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            var btn = e.target.closest('button');
            var email = btn.getAttribute('data-usuario-email');
            const nome = btn.getAttribute('data-usuario-nome');
            const statusAtual = btn.getAttribute('data-usuario-status');
            preencheInfoAprovacaoUsuario(email, nome, statusAtual)

            openModal(ativarContaModal);
        });
    });

    reativarContaBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(reativarContaModal);
        });
    });
});