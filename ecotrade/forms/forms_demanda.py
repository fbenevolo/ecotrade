from django import forms
from ..models import Demanda, Residuo
from django.forms.models import ModelChoiceField

from .base import StyledFormMixin

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_tipo_display


class CadastrarDemandaForm(StyledFormMixin, forms.ModelForm):
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    quantidade = forms.FloatField(label='Quantidade (kg)')

    class Meta:
        model = Demanda
        fields = ['id_residuo', 'quantidade']


class AlterarDemandaForm(StyledFormMixin, forms.ModelForm):
    nome_residuo = forms.CharField(label='Resíduo', required='False', widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Demanda
        fields = ['quantidade']


class CadastrarAtendimentoDemandaForm(StyledFormMixin, forms.Form):
    preco_inicial = forms.DecimalField(label='Preço Inicial por kg (R$)')