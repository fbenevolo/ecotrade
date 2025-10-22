from django import forms
from ..models import Usuario
from django.contrib.auth import get_user_model
from django.forms.models import ModelChoiceField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

Usuario = get_user_model()

from django.forms import ModelChoiceField

class MyModelChoiceField(ModelChoiceField):
    '''
    Sobrescrevendo a classe para que, quando no form de cadastro a opção for 'catador',
    apareça o nome das cooperativas em "cooperativa associada", e não o email (pois é FK para usuário)
    '''
    def label_from_instance(self, obj):
        return obj.nome

class SignUpForm(UserCreationForm):
    cooperativa_associada = MyModelChoiceField(
        queryset=Usuario.objects.filter(tipo_usuario='CO'),)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'nome', 'tipo_usuario', 'cnpj', 'cooperativa_associada')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cnpj'].required = False
        self.fields['cooperativa_associada'].required = False

        self.fields['tipo_usuario'].initial = 'CO'

        # classes para inputs: full width + peer para floating label + placeholder transparente
        common = "appearance-none w-full rounded-lg block px-4 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white bg-transparent focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent"

        for fname in self.fields:
            # if fname in self.fields:
                # placeholder ' ' é importante para ativar peer-placeholder-shown nos labels flutuantes
                self.fields[fname].widget.attrs.update({'class': common, 'placeholder': ' '})
    
    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_usuario')
        cnpj = cleaned.get('cnpj')
        coop = cleaned.get('cooperativa_associada')

        if tipo == 'E' and not cnpj:
            self.add_error('cnpj', 'CNPJ é obrigatório para usuários do tipo Empresa.')
        if tipo == 'CA' and not coop:
            self.add_error('cooperativa_associada', 'Cooperativa associada é obrigatória para Catador.')

        return cleaned
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.status = 'EA'
        if commit:
            usuario.save()
        return usuario


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # classes para inputs: full width + peer para floating label + placeholder transparente
        common = "appearance-none w-full rounded-lg block px-4 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white bg-transparent focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent"

        for fname in self.fields:
            # if fname in self.fields:
                # placeholder ' ' é importante para ativar peer-placeholder-shown nos labels flutuantes
                self.fields[fname].widget.attrs.update({'class': common, 'placeholder': ' '})