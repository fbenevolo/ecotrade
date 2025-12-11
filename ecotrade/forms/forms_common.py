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
        queryset=Usuario.objects.filter(tipo_usuario='CO', status='A', is_superuser=False))

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'nome', 'tipo_usuario', 'cnpj', 'cooperativa_associada')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cnpj'].required = False
        self.fields['cooperativa_associada'].required = False

        self.fields['tipo_usuario'].initial = 'CO'

        common = "appearance-none w-full rounded-lg block px-4 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white bg-transparent focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent"

        for fname in self.fields:
            self.fields[fname].widget.attrs.update({'class': common, 'placeholder': ' '})
    
    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_usuario')
        cnpj = cleaned.get('cnpj')
        coop = cleaned.get('cooperativa_associada')
        email = cleaned.get('email')

        if cnpj:
            cnpj = cnpj.replace(',', '').replace('.', '')
        if email and Usuario.objects.filter(email=email).exists():
            self.add_error(None, 'Este email já está cadastrado no sistema. Por favor, use outro.')
        if tipo == 'E' and not cnpj:
            self.add_error(None, 'CNPJ é obrigatório para usuários do tipo Empresa.')
        if tipo == 'CA' and not coop:
            self.add_error(None, 'Cooperativa associada é obrigatória para Catador.')

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