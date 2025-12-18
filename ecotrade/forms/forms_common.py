from django.contrib.auth import get_user_model
from ..models import Usuario
from django.forms.models import ModelChoiceField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

Usuario = get_user_model()

from django.forms import ModelChoiceField
from .base import StyledFormMixin

class MyModelChoiceField(ModelChoiceField):
    '''
    Sobrescrevendo a classe para que, quando no form de cadastro a opção for 'catador',
    apareça o nome das cooperativas em "cooperativa associada", e não o email (pois é FK para usuário)
    '''
    def label_from_instance(self, obj):
        return obj.nome

class CadastroForm(StyledFormMixin, UserCreationForm):
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
    
    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_usuario')
        cnpj = cleaned.get('cnpj')
        coop = cleaned.get('cooperativa_associada')
        email = cleaned.get('email')

        # validações de email
        if email:
            try:
                validate_email(email)
            except ValidationError:
                self.add_error(None, 'Email inválido.')
        if email and Usuario.objects.filter(email=email).exists():
            self.add_error(None, 'Este email já está cadastrado no sistema. Por favor, use outro.')

        # validações de CNPJ
        if cnpj:
            cnpj = cnpj.replace(',', '').replace('.', '')
        
        if tipo == 'E' and not cnpj:
            self.add_error(None, 'CNPJ é obrigatório para usuários do tipo Empresa.')
        
        # validações de catador
        if tipo == 'CA' and not coop:
            self.add_error(None, 'Cooperativa associada é obrigatória para Catador.')

        return cleaned
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.status = 'EA'
        if commit:
            usuario.save()

        return usuario


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Forçamos o readonly inicial para o gerenciador de senhas não preencher automaticamente o campo
        self.fields['password'].widget.attrs.update({
            'readonly': 'readonly',
            'onfocus': "this.removeAttribute('readonly');",
        })