from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario
from ..forms.forms_admin import AprovarContaForm

@login_required
def aceitar_desativacao(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'D'
        usuario.save()
        messages.success(request, f'A conta de {usuario.email} foi desativada.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))

@login_required
def recusar_desativacao(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'A'
        usuario.save()
        messages.success(request, f'A desativação da conta de {usuario.email} foi recusada.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))

@login_required
def aceitar_exclusao(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.delete()
        messages.success(request, f'A conta de {usuario.email} foi excluída.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))

@login_required
def recusar_exclusao(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'A'
        usuario.save()
        messages.success(request, f'A exclusão da conta de {usuario.email} foi recusada.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))

@login_required
def reativar_conta(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'A'
        usuario.save()
        messages.success(request, f'A conta de {usuario.email} foi reativada.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))

@login_required
def gestao_usuarios(request, email_usuario):

    aprovar_usuario = AprovarContaForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if 'aprovar_usuario' in action:
            usuario_id = request.POST.get('usuario_id')
            aprovar_conta_form = AprovarContaForm(request.POST, usuario=usuario_id)
            if aprovar_conta_form.is_valid():
                try:
                    aprovar_conta_form.save() 
                    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': email_usuario}))                
                except forms.ValidationError as ve:
                    messages.error(request, 'Erro na operação. Verifique o formulário.') 
                
    context = {
        'usuarios': Usuario.objects.all(),
        'aprovar_usuario_form': aprovar_usuario
    }

    return render(request, 'gestao_usuarios/gestao_usuarios.html', context)