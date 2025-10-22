from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Negociacao, Producao, Demanda, CoopDetemResiduo
from ..forms.forms_demanda import (CadastrarDemandaForm, ExcluirDemandaForm,
                                   AlterarDemandaForm, CadastrarAtendimentoDemandaForm)
from ..utils import get_rendimento_total_catador, calcular_preco_sugerido, seleciona_producoes

@login_required
def demandas(request, email_usuario):
    usuario = request.user
    if usuario.email != email_usuario:
        return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
    
    demandas_atendiveis = [] # exclusivo para cooperativa
    # preco_sugerido = None
    # producoes_elegiveis = {} # exclusivo para cooperativa
    
    cadastrar_demanda_form = CadastrarDemandaForm()
    alterar_demanda_form = AlterarDemandaForm()
    excluir_demanda_form = ExcluirDemandaForm()
    cadastrar_atendimento_demanda_form = CadastrarAtendimentoDemandaForm()
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)
    if request.method == 'POST':
        action = request.POST.get('action')
        if 'cadastrar_demanda' in action:
            cadastrar_demanda_form = CadastrarDemandaForm(request.POST)
            if cadastrar_demanda_form.is_valid():
                cadastrar_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
        elif 'excluir_demanda' in action:
            excluir_demanda_form = ExcluirDemandaForm(request.POST)
            if excluir_demanda_form.is_valid():
                excluir_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
        elif 'alterar_demanda' in action:
            if alterar_demanda_form.is_valid():
                alterar_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
        elif 'cadastrar_atendimento_demanda' in action:
            cadastrar_atendimento_demanda_form = CadastrarAtendimentoDemandaForm(request.POST)
            if cadastrar_atendimento_demanda_form.is_valid():
                id_demanda = int(request.POST.get('id_demanda'))
                id_residuo = Demanda.objects.get(pk=id_demanda).id_residuo
                preco_sugerido = calcular_preco_sugerido(id_residuo)
                producoes_elegiveis = seleciona_producoes(id_demanda)
                cadastrar_atendimento_demanda_form.save()
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))


    if usuario.tipo_usuario == 'E':
        demandas = Demanda.objects.filter(id_empresa=usuario, status='EA')
    else:
        demandas = Demanda.objects.filter(status='EA')
        # filtra as demandas que a cooperativa pode atender
        for demanda in demandas:
            residuo = CoopDetemResiduo.objects.filter(id_residuo=demanda.id_residuo)
            if residuo:
                if residuo.first().quantidade >= demanda.quantidade:
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

    # if preco_sugerido:
    #     context['preco_sugerido'] = preco_sugerido
    # if producoes_elegiveis:
    #     context['producoes_elegiveis'] = producoes_elegiveis

    # print('PRODUCOES ELEGIVEIS: ', producoes_elegiveis)


    return render(request, 'demanda/demandas.html', context)


@login_required
def preparar_atendimento_ajax(request, id_demanda):
    if request.method == 'GET':
        try:
            demanda = get_object_or_404(Demanda, pk=id_demanda)
            preco_sugerido = calcular_preco_sugerido(demanda.id_residuo)
            producoes_elegiveis = seleciona_producoes(id_demanda) 
            
            # Converter o QuerySet para uma lista de dicionários serializáveis
            producoes_data = [
                {
                    'catador': producao.id_catador.nome,
                    'data': producao.data,
                    'quantidade': qtd
                    # Adicione outros campos necessários aqui
                }
                for (producao, qtd) in producoes_elegiveis.items()
            ]

            # Retorna os dados em JSON
            return JsonResponse({
                'success': True,
                'preco_sugerido': preco_sugerido,
                'producoes': producoes_data,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)
