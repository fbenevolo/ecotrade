from django import forms
from django.utils import timezone
from ..models import Producao, Negociacao, NegociacaoPagaTrabalho, ContestacaoPreco, ContestacaoPagamento

from ..utils import atualiza_producoes, atualiza_preco_medio_residuo, enviar_email_template

class ConfirmarNegociacaoForm(forms.Form):
    '''
    Classe responsável por fazer a negociação avançar para um dos seguintes estados:
    - 'ACE' (Aguardando Confirmação da Empresa),
        Quando iniciação negociou ou a cooperativa contestou pagamento
    - 'ACC', (Aguardando Confirmação da Segunda Parte),
        Quando a empresa contesta o preço
    - 'AC' (Aguardando Coleta)
        Quando ambas partes confirmam
    - 'C' (Cancelada)
        Quando alguma parte cancela a negociação
    '''
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_negociacao')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    tipo_usuario = forms.CharField(widget=forms.HiddenInput()) 
    opcoes = forms.ChoiceField(
        choices=(
            ('confirmar', 'Confirmar Preço'),
            ('cancelar', 'Cancelar Negociação')
        ),
        widget=forms.HiddenInput()
    )

    def save(self):
        id_negociacao = int(self.cleaned_data['id_negociacao'])
        tipo_usuario = self.cleaned_data['tipo_usuario']
        opcao = self.cleaned_data['opcoes']
        negociacao = Negociacao.objects.get(pk=id_negociacao)

        if opcao == 'cancelar':
            negociacao.status = 'CA'
            # deleta os objetos NegociacaoPagaTrabalho, pois a negociação foi cancelada
            neg_paga_trabalho = NegociacaoPagaTrabalho.objects.filter(id_negociacao=negociacao)
            for obj in neg_paga_trabalho:
                obj.delete()

            # deixar livres as produções alocadas à negociações
            producoes = Producao.objects.filter(id_negociacao=id_negociacao)
            for producao in producoes:
                producao.id_negociacao = None
                producao.status = 'l'
                producao.save()
        elif opcao == 'confirmar':
            if tipo_usuario == 'E':
                if negociacao.status == 'ACE':
                    if negociacao.confirmacao_preco_cooperativa == True:
                        negociacao.confirmacao_preco_empresa = True 
                        negociacao.status = 'AC'
                    else:
                        negociacao.confirmacao_preco_empresa = True 
                        negociacao.status = 'ACC'                    
            else:
                if negociacao.status == 'ACC':
                    if negociacao.confirmacao_preco_empresa == True:
                        negociacao.confirmacao_preco_cooperativa = True
                        negociacao.status = 'AC'
                    else:
                        negociacao.confirmacao_preco_cooperativa = True
                        negociacao.status = 'ACE'
        
        negociacao.save()


class ContestarPrecoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='contestar_preco')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    tipo_usuario = forms.CharField(widget=forms.HiddenInput()) 
    opcoes = forms.ChoiceField(
        choices=(
            ('contestar', 'Contestar Preço'),
        ),
        widget=forms.HiddenInput()
    )
    justificativa = forms.CharField(widget=forms.Textarea())
    novo_preco = forms.FloatField(label='Novo Preço Sugerido', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            style = 'mt-1 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
            self.fields[field].widget.attrs.update({'class': style})

    def save(self):
        negociacao = Negociacao.objects.get(pk=self.cleaned_data['id_negociacao'])
        contestador = self.cleaned_data['tipo_usuario']
        justificativa = self.cleaned_data['justificativa']
        preco_proposto = self.cleaned_data['novo_preco']

        try:
            if contestador == 'E':
                status = 'ACC'
            else:
                status = 'ACE'
            ContestacaoPreco.objects.create(
                id_negociacao=negociacao,
                status=status,
                contestador=contestador,
                justificativa=justificativa,
                preco_proposto=preco_proposto
            )
            negociacao.status = status
            negociacao.save()

            # envia email para as partes
            enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/nova_contestacao_preco.html', 'Contestação de Preço')
            enviar_email_template(negociacao.id_empresa.email, 'negociacao/nova_contestacao_preco.html', 'Contestação de Preço')
        except Exception as e:
            print(f'Erro ao criar contestação de preço: {e}')

class AceitarContestacaoPrecoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='aceitar_contestacao_preco')
    id_contestacao = forms.CharField(widget=forms.HiddenInput())
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    novo_preco = forms.CharField(widget=forms.HiddenInput())

    def save(self):
        id_contestacao = self.cleaned_data['id_contestacao']
        id_negociacao = self.cleaned_data['id_negociacao']
        novo_preco = float(self.cleaned_data['novo_preco'].replace(',', '.'))

        contestacao = ContestacaoPreco.objects.get(pk=id_contestacao)
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        try: 
            # a contestacao foi concluida
            contestacao.status = 'A'
            contestacao.save()
            # mudando preco e status da negociação e confirmando preço em ambas partes
            negociacao.status = 'AC'
            negociacao.preco = novo_preco 
            negociacao.confirmacao_preco_cooperativa = True 
            negociacao.confirmacao_preco_empresa = True
            negociacao.save()

            enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/aceite_contestacao_preco.html', 'Aceite na Contestação de Preço')
            enviar_email_template(negociacao.id_empresa.email, 'negociacao/aceite_contestacao_preco.html', 'Aceite na Contestação de Preço')
        except Exception as e:
            print(f'Erro ao alterar contestação ou negociação: {e}')


class RecusarContestacaoPrecoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='recusar_contestacao_preco')    
    id_contestacao = forms.CharField(widget=forms.HiddenInput())

    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    tipo_usuario = forms.CharField(widget=forms.HiddenInput()) 
    justificativa = forms.CharField(widget=forms.Textarea())
    novo_preco = forms.FloatField(label='Novo Preço Sugerido', required=True)

    opcoes = forms.ChoiceField(
        choices=(
            ('contestar', 'contestar'),    
        ),
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields: # <--- O ERRO PODE ESTAR AQUI
            style = 'mt-1 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
            self.fields[field].widget.attrs.update({'class': style})
    
    def save(self):
        negociacao = Negociacao.objects.get(pk=self.cleaned_data['id_negociacao'])
        contestador = self.cleaned_data['tipo_usuario']
        justificativa = self.cleaned_data['justificativa']
        preco_proposto = self.cleaned_data['novo_preco']
        tipo_usuario = self.cleaned_data['tipo_usuario']

        # fecha a contestação declinada e confirma preço de negociação da parte que abriu a contestação
        id_antiga_contestacao = self.cleaned_data['id_contestacao']
        contestacao_antiga = ContestacaoPreco.objects.get(pk=id_antiga_contestacao)
        if tipo_usuario == 'CO':
            contestacao_antiga.status = 'DC'
            novo_status = 'ACE'
            enviar_email_template(negociacao.id_empresa.email, 'negociacao/recusa_contestacao_preco.html', 'Recusa na Contestação de Preço')
        else:
            contestacao_antiga.status = 'DE'
            novo_status = 'ACC'
            enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/recusa_contestacao_preco.html', 'Recusa na Contestação de Preço')

        contestacao_antiga.save()
        # altera o status da negociação para ser a confirmação da parte que receberá a contestação
        negociacao.status = novo_status
        negociacao.save()

        # abre uma nova contestação
        ContestacaoPreco.objects.create(
            id_negociacao=negociacao,
            status=novo_status,
            contestador=contestador,
            justificativa=justificativa,
            preco_proposto=preco_proposto
        )

        enviar_email_template(negociacao.id_empresa.email, 'negociacao/nova_contestacao_preco.html', 'Recusa na Contestação de Preço')
        enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/nova_contestacao_preco.html', 'Recusa na Contestação de Preço')


class ConfirmarColetaForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_coleta')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = 'mt-1 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
        self.fields['data'].widget.attrs.update({'class': style})

    def save(self):
        id_negociacao = self.cleaned_data['id_negociacao']
        data_coleta = self.cleaned_data['data']

        negociacao = Negociacao.objects.get(pk=id_negociacao)
        negociacao.status = 'ET'
        negociacao.data_coleta = data_coleta
        negociacao.save()

        enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/mudanca_status.html', 
                              'Mudança de Status na Negociação', context={ 'novo_status': 'Em Transporte' })
        enviar_email_template(negociacao.id_empresa.email, 'negociacao/mudanca_status.html', 
                              'Mudança de Status na Negociação', context={ 'novo_status': 'Em Transporte' })


class ConfirmarEntregaForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_entrega')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self):
        id_negociacao = self.cleaned_data['id_negociacao']
        data_entrega = self.cleaned_data['data']
        
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        negociacao.status = 'ACPE'
        negociacao.data_coleta = data_entrega
        negociacao.save()

        enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/mudanca_status.html', 
                              'Mudança de Status na Negociação', context={ 'novo_status': 'Aguardando Confirmação de Pagamento da Empresa' })
        enviar_email_template(negociacao.id_empresa.email, 'negociacao/mudanca_status.html', 
                              'Mudança de Status na Negociação', context={ 'novo_status': 'Aguardando Confirmação de Pagamento da Empresa' })


class ConfirmarPagamentoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_pagamento')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    comprovante = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.tipo_usuario = kwargs.pop('tipo_usuario', None)
        super().__init__(*args, **kwargs)
        # se usuário for cooperativa, não precisa anexar comprovante
        if self.tipo_usuario == 'CO':
            del self.fields['comprovante']
        else: 
            style_comprovante = 'absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10'
            self.fields['comprovante'].widget.attrs.update({'class': style_comprovante})
    
    def save(self):
        id_negociacao = int(self.cleaned_data['id_negociacao'])
        negociacao = Negociacao.objects.get(pk=id_negociacao)

        try:
            if self.tipo_usuario == 'E':
                comprovante = self.cleaned_data['comprovante']
                negociacao.comprovante = comprovante
                negociacao.confirmacao_pgto_empresa = True
                negociacao.status = 'ACPC'
                negociacao.save()

                enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/pagamento_confirmado_empresa.html', 
                                      'Pagamento Confirmado', context={ 'nome_empresa': negociacao.id_empresa.nome })
            else:
                negociacao.confirmacao_pgto_coop = True
                negociacao.data_conclusao = timezone.now()
                negociacao.status = 'C'
                negociacao.save()

                enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')
                enviar_email_template(negociacao.id_empresa.email, 'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')
                
                atualiza_producoes(negociacao.pk)
                atualiza_preco_medio_residuo(negociacao.id_residuo.pk)

        except Exception as e:
            print(f'Erro ao atualizar status de pagamento de negociação: {e}')


class ContestarPagamentoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='contestar_pagamento')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    id_antiga_contestacao = forms.CharField(widget=forms.HiddenInput(), required=False)
    justificativa = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = "w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary"
        self.fields['justificativa'].widget.attrs.update({'class': style})

    def save(self):
        justificativa = self.cleaned_data['justificativa']
        id_negociacao = self.cleaned_data['id_negociacao']
        id_antiga_contestacao = self.cleaned_data['id_antiga_contestacao']

        try:
            # muda status da negociação para 'Pagamento Contestado' (PC)
            negociacao = Negociacao.objects.get(pk=id_negociacao)
            negociacao.status = 'ACPE'
            negociacao.save()

            # se for uma resposta à uma contestação já existente, fecha essa contestação antiga
            if id_antiga_contestacao:
                antiga_contestacao = ContestacaoPagamento.objects.get(pk=id_antiga_contestacao)
                antiga_contestacao.status = 'A'
                antiga_contestacao.save()

            # cria uma contestação de pagamento
            ContestacaoPagamento.objects.create(
                status='EE',
                justificativa=justificativa,
                id_negociacao=negociacao,
                usuario='CO',
            )

            enviar_email_template(negociacao.id_empresa.email, 'negociacao/pagamento_contestado.html',
                                  'Pagamento de Negociação Contestado')

        except Exception as e:
            print(f'Erro ao criar contestação de pagamento: {e}')


class ResponderContestacaoPgtoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='responder_contestar_pagamento')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    id_contestacao = forms.CharField(widget=forms.HiddenInput())
    justificativa = forms.CharField(widget=forms.Textarea())

    comprovante = forms.FileField(  
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer',
                'id': 'id_comprovante',
            }
        ),
        label='Carregar um arquivo' 
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = "w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary"
        self.fields['justificativa'].widget.attrs.update({'class': style})

    def save(self):
        id_negociacao = self.cleaned_data['id_negociacao']
        id_antiga_contestacao = self.cleaned_data['id_contestacao']
        justificativa = self.cleaned_data['justificativa']
        comprovante = self.cleaned_data['comprovante']

        negociacao = Negociacao.objects.get(pk=id_negociacao)

        try:
            # fechando a antiga contestacao
            antiga_contestacao = ContestacaoPagamento.objects.get(pk=id_antiga_contestacao)
            antiga_contestacao.status = 'A'
            antiga_contestacao.save()
            
            # criando nova "contestação", isto é, uma resposta da empresa à antiga contestação com um novo comprovante
            ContestacaoPagamento.objects.create(
                id_negociacao=negociacao,
                justificativa=justificativa,
                comprovante=comprovante,
                status='EE',
                usuario='E'
            )

            enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/resposta_pagamento_contestado.html',
                                  'Resposta à Contestação de Pagamento', context={'nome_empresa': negociacao.id_empresa.nome})

        except Exception as e:
            print(f'Erro ao criar resposta à contestação de pagamento: {e}')


class ConfirmarPagamentoPosContestForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_pgto_pos_contest')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    id_contestacao = forms.CharField(widget=forms.HiddenInput())

    def save(self):
        id_contestacao = self.cleaned_data['id_contestacao']
        id_negociacao = self.cleaned_data['id_negociacao']

        # fechando a contestação
        contestacao = ContestacaoPagamento.objects.get(pk=id_contestacao)
        contestacao.status = 'A'
        contestacao.save()

        # anexando novo comprovante à negociação e concluindo ela
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        negociacao.comprovante = contestacao.comprovante
        negociacao.data_conclusao = timezone.now()
        negociacao.status = 'C'
        negociacao.save()

        enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')

        atualiza_producoes(negociacao.pk)
        atualiza_preco_medio_residuo(negociacao.id_residuo.pk)