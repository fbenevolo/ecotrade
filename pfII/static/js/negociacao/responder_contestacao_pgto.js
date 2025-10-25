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
        closeContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalResponderContestacao);
        });

        const cancelContestarBtn = modalResponderContestacao.querySelector('#cancel-btn');
        cancelContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalResponderContestacao);
        });
    }

    function openResponderModal(idNegociacao, idContestacao) {
        const hiddenIdNegociacaoInput = modalResponderContestacao.querySelector('input[name="id_negociacao"]');
        const hiddenIdContestacaoInput = modalResponderContestacao.querySelector('input[name="id_contestacao"]');

        if (hiddenIdNegociacaoInput) hiddenIdNegociacaoInput.value = idNegociacao;
        if (hiddenIdContestacaoInput) hiddenIdContestacaoInput.value = idContestacao;
        openModal(modalResponderContestacao);

    }

    btnResponderContestacaoPgtoModal.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();

            const btn = e.currentTarget.closest('button');   
            idNegociacao = btn.getAttribute('data-id-negociacao');
            idContestacao = btn.getAttribute('data-id-contestacao');

            openResponderModal(idNegociacao, idContestacao);
        });
    })
});