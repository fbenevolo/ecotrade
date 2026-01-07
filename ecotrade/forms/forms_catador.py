from django import forms
from django.db.models import F
from django.contrib.auth import get_user_model

from .base import StyledFormMixin

Usuario = get_user_model()

class AprovarContaCatadorForm(StyledFormMixin, forms.Form):
    """
    Formulário para aprovar ou rejeitar contas de catadores.
    Exibe o email e nome do catador para visualização.
    """
    # Campos de visualização (readonly)
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
    
    cooperativa_associada = forms.CharField(
        label='Cooperativa Associada',
        max_length=200,
        widget=forms.TextInput(attrs={'readonly': True}),
        required=False
    )
    
    # Campo para ação (aprovar/rejeitar)
    acao = forms.ChoiceField(
        label='Ação',
        choices=[
            ('aprovar', 'Aprovar Conta'),
            ('rejeitar', 'Rejeitar Conta')
        ],
        widget=forms.RadioSelect,
        required=True
    )
    
    # Campo oculto para guardar o ID do usuário
    usuario_id = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se um usuário foi fornecido, preencher os campos de visualização
        if usuario:
            self.fields['email'].initial = usuario.email
            self.fields['nome'].initial = usuario.nome
            self.fields['usuario_id'].initial = usuario.email
            
            # Se o catador tem cooperativa associada, mostrar o nome
            if usuario.cooperativa_associada:
                self.fields['cooperativa_associada'].initial = usuario.cooperativa_associada.nome
            else:
                self.fields['cooperativa_associada'].initial = 'Não informada'
    
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
                # Usar update para evitar validações desnecessárias
                Usuario.objects.filter(email=usuario_email).update(status='A')
                
            elif acao == 'rejeitar':
                usuario.delete()
            
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Usuário não encontrado.')

class AlterarCatadorForm(StyledFormMixin, forms.ModelForm):
    """
    Formulário para alterar dados cadastrais de catadores.
    """
    # Campo oculto para identificação
    catador_id = forms.CharField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput(), initial='alterar_catador')
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email']
        labels = {
            'nome': 'Nome do Catador',
            'email': 'Email do Catador'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': True}),  # Email não pode ser alterado
        }
    
    def save(self, commit=True):
        """
        Salva as alterações dos dados do catador.
        """
        catador_email = self.cleaned_data['catador_id']
        novo_nome = self.cleaned_data['nome']
        try:
            # Atualizar apenas o nome (email não pode ser alterado)
            Usuario.objects.filter(email=catador_email).update(nome=novo_nome)
            print('atualizado')
        except Exception as e:
            raise forms.ValidationError(f'Erro ao alterar dados do catador: {str(e)}')
