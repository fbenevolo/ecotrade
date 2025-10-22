from django import forms
from django.utils import timezone
from ..models import Usuario, Demanda, Residuo, Negociacao, ContestacaoPreco

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


class ConfirmarColetaForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='confirmar_coleta')
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self):
        super().__init__()
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
    
    comprovante = forms.ImageField()

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

        print(negociacao, opcao)

        # if opcao == 'confirmar':
        #     if tipo_usuario == 'E':
        #         negociacao.confirmacao_pgto_empresa = True
        #         negociacao.status = 'ACPC'
        #     else:
        #         negociacao.confirmacao_pgto_coop = True
        #         negociacao.status = 'C'

        # negociacao.save()


