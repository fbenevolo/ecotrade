from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, OuterRef, Subquery, DecimalField, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse

from ..models import Usuario, Demanda, Producao, Negociacao, NegociacaoPagaTrabalho
from ..forms.forms_demanda import CadastrarDemandaForm, AlterarDemandaForm, CadastrarAtendimentoDemandaForm
from ..utils import seleciona_producoes, enviar_email_template

@login_required
def demandas(request, email_usuario):
    usuario = request.user
    if usuario.email != email_usuario:
        return redirect(reverse('demandas', kwargs={'email_usuario': request.user.pk}))
    
    demandas_atendiveis = [] # exclusivo para cooperativa
    
    cadastrar_demanda_form = CadastrarDemandaForm()
    alterar_demanda_form = AlterarDemandaForm()
    cadastrar_atendimento_demanda_form = CadastrarAtendimentoDemandaForm()
    
    if usuario.tipo_usuario == 'E':
        demandas = Demanda.objects.filter(id_empresa=usuario)
    else:
        demandas = Demanda.objects.all()
        
        # subquery que soma a produção da cooperativa para cada resíduo específico
        total_producao_por_residuo = Producao.objects.filter(
            id_cooperativa=usuario.email,
            id_residuo=OuterRef('id_residuo')
            ).values('id_residuo').annotate(
                total=Sum('producao')
            ).values('total')

        # dentro de Demandas, realizar a subquery e armazenar o resultado numa coluna temporária 'qtd_disponivel'
        # Coalesce trata valores NULL, transformando-os em 0 
        demandas = Demanda.objects.annotate(qtd_disponivel=Coalesce(Subquery(total_producao_por_residuo), 0, output_field=DecimalField()))
        # compara a quantidade disponível de resíduo com a quantidade pedida na demanda
        demandas_atendiveis = demandas.filter(qtd_disponivel__gte=F('quantidade'))

    context = {
        'usuario': usuario,
        'demandas': demandas,
        'demandas_atendiveis': demandas_atendiveis,
        'cadastrar_demanda_form': cadastrar_demanda_form,
        'alterar_demanda_form': alterar_demanda_form,
        'cadastrar_atendimento_demanda_form': cadastrar_atendimento_demanda_form,
    }

    return render(request, 'demanda/demandas.html', context)


@login_required
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
                                       quantidade=quantidade
                                       )
                messages.success(request, 'Demanda adicionada com sucesso')
                return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))
            except Exception as e:
                print(f'Erro ao criar demanda para empresa: {e}')
        else:
            return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))
    
    # Se alguém tentar acessar via GET, redirecione ou retorne 405
    return redirect(reverse('demandas', kwargs={'email_usuario': request.user.email}))


@login_required
def alterar_demanda(request, email_usuario, id_demanda):
    demanda = get_object_or_404(Demanda, pk=id_demanda)
    if request.method == 'POST':
        form = AlterarDemandaForm(request.POST, instance=demanda)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Demanda alterada com sucesso')
                return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))
            except Exception as e:
                print(f'Erro ao alterar demanda: {e}')
        else:
            return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))
    
    return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))


@login_required
def excluir_demanda(request, email_usuario, id_demanda):
    demanda = get_object_or_404(Demanda, pk=id_demanda)
    if demanda:
        try:
            demanda.delete()
            messages.success(request, 'Demanda excluída com sucesso')
            return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))
        except Exception as e:
            print(f'Erro ao deletar demanda: {e}')

    return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))


@login_required
def cadastrar_atendimento_demanda(request, email_usuario, id_demanda):
    demanda = get_object_or_404(Demanda, pk=id_demanda)
    if request.method == 'POST':
        form = CadastrarAtendimentoDemandaForm(request.POST)
        if form.is_valid():
            try:
                preco_inicial = form.cleaned_data['preco_inicial']
                cooperativa = get_object_or_404(Usuario, pk=request.user.email)

                # cria uma nova negociação
                id_negociacao = Negociacao.objects.create(id_empresa=demanda.id_empresa,
                                    id_cooperativa=cooperativa,
                                    id_residuo=demanda.id_residuo,
                                    quantidade=demanda.quantidade,
                                    preco=preco_inicial,
                                    confirmacao_preco_cooperativa=True,
                                    status='ACE')

                # envia emails de início de negociação
                enviar_email_template(cooperativa.email, 'negociacao/negociacao_iniciada.html', 'Negociação Iniciada')
                enviar_email_template(demanda.id_empresa.email, 'negociacao/negociacao_iniciada.html', 'Negociação Iniciada')
                
                # aloca produções à negociação
                producoes = seleciona_producoes(id_demanda)
                for (producao, quantidade) in producoes.items():
                    # se a produção não tiver sido selecionada por inteiro, aloca parte da produção atual com a quantidade selecionada
                    # e cria outra produção com o que restou
                    if producao.producao - quantidade > 0:
                        Producao.objects.create(id_cooperativa=cooperativa,
                                                id_catador=producao.id_catador,
                                                id_residuo=producao.id_residuo,
                                                status='l',
                                                data=producao.data,
                                                producao=producao.producao - quantidade)

                    producao.status = 'a'
                    producao.producao = quantidade
                    producao.id_negociacao = id_negociacao
                    producao.save()

                    # cria objetos NegociacaoPagaTrabalho
                    NegociacaoPagaTrabalho.objects.create(id_negociacao=id_negociacao,
                               id_producao=producao,
                               quantidade=quantidade,
                               id_catador=producao.id_catador)

                # exclui a demanda, já que virou uma negociação
                demanda.delete()

                messages.success(request, 'Uma negociação foi iniciada. Entre na seção de Negociações para conferir.')
                return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))

            except Exception as e:
                print(f'Erro ao tentar cadastrar atendimento à demanda: {e}')
        else:
            return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('demandas', kwargs={'email_usuario': email_usuario}))


@login_required
def preparar_atendimento_demanda(request, id_demanda):
    '''
    Função auxiliar que recupera as produções elegíveis para uma negociação,
    além do preço sugerido para a negociação, e retorna um objeto JSON com
    o preço sugerido e com os dados das produções elegíveis
    '''
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
