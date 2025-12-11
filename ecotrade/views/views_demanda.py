from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum

from ..models import Usuario, Demanda, Producao
from ..forms.forms_demanda import (CadastrarDemandaForm, ExcluirDemandaForm,
                                   AlterarDemandaForm, CadastrarAtendimentoDemandaForm)
from ..utils import seleciona_producoes

@login_required
def demandas(request, email_usuario):
    usuario = request.user
    if usuario.email != email_usuario:
        return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
    
    demandas_atendiveis = [] # exclusivo para cooperativa
    
    cadastrar_demanda_form = CadastrarDemandaForm()
    alterar_demanda_form = AlterarDemandaForm()
    excluir_demanda_form = ExcluirDemandaForm()
    cadastrar_atendimento_demanda_form = CadastrarAtendimentoDemandaForm()
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)
    if request.method == 'POST':
        action = request.POST.get('action')
        if 'excluir_demanda' in action:
            excluir_demanda_form = ExcluirDemandaForm(request.POST)
            if excluir_demanda_form.is_valid():
                excluir_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
        # elif 'alterar_demanda' in action:
        #     alterar_demanda_form = AlterarDemandaForm(request.POST)
        #     if alterar_demanda_form.is_valid():
        #         alterar_demanda_form.save()
        #         return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
        elif 'cadastrar_atendimento_demanda' in action:
            cadastrar_atendimento_demanda_form = CadastrarAtendimentoDemandaForm(request.POST)
            if cadastrar_atendimento_demanda_form.is_valid():
                cadastrar_atendimento_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))

    if usuario.tipo_usuario == 'E':
        demandas = Demanda.objects.filter(id_empresa=usuario, status='EA')
    else:
        demandas = Demanda.objects.filter(status='EA')
        for demanda in demandas:
            filtro_residuos = Producao.objects.filter(id_residuo=demanda.id_residuo)
            sum_residuo = filtro_residuos.aggregate(total=Sum('producao'))
            qtd_residuo = sum_residuo['total'] if sum_residuo['total'] is not None else 0
            if qtd_residuo:
                if qtd_residuo >= demanda.quantidade:
                    demandas_atendiveis.append(demanda)

    context = {
        'usuario': usuario,
        'demandas': demandas,
        'demandas_atendiveis': demandas_atendiveis,
        'cadastrar_demanda_form': cadastrar_demanda_form,
        'alterar_demanda_form': alterar_demanda_form,
        'excluir_demanda_form': excluir_demanda_form,
        'cadastrar_atendimento_demanda_form': cadastrar_atendimento_demanda_form,
    }

    return render(request, 'demanda/demandas.html', context)


def cadastrar_demanda(request, email_usuario):
    if request.method == 'POST':
        form = CadastrarDemandaForm(request.POST)
        if form.is_valid():
            id_residuo = form.cleaned_data['id_residuo']
            quantidade = form.cleaned_data['quantidade']
            empresa = Usuario.objects.get(pk=email_usuario)
            try:
                Demanda.objects.create(id_empresa=empresa,
                                       id_residuo=id_residuo,
                                       quantidade=quantidade,
                                       status='EA')
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))
            except Exception as e:
                print(f'Erro ao criar demanda para empresa: {e}')
        else:
            return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))
    
    # Se alguém tentar acessar via GET, redirecione ou retorne 405
    return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))


def alterar_demanda(request, email_usuario, id_demanda):
    demanda = get_object_or_404(Demanda, pk=id_demanda)
    if request.method == 'POST':
        form = AlterarDemandaForm(request.POST, instance=demanda)
        if form.is_valid():
            try:
                form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))
            except Exception as e:
                print(f'Erro ao alterar demanda: {e}')
        else:
            return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))
    
    # Se alguém tentar acessar via GET, redirecione ou retorne 405
    return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))


@login_required
def preparar_atendimento_ajax(request, id_demanda):
    if request.method == 'GET':
        try:
            demanda = get_object_or_404(Demanda, pk=id_demanda)
            preco_sugerido = demanda.id_residuo.preco_medio  
            producoes_elegiveis = seleciona_producoes(id_demanda) 
            producoes_data = [
                {
                    'catador': producao.id_catador.nome,
                    'data': producao.data,
                    'quantidade': qtd
                    # Adicione outros campos necessários aqui
                }
                for (producao, qtd) in producoes_elegiveis.items()
            ]
            return JsonResponse({
                'success': True,
                'preco_sugerido': preco_sugerido,
                'producoes': producoes_data,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)
