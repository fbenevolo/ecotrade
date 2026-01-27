from django import forms
from django.contrib.auth import get_user_model
from .base import StyledFormMixin


Usuario = get_user_model()

class AprovarUsuarioForm(StyledFormMixin, forms.ModelForm):
    acao = forms.ChoiceField(
        label='Ação',
        choices=[
            ('aprovar', 'Aprovar Conta'),
            ('rejeitar', 'Rejeitar Conta')
        ],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['acao'] 
    
    def save(self):
        instance = super().save(commit=False)
        acao = self.cleaned_data['acao']

        if acao == 'aprovar':
            instance.status = 'A'
            instance.save()
        elif acao == 'rejeitar':
            instance.delete()