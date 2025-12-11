from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Producao
from ..forms.forms_producao import AdicionarProducaoForm, AlterarProducaoForm, RemoverProducaoForm
from ..forms.forms_catador import AprovarContaCatadorForm, AlterarCatadorForm

@login_required
def producoes(request, email_usuario):
    # verificacao de segurança
    usuario = request.user
    if usuario.email != email_usuario:
        messages.error(request, "Acesso negado. Você só pode ver produção para sua conta.")
        return redirect('home') 
    
    adicionar_producao_form = AdicionarProducaoForm(cooperativa=usuario)
    aprovar_catador_form = AprovarContaCatadorForm()
    alterar_catador_form = AlterarCatadorForm()

    alterar_producao_form = AlterarProducaoForm()        
    remover_producao_form = RemoverProducaoForm()
    
    outras_infos = {}

    if request.method == 'POST':
        # pega a ação que é para ser feita: criação, alteração, remoção de produção ou aprovação de catador
        action = request.POST.get('action')

        # --- PROCESSAMENTO DE APROVAÇÃO DE CATADOR ---
        if 'acao' in request.POST:  # Verifica se é uma ação de aprovação
            aprovar_catador_form = AprovarContaCatadorForm(request.POST)
            if aprovar_catador_form.is_valid():
                try:
                    aprovar_catador_form.save()
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
                except Exception as e:
                    messages.error(request, f'Erro ao processar aprovação: {str(e)}')
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
        
        elif 'alterar_catador' in action:
            catador = get_object_or_404(Usuario, email=request.POST.get('catador_id'))
            alterar_catador_form = AlterarCatadorForm(request.POST, instance=catador)
            if alterar_catador_form.is_valid():
                try:
                    alterar_catador_form.save()
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
                except Exception as e:
                    messages.error(request, f'Erro ao alterar dados do catador: {str(e)}')
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
        
        if 'create_residuo' in action:            
            adicionar_producao_form = AdicionarProducaoForm(request.POST, cooperativa=usuario)
            if adicionar_producao_form.is_valid():
                adicionar_producao_form.save(cooperativa=usuario)
                messages.success(request, "Produção registrada com sucesso!")
                return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))

        elif 'alterar_producao' in action:
            producao_pk = request.POST.get('producao_pk')
            producao_instancia = get_object_or_404(Producao, pk=producao_pk, id_cooperativa=usuario)
            
            alterar_form = AlterarProducaoForm(request.POST, instance=producao_instancia)
            if alterar_form.is_valid():
                alterar_form.save()
                messages.success(request, "Produção alterada com sucesso!")
                return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))

        # PROCESSAMENTO DE REMOÇÃO DE RESÍDUO
        elif 'remover_producao' in action:
            producao_pk = request.POST.get('producao_pk')
            producao_instancia = get_object_or_404(Producao, pk=producao_pk, id_cooperativa=usuario)
            producao_instancia.delete()

            messages.success(request, "Produção removida com sucesso.")
            return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
    
    if request.user.tipo_usuario == 'CA':
        producoes = Producao.objects.filter(id_cooperativa=usuario.cooperativa_associada)
        outras_infos['producoes_catador'] = producoes.filter(id_catador=usuario.pk).exclude(status='z')
    else:
        producoes = Producao.objects.filter(id_cooperativa=usuario.pk)
    
    catadores = Usuario.objects.filter(cooperativa_associada=usuario.pk)

    context = {
        'producoes': producoes,
        'catadores': catadores,
        'adicionar_producao_form': adicionar_producao_form,
        'remover_producao_form': remover_producao_form,
        'alterar_producao_form': alterar_producao_form,
        'aprovar_catador_form': aprovar_catador_form,
        'alterar_catador_form': alterar_catador_form,
    }

    context['outras_infos'] = outras_infos

    return render(request, 'producao/producoes.html', context)
