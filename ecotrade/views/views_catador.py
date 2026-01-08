from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario
from ..forms.forms_catador import AprovarContaCatadorForm


def catadores(request, email_usuario):
    catadores = Usuario.objects.filter(cooperativa_associada=email_usuario)
    
    context = {
        'catadores': catadores
    }

    return render(request, 'catador/catadores.html', context=context)


def aprovar_conta_catador(request, email_usuario, email_catador):
    catador = get_object_or_404(Usuario, pk=email_catador)
    if request.method == 'POST':
        form = AprovarContaCatadorForm(request.POST, instance=catador)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Conta de catador aprovada com sucesso.')
                return redirect(reverse('catadores', kwargs={'email_usuario': email_usuario}))
            except Exception as e:
                print(f'Erro ao aprovar conta de catador: {e}')
                return redirect(reverse('catadores', kwargs={'email_usuario': email_usuario}))
        else:
            print(form.errors.as_data())

    return redirect(reverse('catadores', kwargs={'email_usuario': email_usuario}))
