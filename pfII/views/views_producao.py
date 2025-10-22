from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import F
from ..models import Usuario, Producao, CoopDetemResiduo
from ..forms.forms_producao import AdicionarProducaoForm, AlterarProducaoForm, RemoverProducaoForm
from ..forms.forms_catador import AprovarContaCatadorForm, AlterarCatadorForm, ExcluirCatadorForm

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
    excluir_catador_form = ExcluirCatadorForm()

    alterar_producao_form = AlterarProducaoForm()
        
    remover_producao_form = RemoverProducaoForm()
    

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
        
        # --- PROCESSAMENTO DE ALTERAÇÃO DE CATADOR ---
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
        
        # --- PROCESSAMENTO DE EXCLUSÃO DE CATADOR ---
        elif 'excluir_catador' in action:
            excluir_catador_form = ExcluirCatadorForm(request.POST)
            if excluir_catador_form.is_valid():
                try:
                    catador_email = excluir_catador_form.cleaned_data['catador_id']
                    catador = get_object_or_404(Usuario, email=catador_email)
                    catador_nome = catador.nome
                    
                    excluir_catador_form.save()
                    
                    messages.success(request, f'Catador {catador_nome} excluído com sucesso!')
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
                    
                except Exception as e:
                    messages.error(request, f'Erro ao excluir catador: {str(e)}')
                    return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))

        # PROCESSAMENTO DE CRIAÇÃO DE RESÍDUO
        if 'create_residuo' in action:            
            adicionar_producao_form = AdicionarProducaoForm(request.POST, cooperativa=usuario)
            if adicionar_producao_form.is_valid():
                adicionar_producao_form.save(cooperativa=usuario)
                messages.success(request, "Produção registrada com sucesso!")
                return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))

        # PROCESSAMENTO DE ALTERAÇÃO DE RESÍDUO
        elif 'update' in action:
            producao_pk = request.POST.get('producao_pk')
            # Garante que a produção existe e pertence à cooperativa
            producao_instancia = get_object_or_404(Producao, pk=producao_pk, id_cooperativa=usuario)
            
            alterar_form = AlterarProducaoForm(request.POST, instance=producao_instancia)
            if alterar_form.is_valid():
                alterar_form.save()
                messages.success(request, "Produção alterada com sucesso!")
                return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))

        # PROCESSAMENTO DE REMOÇÃO DE RESÍDUO
        elif 'remover_producao' in action:
            producao_pk = request.POST.get('producao_pk')
            residuo = request.POST.get('residuo')
            quantidade_removida = request.POST.get('quantidade').replace(',', '.')
            producao_instancia = get_object_or_404(Producao, pk=producao_pk, id_cooperativa=usuario)
            producao_instancia.delete()

            CoopDetemResiduo.objects.filter(id_cooperativa=usuario, id_residuo=residuo).update(
                                            quantidade=F('quantidade') - float(quantidade_removida))    


            messages.success(request, "Produção removida com sucesso.")
            return redirect(reverse('producoes', kwargs={'email_usuario': usuario.email}))
    
    if request.user.tipo_usuario == 'CA':
        producoes = Producao.objects.filter(id_cooperativa=usuario.cooperativa_associada)
    else:
        producoes = Producao.objects.filter(id_cooperativa=usuario.pk)
    
    catadores = Usuario.objects.filter(cooperativa_associada=usuario.pk)

    print(producoes)

    context = {
        'producoes': producoes,
        'catadores': catadores,
        'adicionar_producao_form': adicionar_producao_form,
        'remover_producao_form': remover_producao_form,
        'alterar_producao_form': alterar_producao_form,
        'aprovar_catador_form': aprovar_catador_form,
        'alterar_catador_form': alterar_catador_form,
        'excluir_catador_form': excluir_catador_form,
    }

    return render(request, 'producao/producoes.html', context)
