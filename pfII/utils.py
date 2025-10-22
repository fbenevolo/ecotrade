from .models import Usuario, Negociacao, Demanda, Producao, NegociacaoPagaTrabalho
from typing import List

def get_rendimento_total_catador(usuario: Usuario, negociacoes: List[Negociacao]):
    """
    Calcula o rendimento total do catador
    """
    if usuario.tipo_usuario != 'CA':
        raise Exception('Usuário diferente de catador')
    
    total_pago = 0
    negociacoes_participantes = list()
    for negociacao in negociacoes:
        n_paga_t = NegociacaoPagaTrabalho.objects.filter(id_negociacao=negociacao)
        recebido = negociacao.preco * n_paga_t.quantidade
        total_pago += recebido

    return total_pago 


def calcular_preco_sugerido(id_residuo):
    return


def seleciona_producoes(id_demanda):
    '''
    Seleciona catadores e suas produções para uma negociação.
    Retorna um dicionário no formato <objeto-producao>: quantidade_selecionada
    '''
    demanda = Demanda.objects.get(pk=id_demanda)
    residuo = demanda.id_residuo.tipo
    producoes_residuo = Producao.objects.filter(id_residuo=residuo).order_by('-data')

    selecao_producoes = {}

    qtd_demanda_restante = demanda.quantidade
    for producao in producoes_residuo:
        if qtd_demanda_restante <= 0:
            break 
        
        qtd_produzida = producao.producao
        if qtd_produzida <= qtd_demanda_restante:
            selecao = qtd_produzida
        else:
            selecao = qtd_produzida - qtd_demanda_restante

        selecao_producoes[producao] = selecao
        qtd_demanda_restante -= selecao

    return selecao_producoes


def calcula_valor_a_receber(id_negociacao, lista_producoes_catadores):
    '''
    Calcula o valor individual que cada catador deve receber
    da negociação.
    '''
    negociacao = Negociacao.objects.get(pk=id_negociacao)
    valores_a_receber = []
    for (_, qtd) in lista_producoes_catadores.items():
        a_receber = qtd * negociacao.preco
        valores_a_receber.append(a_receber)

    return valores_a_receber
