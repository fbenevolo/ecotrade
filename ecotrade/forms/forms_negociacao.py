from django import forms
from django.utils import timezone
from ..models import Producao, Negociacao, NegociacaoPagaTrabalho, ContestacaoPreco, ContestacaoPagamento

from .base import StyledFormMixin
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


class ContestarPrecoForm(StyledFormMixin, forms.ModelForm):
    id_negociacao = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ContestacaoPreco
        fields = ['justificativa', 'preco_proposto']

        labels = {
            'justificativa': 'Justificativa',
            'preco_proposto': 'Preço Proposto'
        }

        widgets = {
            'justificativa': forms.Textarea()
        }

    def save(self, tipo_usuario):
        negociacao = Negociacao.objects.get(pk=self.cleaned_data['id_negociacao'])
        status = 'ACC' if tipo_usuario == 'E' else 'ACE'

        # Cria um objeto ContestacaoPreco
        contestacao = super().save(commit=False)
        contestacao.id_negociacao = negociacao
        contestacao.contestador = tipo_usuario
        contestacao.status = status
        contestacao.save()

        # Modifica o status da negociação
        negociacao.status = status
        negociacao.save()


class ResponderContestacaoPrecoForm(ContestarPrecoForm):
    opcoes = forms.ChoiceField(
        choices=(
            ('aceitar', 'Aceitar'),
            ('contestar', 'Propor Novo Preço'),    
        ),
        widget=forms.RadioSelect
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornamos os campos opcionais para que o 'aceitar' funcione
        self.fields['id_negociacao'].required = False
        self.fields['justificativa'].required = False
        self.fields['preco_proposto'].required = False

    def save(self, tipo_usuario, instance=None):
        opcao = self.cleaned_data['opcoes']
        if opcao == 'aceitar':
            instance.status = 'A'
            instance.save()
            
            negociacao = instance.id_negociacao
            negociacao.status = 'AC'
            negociacao.save()
        else:
            instance.status = 'DC' if tipo_usuario == 'CO' else 'DE'
            instance.save()
            # Se for 'contestar', usamos a lógica da classe pai para criar uma NOVA instância
            return super().save(tipo_usuario)


class ConfirmarColetaForm(StyledFormMixin, forms.ModelForm):
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Negociacao
        fields = ['data']

    def save(self):
        instance = super().save(commit=False)
        instance.data_coleta = self.cleaned_data['data']
        instance.status = 'ET'
        instance.save() 


class ConfirmarEntregaForm(StyledFormMixin, forms.ModelForm):
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Negociacao
        fields = ['data']

    def save(self):
        instance = super().save(commit=False)        
        instance.status = 'ACPE'
        instance.data_coleta = self.cleaned_data['data']
        instance.save()


class ConfirmarPagamentoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Negociacao
        fields = ['comprovante']

        widgets = {
            'comprovante': forms.ClearableFileInput(attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.tipo_usuario = kwargs.pop('tipo_usuario', None)
        super().__init__(*args, **kwargs)
        # se usuário for cooperativa, não precisa anexar comprovante
        if self.tipo_usuario == 'CO':
            del self.fields['comprovante']

    def save(self):
        instance = super().save(commit=False)
        if self.tipo_usuario == 'E':
            instance.confirmacao_pgto_empresa = True
            instance.status = 'ACPC'
        else:
            instance.confirmacao_pgto_coop = True
            instance.data_conclusao = timezone.now().date()
            instance.status = 'C'
        
        instance.save()


class ContestarPagamentoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContestacaoPagamento
        fields = ['justificativa']

    def save(self, id_negociacao):
        # mudando status de negociação para 'Aguardando Confirmação de Pagamento da Empresa'
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        negociacao.status = 'ACPE' 
        negociacao.save()
        
        instance = super().save(commit=False)
        instance.id_negociacao = negociacao
        instance.status = 'EE'
        instance.usuario = 'CO'
        instance.save()


class ResponderContestacaoPagamentoEmpresaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContestacaoPagamento
        fields = ['justificativa', 'comprovante']

        labels = {
            'comprovante': 'Carregar um Arquivo'
        }

        widgets = {
            'comprovante': forms.ClearableFileInput(attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer'
            }),
        }

    def save(self, id_negociacao):
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        negociacao.status = 'ACPC'
        negociacao.save()
        
        instance = super().save(commit=False)
        instance.id_negociacao = negociacao
        instance.usuario = 'E'
        instance.status = 'EE'
        instance.save()


class ResponderContestacaoPagamentoCoopForm(StyledFormMixin, forms.ModelForm):
    justificativa = forms.CharField(required=False, widget=forms.Textarea())
    opcoes = forms.ChoiceField(
        choices=(
            ('confirmar', 'Confirmar'),
            ('contestar', 'Contestar Novamente'),
        ),
        widget=forms.RadioSelect()
    )

    class Meta:
        model = ContestacaoPagamento
        fields = ['justificativa', 'opcoes']

    def save(self, id_negociacao):
        opcao = self.cleaned_data['opcoes']
        negociacao = Negociacao.objects.get(pk=id_negociacao)
        
        contestacao_atual = ContestacaoPagamento.objects.get(pk=self.instance.pk)
        contestacao_atual.status = 'A'
        contestacao_atual.save()
        
        if opcao == 'confirmar':
            negociacao.comprovante = contestacao_atual.comprovante
            negociacao.data_conclusao = timezone.now()
            negociacao.status = 'C'
            negociacao.save()

            return contestacao_atual
        else:
            nova_contestacao = super().save(commit=False)
            nova_contestacao.pk = None
            nova_contestacao.comprovante = None
            nova_contestacao.id_negociacao = negociacao
            nova_contestacao.status = 'EE'
            nova_contestacao.usuario = 'CO'
            nova_contestacao.save()

            negociacao.status = 'ACPE'
            negociacao.save()

            return nova_contestacao