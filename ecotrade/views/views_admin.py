from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario
from ..forms.forms_admin import AprovarUsuarioForm
from ..utils import enviar_email_template, gera_link_acesso

@login_required
def gestao_usuarios(request, email_usuario):
    aprovar_usuario_form = AprovarUsuarioForm()

    context = {
        'usuarios': Usuario.objects.all().exclude(is_staff=True),
        'aprovar_usuario_form': aprovar_usuario_form
    }

    return render(request, 'gestao_usuarios/gestao_usuarios.html', context)


def aprovar_usuario(request, email_usuario, email_novo_usuario):
    usuario = get_object_or_404(Usuario, pk=email_novo_usuario)
    if request.method == 'POST':
        form = AprovarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            acao = form.cleaned_data['acao']
            if acao == 'aprovar':
                link = gera_link_acesso(request, 'login')
                # enviar_email_template(usuario.email, 
                #                     'conta/aprovacao_conta.html', 
                #                     'Criação de Conta', 
                #                     context = { 'nome': usuario.nome, 'link_acesso': link })
                messages.success(request, 'Usuário aprovado com sucesso.')
            else:
                messages.success(request, 'Usuário deletado com sucesso.')
            return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': email_usuario}))                



@login_required
def desativar_usuario(request, email_usuario, email_novo_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_novo_usuario)
        usuario.status = 'D'
        usuario.save()
        enviar_email_template(usuario.email, 'conta/desativacao_conta.html', 'Desativação de Conta')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': email_usuario}))
    
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': email_usuario}))

@login_required
def reativar_conta(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'A'
        usuario.save()
        link = gera_link_acesso(request, 'login')
        enviar_email_template(usuario.email, 
                              'conta/reativacao_conta.html', 
                              'Reativação de Conta', 
                              context={ 'link_site': link })
        messages.success(request, f'A conta de {usuario.email} foi reativada.')
        return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))
    return redirect(reverse('gestao_usuarios', kwargs={'email_usuario': request.user.pk}))