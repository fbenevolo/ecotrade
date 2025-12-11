document.addEventListener('DOMContentLoaded', function () {
    const modalCadastrarAtendimentoDemanda = document.getElementById('modal-cadastrar-atendimento-demanda');
    const openModalBtns = document.querySelectorAll('button.negociar-btn');
    const closeModalBtn = document.getElementById('modal-close-btn');
    const cancelModalBtn = document.getElementById('modal-cancel-btn');

    // Elementos de Display Dinâmico (Ajuste este ID para o local onde o preço sugerido aparece)
    const precoSugeridoDisplay = modalCadastrarAtendimentoDemanda ? modalCadastrarAtendimentoDemanda.querySelector('#preco-sugerido-display') : null;
    const producoesGridBody = modalCadastrarAtendimentoDemanda ? modalCadastrarAtendimentoDemanda.querySelector('#catadores-grid-container') : null; // Assumindo este ID

    // Variáveis que persistem entre o AJAX e a abertura
    let currentDemandaData = {}; 

    // Funções genéricas de modal
    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    // =========================================================
    // I. FUNÇÃO PRINCIPAL DE ABERTURA (Agora recebe os dados do AJAX)
    // =========================================================

    function openCadastrarAtendimentoModal(data) {
        if (!modalCadastrarAtendimentoDemanda) return;
        
        // Campos que o formulário submeterá
        const hiddenCooperativaIdInput = modalCadastrarAtendimentoDemanda.querySelector('input[name="id_cooperativa"]');
        const hiddenResiduoIdInput = modalCadastrarAtendimentoDemanda.querySelector('input[name="id_residuo"]');
        const hiddenDemandaIdInput = modalCadastrarAtendimentoDemanda.querySelector('input[name="id_demanda"]');
        
        // Elementos visuais
        const confirmTextResiduo = modalCadastrarAtendimentoDemanda.querySelector('#confirm-residuo');
        const confirmTextQuantidade = modalCadastrarAtendimentoDemanda.querySelector('#confirm-quantidade');
    
        // 1. Injeta os IDs e Quantidade nos campos ocultos e displays
        if (hiddenCooperativaIdInput) hiddenCooperativaIdInput.value = currentDemandaData.cooperativaId;
        if (hiddenResiduoIdInput) hiddenResiduoIdInput.value = currentDemandaData.residuoId;
        if (hiddenDemandaIdInput) hiddenDemandaIdInput.value = currentDemandaData.demandaId;
        
        if (confirmTextResiduo) confirmTextResiduo.textContent = currentDemandaData.residuoTexto;
        if (confirmTextQuantidade) confirmTextQuantidade.textContent = currentDemandaData.quantidade + " kg";

        // 2. Injeta os dados do AJAX
        if (data.preco_sugerido && precoSugeridoDisplay) {
            // Formata o valor com 2 casas decimais e prefixo R$
            precoSugeridoDisplay.textContent = 'R$ ' + data.preco_sugerido.toFixed(2);
        } else if (precoSugeridoDisplay) {
            // Se o preço for nulo ou zero, exibe uma mensagem
            precoSugeridoDisplay.textContent = 'Não há sugestão de preço para esta negociação';
        }

        if (data.producoes && producoesGridBody) {
            // 3. Renderiza a tabela de catadores elegíveis
            renderProducoesGrid(data.producoes, producoesGridBody, data.preco_sugerido);
        }

        openModal(modalCadastrarAtendimentoDemanda);
    }
    
    // =========================================================
    // II. FUNÇÃO DE CHAMADA AJAX (NOVA)
    // =========================================================

    function loadDataAndOpenModal(demandaId) {
        // Obtenha a URL do endpoint AJAX (Ajuste o caminho se necessário)
        const ajaxUrl = `/api/demanda/preparar/${demandaId}/`; 
        fetch(ajaxUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Chama a função principal para preencher e abrir o modal
                    openCadastrarAtendimentoModal(data); 
                } else {
                    alert('Erro ao carregar dados: ' + data.error);
                }
            })
            .catch(error => {
                console.error("Erro de rede ao buscar dados:", error);
                alert('Ocorreu um erro de conexão ao tentar negociar.');
            });
    }

    const formatarDataParaBR = (dataString) => {
        const partes = dataString.split('-'); // ["YYYY", "MM", "DD"]
        if (partes.length === 3) {
            const [ano, mes, dia] = partes;
            // Retorna no formato brasileiro DD-MM-YYYY
            return `${dia}-${mes}-${ano}`;
        }
        return dataString; // Retorna o original se o formato for inesperado
    }



    // Esta função é vital e você deve implementá-la em seu JS
    function renderProducoesGrid(producoes, containerElement, precoSugerido) {
        // Limpa o conteúdo anterior e o placeholder "Carregando..."
        containerElement.innerHTML = ''; 

        if (producoes.length === 0) {
            containerElement.innerHTML = `<div class="p-4 text-center text-gray-500">Nenhum catador elegível encontrado.</div>`;
            return;
        }
        producoes.forEach(p => {
            // O cálculo agora usa os dados reais do JSON
            const gridItem = document.createElement('div');
            gridItem.className = 'grid grid-cols-3 gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50';
            
            gridItem.innerHTML = `
                <div class="flex items-center">
                    <span class="material-symbols-outlined mr-3 text-primary">person</span>
                    <span class="font-medium text-gray-800 dark:text-gray-200">${p.catador}</span>
                </div>
                <div class="text-right font-semibold text-gray-800 dark:text-white">${p.quantidade} kg</div>
                <div class="text-right font-semibold text-gray-800 dark:text-white">${formatarDataParaBR(p.data)}</div>
            `;
            containerElement.appendChild(gridItem);
        });
    }

    // =========================================================
    // IV. LISTENER DE CLIQUE (AGORA CHAMA O AJAX)
    // =========================================================

    if (modalCadastrarAtendimentoDemanda) {
        // Listener de Fechamento (Mantido)
        closeModalBtn.addEventListener('click', () => closeModal(modalCadastrarAtendimentoDemanda));
        cancelModalBtn.addEventListener('click', () => closeModal(modalCadastrarAtendimentoDemanda));
        
        modalCadastrarAtendimentoDemanda.addEventListener('click', function (e) {
            if (e.target.id === 'modal-cadastrar-atendimento-demanda') { // Corrigido ID de fechamento
                closeModal(modalCadastrarAtendimentoDemanda);
            }
        });
    }
    
    openModalBtns.forEach(button => {
         button.addEventListener('click', function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            // Coleta os dados estáticos da linha (para preencher displays e hidden inputs)
            const demandaId = row.getAttribute('data-demanda-id');
            const cooperativaId = row.getAttribute('data-cooperativa-id');
            const residuoId = row.getAttribute('data-residuo-id');
            const residuoTexto = row.getAttribute('data-residuo-texto');
            const quantidade = row.getAttribute('data-quantidade');

            if (demandaId) {
                // Armazena os dados estáticos globalmente
                currentDemandaData = { demandaId, cooperativaId, residuoId, residuoTexto, quantidade };
                
                // Inicia o fluxo AJAX
                loadDataAndOpenModal(demandaId);
            }
        });
    });

});