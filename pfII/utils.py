from .models import Usuario, Negociacao, Demanda, Residuo, Producao, NegociacaoPagaTrabalho
from typing import List
from django.utils import timezone
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def get_rendimento_total_catador(usuario: Usuario, negociacoes: List[Negociacao]):
    """
    Calcula o rendimento total do catador
    """
    if usuario.tipo_usuario != 'CA':
        raise Exception('Usuário diferente de catador')
    
    total_pago = 0
    for negociacao in negociacoes:
        n_paga_t = NegociacaoPagaTrabalho.objects.filter(id_negociacao=negociacao)
        recebido = negociacao.preco * n_paga_t.quantidade
        total_pago += recebido

    return total_pago 


def seleciona_producoes(id_demanda):
    '''
    Seleciona catadores e suas produções para uma negociação.
    
    '''
    demanda = Demanda.objects.get(pk=id_demanda)
    residuo = demanda.id_residuo.tipo
    producoes_residuo = Producao.objects.filter(id_residuo=residuo, status='l').order_by('data')

    selecao_producoes = {}

    qtd_demanda_restante = demanda.quantidade
    for producao in producoes_residuo:
        if qtd_demanda_restante <= 0:
            break     
        
        qtd_produzida = producao.producao
        if qtd_produzida <= qtd_demanda_restante:
            qtd_selecionada = qtd_produzida
        else:
            qtd_selecionada = qtd_produzida - (qtd_produzida - qtd_demanda_restante)

        selecao_producoes[producao] = qtd_selecionada
        qtd_demanda_restante -= qtd_selecionada


    return selecao_producoes


def calcula_valor_a_receber(id_negociacao, lista_producoes_catadores):
    '''
    Calcula o valor individual que cada catador deve receber
    da negociação.
    '''
    negociacao = Negociacao.objects.get(pk=id_negociacao)
    valores_a_receber = []
    for obj in lista_producoes_catadores:
        a_receber = obj.quantidade * negociacao.preco
        valores_a_receber.append(a_receber)

    return valores_a_receber


def atualiza_producoes(id_negociacao):
    '''
    Atualiza a tabela Producao, diminuindo as quantidades que foram selecionadas em NegociacaoPagaTrabalho
    para uma determinada negociação
    '''
    negociacao = Negociacao.objects.get(pk=id_negociacao)
    n_paga_t = NegociacaoPagaTrabalho.objects.filter(id_negociacao=negociacao)

    # para cada produção,cria um objeto NegociacaoPagaTrabalho e desconta a quantidade selecionada das produçõess
    for n in n_paga_t:
        producao = Producao.objects.get(pk=n.id_producao.pk)
        producao.producao -= n.quantidade

        # se toda a produção foi utilizada, deleta o objeto do banco
        if producao.producao == 0:
            producao.status = 'z'
        else:
            producao.status = 'l'
        
        producao.id_negociacao = None
        producao.save()

def atualiza_preco_medio_residuo(id_residuo):
    '''
    Atualiza preço médio de um resíduo
    '''
    residuo = Residuo.objects.get(pk=id_residuo)
    # todas as negociacoes em que aquele residuo foi negociado nos ultimos três meses
    three_months_ago_approx = timezone.now() - timedelta(days=90) # aproximação, pode errar em alguns dias
    negociacoes_residuo = Negociacao.objects.filter(id_residuo=residuo, 
                                                    status='C',
                                                    data_conclusao__gte=three_months_ago_approx)
    if len(negociacoes_residuo):
        total = 0
        for negociacao in negociacoes_residuo:
            total += negociacao.preco
        media = total / len(negociacoes_residuo)
        residuo.preco_medio = media

    residuo.save()


def enviar_email_template(destinatario_email: str, template_name: str, subject: str, 
                          context: dict = None, from_email: str = None) -> int:
    """
    Envia um e-mail HTML dinâmico usando um template do Django.
    """
    if context is None:
        context = {}

    try:
        template_path = 'email/' + template_name
        html_content = render_to_string(template_path, context)
        plain_content = strip_tags(html_content)
        remetente = from_email if from_email else settings.DEFAULT_FROM_EMAIL
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content, 
            from_email=remetente,
            to=[destinatario_email]
        )
        
        msg.attach_alternative(html_content, "text/html")
        return msg.send(fail_silently=False)
        
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destinatario_email}: {e}")
        return 0