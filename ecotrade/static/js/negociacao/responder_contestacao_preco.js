document.addEventListener('DOMContentLoaded', function() {
    const modalResponderContestacao = document.getElementById('modal-responder-contestacao');
    const modalConfirmarPreco = document.getElementById('modal-confirmar-preco');
    const aceitarContestacaoBtn = document.querySelector('button.aceitar-contestacao-btn');
    const contestarPrecoBtn = document.querySelector('button.contestar-preco-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    if (modalResponderContestacao) {
        const closeContestarBtn = modalResponderContestacao ? modalResponderContestacao.querySelector('#close-btn') : null;
        closeContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalResponderContestacao);
        });

        const cancelContestarBtn = modalResponderContestacao ? modalResponderContestacao.querySelector('#cancel-btn') : null;
        cancelContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalResponderContestacao);
        });
    }

     if (modalConfirmarPreco) {
        const cancelContestarBtn = modalConfirmarPreco ? modalConfirmarPreco.querySelector('#cancel-btn') : null;
        cancelContestarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(modalConfirmarPreco);
        });
    }


    function openModalContestar(modal, contestacaoId, negociacaoId, precoSugerido, acao, tipoUsuario) {
        const hiddenContestacaoIdInput = modal.querySelector('input[name="id_contestacao"]');
        const hiddenNegociacaoIdInput = modal.querySelector('input[name="id_negociacao"]');
        const hiddenOpcoesInput = modal.querySelector('input[name="opcoes"]');
        const hiddenTipoUsuarioInput = modal.querySelector('input[name="tipo_usuario"]');
        const spanPrecoSugerido = modalResponderContestacao.querySelector('#span-preco-sugerido');


        const hiddenActionInput = modal.querySelector('input[name="action"]');
        console.log(hiddenActionInput);

        if (hiddenContestacaoIdInput) hiddenContestacaoIdInput.value = contestacaoId;
        if (hiddenNegociacaoIdInput) hiddenNegociacaoIdInput.value = negociacaoId;
        if (spanPrecoSugerido) spanPrecoSugerido.innerHTML = precoSugerido;
        if (hiddenOpcoesInput) hiddenOpcoesInput.value = acao; 
        if (hiddenTipoUsuarioInput) hiddenTipoUsuarioInput.value = tipoUsuario;

        openModal(modal);
    }

    function openModalAceitar(contestacaoId, negociacaoId, novoPreco) {
        const hiddenContestacaoId = modalConfirmarPreco.querySelector('input[name="id_contestacao"]');
        const hiddenNegociacaoId = modalConfirmarPreco.querySelector('input[name="id_negociacao"]');
        const hiddenPrecoProposto = modalConfirmarPreco.querySelector('input[name="novo_preco"]');

            
        const spanNovoPreco = modalConfirmarPreco.querySelector('#span-preco-sugerido');
        
        if (hiddenContestacaoId) hiddenContestacaoId.value = contestacaoId;
        if (hiddenNegociacaoId) hiddenNegociacaoId.value = negociacaoId;
        if (hiddenPrecoProposto) hiddenPrecoProposto.value = novoPreco;
        if (spanNovoPreco) spanNovoPreco.innerHTML = 'R$' + novoPreco;
        
        openModal(modalConfirmarPreco);
    }

    contestarPrecoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let btn = e.currentTarget;
        let contestacaoId = btn.getAttribute('data-contestacao-id');
        let negociacaoId = btn.getAttribute('data-negociacao-id');
        let tipoUsuario = btn.getAttribute('data-tipo-usuario');
        let precoSugerido = btn.getAttribute('data-preco-sugerido');
        openModalContestar(modalResponderContestacao, contestacaoId, negociacaoId, precoSugerido, 'contestar', tipoUsuario);
    });

    aceitarContestacaoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        let btn = e.currentTarget.closest('button');
        let contestacaoId = btn.getAttribute('data-contestacao-id');
        let negociacaoId = btn.getAttribute('data-negociacao-id')
        let precoSugerido = btn.getAttribute('data-preco-sugerido');

        openModalAceitar(contestacaoId, negociacaoId, precoSugerido);

    });


});