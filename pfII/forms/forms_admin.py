from django import forms
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class AprovarContaForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='aprovar_usuario') 

    email = forms.EmailField(
        label='Email do Catador',
        widget=forms.EmailInput(attrs={'readonly': True}),
        required=False
    )

    nome = forms.CharField(
        label='Nome do Catador',
        max_length=200,
        widget=forms.TextInput(attrs={'readonly': True}),
        required=False
    )

    acao = forms.ChoiceField(
        label='Ação',
        choices=[
            ('aprovar', 'Aprovar Conta'),
            ('rejeitar', 'Rejeitar Conta')
        ],
        widget=forms.RadioSelect,
        required=True
    )
    
    usuario_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
            
        # Aplicar estilos CSS aos campos
        common_style = "w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary"
        readonly_style = "w-full bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg cursor-not-allowed"

        self.fields['email'].widget.attrs.update({'class': readonly_style})
        self.fields['nome'].widget.attrs.update({'class': readonly_style})        
        self.fields['acao'].widget.attrs.update({'class': common_style})
    
    def save(self):
        """
        Processa a aprovação ou rejeição do catador.
        Em caso de rejeição, deleta a conta do banco de dados.
        """
        usuario_email = self.cleaned_data['usuario_id']
        acao = self.cleaned_data['acao']

        try:
            usuario = Usuario.objects.get(email=usuario_email)
            if acao == 'aprovar':
                Usuario.objects.filter(email=usuario_email).update(status='A')
                return usuario
            elif acao == 'rejeitar':
                usuario.delete()
                return None
            
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Usuário não encontrado.')