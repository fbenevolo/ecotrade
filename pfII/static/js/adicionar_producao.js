document.addEventListener('DOMContentLoaded', function () {
    const modalAdicionarProducao = document.getElementById('modal-adicionar-producao');
    const openAdicionarBtn = document.getElementById('adicionar-producao-btn');
    const adicionarCloseBtn = document.getElementById('modal-close-btn');
    const adicionarCancelBtn = document.getElementById('modal-cancel-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalAdicionarProducao) {
        openAdicionarBtn.addEventListener('click', (e) => { e.preventDefault(); openModal(modalAdicionarProducao)});
        adicionarCloseBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalAdicionarProducao)});
        adicionarCancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalAdicionarProducao)});
    }

    openAdicionarBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal(modalAdicionarProducao);
    })
});