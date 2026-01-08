from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Producao
from ..forms.forms_producao import AdicionarProducaoForm, AlterarProducaoForm

@login_required
def producoes(request, email_usuario):
    # verificacao de segurança
    usuario = get_object_or_404(Usuario, pk=email_usuario)
    
    
    adicionar_producao_form = AdicionarProducaoForm(cooperativa=usuario)
    alterar_producao_form = AlterarProducaoForm()        
    
    producoes_catador = None # Informação exclusiva para catador
        
    if request.user.tipo_usuario == 'CA':
        producoes = Producao.objects.filter(id_cooperativa=usuario.cooperativa_associada)
        producoes_catador = producoes.filter(id_catador=usuario.pk).exclude(status='z')
    else:
        producoes = Producao.objects.filter(id_cooperativa=usuario.pk)
    
    catadores = Usuario.objects.filter(cooperativa_associada=usuario.pk)

    context = {
        'producoes': producoes,
        'catadores': catadores,
        'producoes_catador': producoes_catador,
        'adicionar_producao_form': adicionar_producao_form,
        'alterar_producao_form': alterar_producao_form,
    }

    return render(request, 'producao/producoes.html', context)


def cadastrar_producao(request, email_usuario):
    usuario = get_object_or_404(Usuario, pk=email_usuario)
    if request.method == 'POST':
        form = AdicionarProducaoForm(request.POST, cooperativa=usuario)
        if form.is_valid():
            try:
                form.save(cooperativa=usuario)
                messages.success(request, 'Produção adicionada com sucesso.')
                return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))
            except Exception as e:
                print(f'Erro ao adicionar produção: {e}')
        else:
            messages.error(request, 'Erro ao adicionar produção.')
            return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))


def alterar_producao(request, email_usuario, id_producao):
    producao = get_object_or_404(Producao, pk=id_producao)
    if request.method == 'POST':
        form = AlterarProducaoForm(request.POST, instance=producao)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Produção alterada com sucesso.')
                return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))
            except Exception as e:
                print(f'Erro ao alterar produçã: {e}')
        else:
            messages.error(request, 'Erro ao alterar produção.')
            return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))
                
    return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))


def remover_producao(request, email_usuario, id_producao):
    producao = get_object_or_404(Producao, pk=id_producao)
    if request.method == 'POST':
        try:
            producao.delete()
            messages.success(request, 'Produção removida com sucesso.')
            return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))
        except Exception as e:
            print(f'Erro ao remover produção: {e}')
            messages.error(request, 'Erro ao remover produção')
            return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))                

    return redirect(reverse('producoes', kwargs={'email_usuario': email_usuario}))

