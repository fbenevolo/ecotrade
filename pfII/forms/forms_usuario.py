from django import forms
from ..models import Usuario

class AlterarUsuarioForm(forms.ModelForm):
    nome = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'cnpj']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        common_style = 'w-full bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-primary focus:border-primary'
        readonly_style = "w-full bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg cursor-not-allowed"
        
        self.fields['email'].widget.attrs['readonly'] = True
        
        self.fields['nome'].widget.attrs.update({'class': common_style })
        self.fields['email'].widget.attrs.update({'class': readonly_style})
        self.fields['cnpj'].widget.attrs.update({'class': common_style })

        if self.instance:
            self.fields['nome'].initial = self.instance.nome
            if self.instance.tipo_usuario != 'E':
                del self.fields['cnpj']



    def save(self, commit=True):
        self.instance.first_name = self.cleaned_data['nome']
        return super().save(commit)
