document.addEventListener('DOMContentLoaded', function () {
    const confirmarEntregaModal = document.getElementById('confirmar-entrega-modal');
    const confirmarEntregaBtn = document.querySelectorAll('button.confirmar-entrega-btn');
    
    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    if (confirmarEntregaModal) {
        const cancelBtn = document.getElementById('cancel-btn');
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal(confirmarEntregaModal);
        })
    }

    function openConfirmarColetaModal(idNegociacao) {
        const hiddenIdNegociacao = confirmarEntregaModal.querySelector('input[name="id_negociacao"]');
        hiddenIdNegociacao.value = idNegociacao;
        openModal(confirmarEntregaModal);
    }

    confirmarEntregaBtn.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const btn = e.currentTarget.closest('button');
            const idNegociacao = btn.getAttribute('data-id-negociacao');

            openConfirmarColetaModal(idNegociacao);
        });

    });
});