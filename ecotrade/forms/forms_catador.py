from django import forms
from django.db.models import F
from django.contrib.auth import get_user_model

from .base import StyledFormMixin

Usuario = get_user_model()

class AprovarContaCatadorForm(StyledFormMixin, forms.ModelForm):
    '''
    Formulário para aprovar ou rejeitar contas de catadores.
    Exibe o email e nome do catador para visualização.
    '''
    # Campo para ação (aprovar/rejeitar)
    acao = forms.ChoiceField(label='Ação', 
                             choices=[ ('aprovar', 'Aprovar Conta'), ('rejeitar', 'Rejeitar Conta')],
                             widget=forms.RadioSelect,
                             required=True
                             )
    class Meta:
        model = Usuario
        fields = ['acao']
    
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
        '''
        Processa a aprovação ou rejeição do catador.
        Em caso de rejeição, deleta a conta do banco de dados.
        '''
        catador = self.instance
        acao = self.cleaned_data['acao']            
        if acao == 'aprovar':
            catador.status = 'A'
            catador.save()            
        elif acao == 'rejeitar':
            catador.delete()