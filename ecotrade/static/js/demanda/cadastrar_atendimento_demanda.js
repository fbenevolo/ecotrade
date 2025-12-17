document.addEventListener('DOMContentLoaded', function () {
    const cadastrarAtendimentoModal = document.getElementById('modal-cadastrar-atendimento-demanda');
    const openModalBtns = document.querySelectorAll('button.negociar-btn');

    const closeModal = (modal) => {
        if (modal) modal.classList.add('hidden');
    };

    const openModal = (modal) => {
        if (modal) modal.classList.remove('hidden');
    };

    const formatarDataParaBR = (dataString) => {
        const partes = dataString.split('-'); // ["YYYY", "MM", "DD"]
        if (partes.length === 3) {
            const [ano, mes, dia] = partes;
            // Retorna no formato brasileiro DD-MM-YYYY
            return `${dia}-${mes}-${ano}`;
        }
        return dataString; // Retorna o original se o formato for inesperado
    }

    function openCadastrarAtendimentoModal(producoesSelecionadas, demandaData) {
        if (!cadastrarAtendimentoModal) return;
        
        // substituindo o placeholder 0 pelo id da demanda a ser atendida
        const cadastrarAtendimentoForm = cadastrarAtendimentoModal.querySelector('#cadastrar-atendimento-form');
        let actionUrl = cadastrarAtendimentoForm.getAttribute('action');
        actionUrl = actionUrl.replace('0', `${demandaData.idDemanda}`);
        cadastrarAtendimentoForm.setAttribute('action', actionUrl);
        
        // Elementos visuais
        const confirmTextResiduo = cadastrarAtendimentoModal.querySelector('#confirm-residuo');
        const confirmTextQuantidade = cadastrarAtendimentoModal.querySelector('#confirm-quantidade');        
        confirmTextResiduo.textContent = demandaData.residuo;
        confirmTextQuantidade.textContent = demandaData.quantidade + " kg";

        const precoSugeridoDisplay = cadastrarAtendimentoModal.querySelector('#preco-sugerido-display');
        precoSugeridoDisplay.textContent = 'R$ ' + producoesSelecionadas.preco_sugerido.toFixed(2);
        if (producoesSelecionadas.preco_sugerido && precoSugeridoDisplay) {
            // Formata o valor com 2 casas decimais e prefixo R$
            precoSugeridoDisplay.textContent = 'R$ ' + producoesSelecionadas.preco_sugerido.toFixed(2);
        } else if (precoSugeridoDisplay) {
            // Se o preço for nulo ou zero, exibe uma mensagem
            precoSugeridoDisplay.textContent = 'Não há sugestão de preço para esta negociação';
        }

        const producoesGridBody = cadastrarAtendimentoModal.querySelector('#catadores-grid-container');
        renderCatadoresElegiveisGrid(producoesSelecionadas.producoes, producoesGridBody);

        openModal(cadastrarAtendimentoModal);
    }
    

    async function loadProducoesSelecionadas(idDemanda) {
        /* 
        Esta função acessa um endpoint no qual ela obtém acesso às produções que são elegíveis para uma negociação
        */
        const ajaxUrl = `/api/demanda/preparar/${idDemanda}/`; 
        return fetch(ajaxUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status} ao carregar produções demanda ${idDemanda}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    return data;
                } else {
                    console.log('Erro ao carregar dados: ' + data.error);
                }
            })
            .catch(error => {
                console.error("Erro de rede ao buscar dados:", error);
                console.log('Ocorreu um erro de conexão ao tentar negociar.');
            });
    }

    function renderCatadoresElegiveisGrid(producoes, containerElement) {
        /* 
        Renderiza um grid com as produções/catadores elegíveis para a negociação 
        */
        
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

    if (cadastrarAtendimentoModal) {
        const closeModalBtn = document.getElementById('modal-close-btn');
        const cancelModalBtn = document.getElementById('modal-cancel-btn');
        closeModalBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(cadastrarAtendimentoModal) });
        cancelModalBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(cadastrarAtendimentoModal) });
    }
    
    openModalBtns.forEach(button => {
         button.addEventListener('click', async function (e) {
            e.preventDefault();
            const row = e.currentTarget.closest('tr');
            
            // Coleta os dados estáticos da linha (para preencher displays e hidden inputs)
            const idDemanda = row.getAttribute('data-id-demanda');
            const residuo = row.getAttribute('data-residuo');
            const quantidade = row.getAttribute('data-quantidade');

            // Armazena os dados estáticos globalmente
            const demandaData = { idDemanda: idDemanda, residuo: residuo, quantidade: quantidade };
                
            const producoesSelecionadas = await loadProducoesSelecionadas(idDemanda);
            openCadastrarAtendimentoModal(producoesSelecionadas, demandaData); 

        });
    });

});