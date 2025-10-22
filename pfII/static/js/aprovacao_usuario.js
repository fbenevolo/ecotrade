document.addEventListener('DOMContentLoaded', function () {
    const deactivateButton = document.querySelector('#deactivate-button');
    const deactivateModal = document.querySelector('#deactivate-modal');
    const cancelButton = document.querySelector('#cancel-button');
    const deleteButton = document.querySelector('#delete-button');
    const deleteModal = document.querySelector('#delete-modal');
    const cancelDeleteButton = document.querySelector('#cancel-delete-button');
    // const demandButton = document.querySelector('#demand-button');
    // const demandModal = document.querySelector('#demand-modal');
    // const cancelDemandButton = document.querySelector('#cancel-demand-button');

    if (deactivateButton) {
        deactivateButton.addEventListener('click', () => {
            deactivateModal.classList.remove('hidden');
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            deactivateModal.classList.add('hidden');
        });
    }

    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            deleteModal.classList.remove('hidden');
        });
    }

    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', () => {
            deleteModal.classList.add('hidden');
        });
    }

    // if (demandButton) {
    //     demandButton.addEventListener('click', () => {
    //         demandModal.classList.remove('hidden');
    //     });
    // }

    // if (cancelDemandButton) {
    //     cancelDemandButton.addEventListener('click', () => {
    //         demandModal.classList.add('hidden');
    //     });
    // }
});
