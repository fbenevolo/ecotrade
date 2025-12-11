from django import forms
from ..models import Usuario, Demanda, Residuo, Negociacao, NegociacaoPagaTrabalho
from django.forms.models import ModelChoiceField

from ..utils import seleciona_producoes, enviar_email_template


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_tipo_display

class CadastrarDemandaForm(forms.ModelForm):
    id_residuo = MyModelChoiceField(queryset=Residuo.objects.all(), label='Resíduo')
    quantidade = forms.FloatField(label='Quantidade (kg)')

    class Meta:
        model = Demanda
        fields = ['id_residuo', 'quantidade']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style = 'mt-3 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
        for field in self.fields.values():
            field.widget.attrs.update({'class': style})


class AlterarDemandaForm(forms.ModelForm):
    nome_residuo = forms.CharField(label='Resíduo', required='False', widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Demanda
        fields = ['quantidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        style = 'mt-3 block w-full bg-background-light dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm'
        self.fields['quantidade'].widget.attrs.update({'class': style})
        self.fields['nome_residuo'].widget.attrs.update({'class': style + ' cursor-not-allowed bg-gray-100'}) # estilização readonly


class ExcluirDemandaForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='excluir_demanda')
    id_demanda = forms.CharField(widget=forms.HiddenInput())

    def save(self):
        id_demanda = self.cleaned_data['id_demanda']
        try:
            Demanda.objects.filter(pk=id_demanda).delete()
        except Exception as e:
            print(f'Erro ao deletar demanda: {e}')


class CadastrarAtendimentoDemandaForm(forms.Form):
    id_demanda = forms.CharField(widget=forms.HiddenInput())
    id_cooperativa = forms.CharField(widget=forms.HiddenInput())
    id_residuo = forms.CharField(widget=forms.HiddenInput())
    preco_inicial = forms.DecimalField(label='Preço Inicial por kg (R$)')
    action = forms.CharField(widget=forms.HiddenInput(), initial='cadastrar_atendimento_demanda')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = "appearance-none w-full rounded-lg block px-4 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white bg-transparent focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent"
        for field in self.fields.values():
            field.widget.attrs.update({'class': common})

    def save(self):
        id_demanda = self.cleaned_data['id_demanda']
        id_residuo = self.cleaned_data['id_residuo']
        id_cooperativa = self.cleaned_data['id_cooperativa']
        preco_inicial = self.cleaned_data['preco_inicial']

        if preco_inicial is None or preco_inicial <= 0 or preco_inicial == ' ':
            raise forms.ValidationError('Erro no preenchimento do campo de preço. Verifique novamente')

        try:
            # atualiza demanda
            demanda = Demanda.objects.get(pk=id_demanda)
            demanda.status='A'
            demanda.save()

            cooperativa = Usuario.objects.get(pk=id_cooperativa)
            residuo = Residuo.objects.get(pk=id_residuo)
            # Cria objeto negociação com as informações da demanda
            negociacao = Negociacao.objects.create(id_empresa=demanda.id_empresa,
                                    id_cooperativa=cooperativa,
                                    id_residuo=residuo,
                                    quantidade=demanda.quantidade,
                                    preco=preco_inicial,
                                    confirmacao_preco_cooperativa=True,
                                    demanda_associada=demanda,
                                    status='ACE')
            
            enviar_email_template(cooperativa.email, 'negociacao/negociacao_iniciada.html', 'Negociação Iniciada')
            enviar_email_template(demanda.id_empresa.email, 'negociacao/negociacao_iniciada.html', 'Negociação Iniciada')

            # seleciona producoes e aloca elas para negociação
            producoes = seleciona_producoes(id_demanda)
            for (producao, quantidade) in producoes.items():
                producao.status = 'a'
                producao.id_negociacao = negociacao 
                producao.save()

                # cria objetos NegociacaoPagaTrabalho
                NegociacaoPagaTrabalho.objects.create(id_negociacao=negociacao,
                               id_producao=producao,
                               quantidade=quantidade,
                               id_catador=producao.id_catador)

        except Exception as e:
            print(f'Erro ao criar negociação: {e}')
            

