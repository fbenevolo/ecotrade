from django import forms
from ..models import Producao, Usuario, Residuo
from django.forms.models import ModelChoiceField
from django.db.models import F

from .base import StyledFormMixin

class ResiduoModelChoiceField(ModelChoiceField):
    '''
    Sobrescreve a função label_from_instance para se obter os nomes dos resíduos ao invés de IDs numéricos.
    '''
    def label_from_instance(self, obj):
        return obj.get_tipo_display 
    

class UsuarioChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Retorna a string personalizada: email (nome)
        return f'{obj.email} ({obj.nome})'


class AdicionarProducaoForm(StyledFormMixin, forms.ModelForm):
    id_residuo = ResiduoModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    id_catador = UsuarioChoiceField(queryset=Usuario.objects.none(), label='Catador') # inicializa o queryset como vazio 

    class Meta:
        model = Producao
        fields = ['id_catador', 'id_residuo', 'producao', 'data']

        labels = {
            'producao': 'Quantidade Produzida (kg)',
            'data': 'Data'
        }

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        cooperativa = kwargs.pop('cooperativa', None)
        super().__init__(*args, **kwargs)

        # Filtra apenas os catadores associados a essa cooperativa
        if cooperativa:
            self.fields['id_catador'].queryset = Usuario.objects.filter(
                cooperativa_associada=cooperativa.pk # Use .pk do objeto Usuario da cooperativa
            ) 

    def save(self, cooperativa=None, commit=True):
        ''' Foi necessário sobrescrever para linkar a produção com uma cooperativa '''
        producao = super().save(commit=False)

        if cooperativa:
            producao.id_cooperativa = cooperativa 
        if commit:
            producao.save()
            

class AlterarProducaoForm(StyledFormMixin, forms.ModelForm):
    id_residuo = ResiduoModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')

    class Meta:
        model = Producao
        fields = ['id_residuo', 'data', 'producao']

        labels = {
            'producao': 'Produção',
            'data': 'Data'
        }

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }


class RemoverProducaoForm(forms.ModelForm):
    # action = forms.CharField(widget=forms.HiddenInput(), initial='remover_producao')
    # producao_pk = forms.CharField(widget=forms.HiddenInput())
    # residuo = forms.CharField(widget=forms.HiddenInput())
    # quantidade = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Producao
        fields = []