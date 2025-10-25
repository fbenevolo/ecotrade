from django import forms
from django.utils import timezone
from ..models import Negociacao, ContestacaoPreco, ContestacaoPagamento

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
        negociacao = Negociacao.objects.filter(pk=id_negociacao)

        neg_obj = negociacao.first()
        if opcao == 'cancelar':
            negociacao.update(status='C')
        elif opcao == 'confirmar':
            if tipo_usuario == 'E':
                if neg_obj.status == 'ACE':
                    if neg_obj.confirmacao_preco_cooperativa == True:
                        negociacao.update(confirmacao_empresa=True, status='AC')
                    else:
                        negociacao.update(confirmacao_empresa=True, status='ACC')                    
            else:
                if neg_obj.status == 'ACC':
                    if neg_obj.confirmacao_preco_empresa == True:
                        negociacao.update(confirmacao_cooperativa=True, status='AC')
                    else:
                        negociacao.update(confirmacao_cooperativa=True, status='ACE')


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
                status = 'AAC'
            else:
                status = 'AAE'
            ContestacaoPreco.objects.create(
                id_negociacao=negociacao,
                status=status,
                contestador=contestador,
                justificativa=justificativa,
                preco_proposto=preco_proposto
            )
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

        else:
            contestacao_antiga.status = 'DE'
            novo_status = 'ACC'
        contestacao_antiga.save()

        try:
            # altera o status da negociação para ser a confirmação da parte que receberá a contestação
            negociacao.status = novo_status

            print(novo_status)
            negociacao.save()
            # abre uma nova contestação
            ContestacaoPreco.objects.create(
                id_negociacao=negociacao,
                status=novo_status,
                contestador=contestador,
                justificativa=justificativa,
                preco_proposto=preco_proposto
            )
        except Exception as e:
            print(f'Erro ao criar uma nova contestação: {e}')


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


class ConfirmarPagamentoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_pagamento')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    opcoes = forms.ChoiceField(
        choices=(
            ('confirmar', 'Confirmar Pagamento'),
            ('contestar', 'Contestar Pagamento'),
        ),
        widget=forms.HiddenInput()
    )
    
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
        opcao = self.cleaned_data['opcoes']
        negociacao = Negociacao.objects.get(pk=id_negociacao)

        try:
            if self.tipo_usuario == 'E':
                    comprovante = self.cleaned_data['comprovante']
                    negociacao.comprovante = comprovante
                    negociacao.confirmacao_pgto_empresa = True
                    negociacao.status = 'ACPC'
                    negociacao.save()
            else:
                if opcao == 'confirmar':
                    negociacao.confirmacao_pgto_coop = True
                    negociacao.status = 'C'
                    negociacao.data_conclusao = timezone.now()
                    negociacao.save()
            
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

            # # cria uma contestação de pagamento
            # ContestacaoPagamento.objects.create(
            #     status='EE',
            #     justificativa=justificativa,
            #     id_negociacao=negociacao,
            #     usuario='C',
            # )

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

            ContestacaoPagamento.objects.create(
                id_negociacao=negociacao,
                justificativa=justificativa,
                comprovante=comprovante,
                status='EE',
                usuario='E'
            )
        except Exception as e:
            print(f'Erro ao criar resposta à contestação de pagamento: {e}')