document.addEventListener('DOMContentLoaded', function() {
    const modalResponderContestacao = document.getElementById('modal-responder-contest-preco');
    const responderContestacaobtns = document.querySelectorAll('button.responder-contest-preco-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };
    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalResponderContestacao) {
        const closeBtn = modalResponderContestacao.querySelector('button.close-btn');
        const cancelBtn = modalResponderContestacao.querySelector('button.cancel-btn');
        closeBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(modalResponderContestacao); });

    }

    responderContestacaobtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(modalResponderContestacao);
        });
    });

    const opcoesContestacao = document.querySelectorAll('#opcoes-contestacao input[type="radio"]');
    const camposContestar = document.querySelector('#contestar-preco');
    
    const campoJustificativa = document.querySelector('[name="justificativa"]');
    const campoPreco = document.querySelector('[name="preco_proposto"]');
    
    opcoesContestacao.forEach(opcao => {
        opcao.addEventListener('change', (e) => {
            const selectedValue = e.target.value;
    
            if (selectedValue == 'contestar') {
                camposContestar.classList.remove('hidden');
                campoJustificativa.required = true;
                campoPreco.required = true;
            }
            else {
                camposContestar.classList.add('hidden');      
                campoJustificativa.required = false;
                campoPreco.required = false;      
            }
        });
    })


});