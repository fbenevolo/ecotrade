from django import forms
from ..models import Producao, Usuario, Residuo
from django.forms.models import ModelChoiceField
from django.db.models import F

from .base import StyledFormMixin

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_tipo_display

class AdicionarProducaoForm(StyledFormMixin, forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create_residuo')
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Data')

    class Meta:
        model = Producao
        fields = ['id_catador', 'id_residuo', 'producao', 'data']

        labels = {
            'id_catador': 'Catador',
            'producao': 'Quantidade Produzida (kg)'
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
        producao = super().save(commit=False)
        
        if cooperativa:
            producao.id_cooperativa = cooperativa 
        if commit:
            producao.save()
            

class AlterarProducaoForm(StyledFormMixin, forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='alterar_producao') 
    producao_pk = forms.CharField(widget=forms.HiddenInput())
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    producao = forms.FloatField(label='Produção')
    data = forms.DateField(label='Data', widget=forms.DateInput(attrs={'type': 'date',}))

    class Meta:
        model = Producao
        fields = ['id_residuo', 'data', 'producao']
        

class RemoverProducaoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='remover_producao')
    producao_pk = forms.CharField(widget=forms.HiddenInput())
    residuo = forms.CharField(widget=forms.HiddenInput())
    quantidade = forms.CharField(widget=forms.HiddenInput())