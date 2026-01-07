from django import forms
from ..models import Usuario
from .base import StyledFormMixin

class AlterarUsuarioForm(StyledFormMixin, forms.ModelForm):
    nome = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'cnpj']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': True}),  # Email não pode ser alterado
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['nome'].initial = self.instance.nome
            if self.instance.tipo_usuario != 'E':
                del self.fields['cnpj']



    def save(self, commit=True):
        self.instance.first_name = self.cleaned_data['nome']
        return super().save(commit)
