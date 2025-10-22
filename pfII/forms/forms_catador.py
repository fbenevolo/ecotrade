from django import forms
from django.db.models import F
from ..models import Producao, CoopDetemResiduo
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class AprovarContaCatadorForm(forms.Form):
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
        
        # Aplicar estilos CSS aos campos
        common_style = "w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary"
        readonly_style = "w-full bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg cursor-not-allowed"
        
        # Aplicar estilo aos campos readonly
        self.fields['email'].widget.attrs.update({'class': readonly_style})
        self.fields['nome'].widget.attrs.update({'class': readonly_style})
        self.fields['cooperativa_associada'].widget.attrs.update({'class': readonly_style})
        
        # Aplicar estilo ao campo de ação
        self.fields['acao'].widget.attrs.update({'class': 'text-primary'})
    
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

class AlterarCatadorForm(forms.ModelForm):
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        common_style = "w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary"
        readonly_style = "w-full bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg cursor-not-allowed"
        
        self.fields['nome'].widget.attrs.update({'class': common_style})
        self.fields['email'].widget.attrs.update({'class': readonly_style})
    
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

class ExcluirCatadorForm(forms.Form):
    """
    Formulário para confirmar exclusão de catadores.
    """
    # Campos ocultos para identificação
    catador_id = forms.CharField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput(), initial='excluir_catador')
    
    # Campo de confirmação
    confirmacao = forms.BooleanField(
        label='Confirmo que desejo excluir permanentemente esta conta',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-red-600 focus:ring-red-500'})
    )
    
    def __init__(self, *args, catador=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se um catador foi fornecido, preencher o ID
        if catador:
            self.fields['catador_id'].initial = catador.email
    
    def save(self):
        """
        Exclui o catador do banco de dados.
        """
        catador_email = self.cleaned_data['catador_id']
        try:
            catador = Usuario.objects.get(email=catador_email)

            # excluir todas as producoes associadas ao catador e atualiza a quantidade que a cooperativa tem
            producoes = Producao.objects.filter(id_catador=catador)
            for producao in producoes:
                CoopDetemResiduo.objects.filter(id_residuo=producao.id_residuo).update(
                    quantidade=F('quantidade')-producao.producao
                )
                producao.delete()

            catador.delete()
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Catador não encontrado.')
        except Exception as e:
            raise forms.ValidationError(f'Erro ao excluir catador: {str(e)}')



