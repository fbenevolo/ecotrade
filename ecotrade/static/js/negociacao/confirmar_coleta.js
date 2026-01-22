document.addEventListener('DOMContentLoaded', function () {
    const confirmarColetaModal = document.getElementById('confirmar-coleta-modal');
    const confirmarColetaBtn = document.querySelectorAll('button.confirmar-coleta-btn');

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    if (confirmarColetaModal) {
        const cancelBtn = document.getElementById('cancel-btn');
        cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(confirmarColetaModal); });
    }

    confirmarColetaBtn.forEach(btn => {
        btn.addEventListener('click', (e) => { e.preventDefault(); openModal(confirmarColetaModal); });
    });
});