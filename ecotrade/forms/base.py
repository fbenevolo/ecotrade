from django import forms

class StyledFormMixin:
    '''
    Classe que contém estilização básica dos campos de form.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = 'appearance-none w-full block rounded-lg px-4 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm peer placeholder-transparent dark:border-gray-700 dark:text-white dark:bg-gray-700 '
        read_only = 'cursor-not-allowed bg-gray-100'

        for field_name, field in self.fields.items():
            # pula a estilização pesada para campos checkbox ou radio
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue 

            existing_classes = field.widget.attrs.get('class', '')
            new_classes = common
            
            # Verifica se o widget tem o atributo 'readonly'
            is_readonly = field.widget.attrs.get('readonly') or getattr(field, 'disabled', False)
            if is_readonly:
                new_classes += read_only
            
            # Adiciona a classe mantendo o que já existir
            field.widget.attrs['class'] = f"{existing_classes} {new_classes}".strip()
            field.widget.attrs.setdefault('placeholder', ' ')