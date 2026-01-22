document.addEventListener('DOMContentLoaded', function() {
    const modalResponderContestacao = document.getElementById('modal-responder-contest-pgto-coop');
    const btnConfirmarPgto = document.querySelectorAll('button.responder-contestacao-preco-coop-btn');

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    if (modalResponderContestacao) {
        const closeBtn = modalResponderContestacao.querySelector('#close-btn');
        const cancelBtn = modalResponderContestacao.querySelector('#cancel-btn');
        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });
    }

    btnConfirmarPgto.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(modalResponderContestacao);
        });
    }); 

    const opcoesContestacao = document.querySelectorAll('#opcoes-contestacao input[type="radio"]');
    const camposContestar = document.querySelector('#contestar-pgto');
    const campoJustificativa = document.querySelector('#contestar-pgto [name="justificativa"]');

    opcoesContestacao.forEach(opcao => {
        opcao.addEventListener('change', (e) => {
            const selectedValue = e.target.value;

            if (selectedValue == 'contestar') {
                camposContestar.classList.remove('hidden');
                campoJustificativa.required = true;

            }
            else {
                camposContestar.classList.add('hidden');      
                campoJustificativa.required = false;
            }
        });
    })
});