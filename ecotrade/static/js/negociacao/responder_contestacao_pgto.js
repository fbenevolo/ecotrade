document.addEventListener('DOMContentLoaded', function() {
    const modalResponderContestacao = document.getElementById('modal-responder-contestacao-pgto')
    const btnResponderContestacaoPgtoModal = document.querySelectorAll('button.responder-contestacao-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };
    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalResponderContestacao) {
        const closeContestarBtn = modalResponderContestacao.querySelector('#close-btn');
        const cancelContestarBtn = modalResponderContestacao.querySelector('#cancel-btn');

        closeContestarBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });
        cancelContestarBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });
    }

    btnResponderContestacaoPgtoModal.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();            
            openModal(modalResponderContestacao);

        });
    })
});