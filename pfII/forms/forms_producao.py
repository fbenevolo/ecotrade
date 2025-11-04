from django import forms
from ..models import Producao, Usuario, Residuo
from django.forms.models import ModelChoiceField
from django.db.models import F

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_tipo_display

class AdicionarProducaoForm(forms.ModelForm):
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

        for field in self.fields:
            style = 'mt-1 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
            self.fields[field].widget.attrs.update({'class': style})    

    def save(self, cooperativa=None, commit=True):
        producao = super().save(commit=False)
        
        if cooperativa:
            producao.id_cooperativa = cooperativa 
        if commit:
            producao.save()
            

class AlterarProducaoForm(forms.ModelForm):
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    data = forms.DateField(label='Data', widget=forms.DateInput(attrs={'type': 'date',}))


    class Meta:
        model = Producao
        fields = ['id_residuo', 'data', 'producao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'mt-1 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'})

class RemoverProducaoForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='remover_producao')
    producao_pk = forms.CharField(widget=forms.HiddenInput())

    residuo = forms.CharField(widget=forms.HiddenInput())
    quantidade = forms.CharField(widget=forms.HiddenInput())


    def save(self):
        print()