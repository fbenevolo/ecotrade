from django import forms
from ..models import Demanda, Residuo
from django.forms.models import ModelChoiceField


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_tipo_display


class CadastrarDemandaForm(forms.ModelForm):
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    quantidade = forms.FloatField(label='Quantidade (kg)')

    class Meta:
        model = Demanda
        fields = ['id_residuo', 'quantidade']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = 'mt-3 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
        for field in self.fields.values():
            field.widget.attrs.update({'class': style})


class AlterarDemandaForm(forms.ModelForm):
    nome_residuo = forms.CharField(label='Resíduo', required='False', widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Demanda
        fields = ['quantidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        style = 'mt-3 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
        self.fields['quantidade'].widget.attrs.update({'class': style})
        self.fields['nome_residuo'].widget.attrs.update({'class': style + ' cursor-not-allowed bg-gray-100'}) # estilização readonly


class CadastrarAtendimentoDemandaForm(forms.Form):
    preco_inicial = forms.DecimalField(label='Preço Inicial por kg (R$)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = "appearance-none w-full rounded-lg block px-4 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white bg-transparent focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent"
        for field in self.fields.values():
            field.widget.attrs.update({'class': common})