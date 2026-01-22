from django.urls import reverse
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Negociacao, NegociacaoPagaTrabalho, ContestacaoPreco, ContestacaoPagamento
from ..forms.forms_negociacao import (ConfirmarNegociacaoForm, 
                                      ContestarPrecoForm, ResponderContestacaoPrecoForm,
                                      ConfirmarColetaForm, ConfirmarEntregaForm,
                                      ConfirmarPagamentoForm,ContestarPagamentoForm, 
                                      ResponderContestacaoPagamentoEmpresaForm, ResponderContestacaoPagamentoCoopForm,
                                    )
from pathlib import Path

from ..utils import calcula_valor_a_receber, enviar_email_template, atualiza_producoes, atualiza_preco_medio_residuo

@login_required
def negociacoes(request, email_usuario):
    if request.user.email != email_usuario:
        return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)

    confirmar_negociacao_form = ConfirmarNegociacaoForm()
    contestar_preco_form = ContestarPrecoForm()
    confirmar_coleta_form = ConfirmarColetaForm()
    confirmar_entrega_form = ConfirmarEntregaForm()
    confirmar_pagamento_form = ConfirmarPagamentoForm(tipo_usuario=request.user.tipo_usuario)

    contestar_pagamento_form = ContestarPagamentoForm()
    
    if usuario.tipo_usuario == 'E':
        negociacoes = Negociacao.objects.filter(id_empresa=usuario.pk).exclude(status__in=('CA', 'C'))
    elif usuario.tipo_usuario == 'CO':
        negociacoes = Negociacao.objects.filter(id_cooperativa=usuario.pk).exclude(status__in=('CA', 'C'))
    else:
        negociacoes = Negociacao.objects.filter(id_cooperativa=usuario.cooperativa_associada).exclude(status__in=('CA', 'C'))

    if request.method == 'POST':
        action = request.POST.get('action')
        if 'confirmar_negociacao' in action:
            confirmar_negociacao_form = ConfirmarNegociacaoForm(request.POST)
            if confirmar_negociacao_form.is_valid():
                confirmar_negociacao_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
            
    context = {
        'negociacoes': negociacoes,
        'confirmar_negociacao_form': confirmar_negociacao_form,
        'contestar_preco_form': contestar_preco_form,
        'confirmar_coleta_form': confirmar_coleta_form,
        'confirmar_entrega_form': confirmar_entrega_form,
        'confirmar_pagamento_form': confirmar_pagamento_form,
        'contestar_pagamento_form': contestar_pagamento_form,
    }

    return render(request, 'negociacao/negociacoes.html', context)


def contestar_preco(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    tipo_usuario = request.user.tipo_usuario
    if request.method == 'POST':
        form = ContestarPrecoForm(request.POST)
        print('form: ', form)
        if form.is_valid():
            form.save(tipo_usuario=tipo_usuario)

            enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/nova_contestacao_preco.html', 'Contestação de Preço')
            enviar_email_template(negociacao.id_empresa.email, 'negociacao/nova_contestacao_preco.html', 'Contestação de Preço')
            
            return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))


def responder_contestacao_preco(request, email_usuario, id_negociacao, id_contestacao):
    contestacao = get_object_or_404(ContestacaoPreco, pk=id_contestacao)
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.method == 'POST':
        print(request.POST)
        form = ResponderContestacaoPrecoForm(request.POST)
        if form.is_valid():
            opcao = form.cleaned_data['opcoes']
            if opcao == 'contestar':
                enviar_email_template(negociacao.id_empresa.email, 'negociacao/nova_contestacao_preco.html', 'Recusa na Contestação de Preço')
                enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/nova_contestacao_preco.html', 'Recusa na Contestação de Preço')
            else:
                enviar_email_template(negociacao.id_cooperativa.email, 'negociacao/aceite_contestacao_preco.html', 'Aceite na Contestação de Preço')
                enviar_email_template(negociacao.id_empresa.email, 'negociacao/aceite_contestacao_preco.html', 'Aceite na Contestação de Preço')
            form.save(instance=contestacao, tipo_usuario=request.user.tipo_usuario)
            return redirect(reverse('detalhes_negociacao', kwargs={'email_usuario': email_usuario, 'id_negociacao': id_negociacao}))
        else:
            print(form.errors.as_data())

    return redirect(reverse('detalhes_negociacao', kwargs={'email_usuario': email_usuario, 'id_negociacao': id_negociacao}))


def confirmar_coleta(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.method == 'POST':
        form = ConfirmarColetaForm(request.POST, instance=negociacao)
        if form.is_valid():
            form.save()
            enviar_email_template(negociacao.id_cooperativa.email, 
                                  'negociacao/mudanca_status.html', 
                                  'Mudança de Status na Negociação', 
                                  context={ 'novo_status': 'Em Transporte' })
            enviar_email_template(negociacao.id_empresa.email, 
                                  'negociacao/mudanca_status.html', 
                                  'Mudança de Status na Negociação', 
                                  context={ 'novo_status': 'Em Transporte' })
            return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))


def confirmar_entrega(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.method == 'POST':
        form = ConfirmarEntregaForm(request.POST, instance=negociacao)
        if form.is_valid():
            form.save()
            enviar_email_template(negociacao.id_cooperativa.email, 
                                  'negociacao/mudanca_status.html', 
                                  'Mudança de Status na Negociação', 
                                  context={ 'novo_status': 'Aguardando Confirmação de Pagamento da Empresa' })
            enviar_email_template(negociacao.id_empresa.email, 
                                  'negociacao/mudanca_status.html', 
                                  'Mudança de Status na Negociação', 
                                  context={ 'novo_status': 'Aguardando Confirmação de Pagamento da Empresa' })
            return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))

    return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))

 
def confirmar_pagamento(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    tipo_usuario = request.user.tipo_usuario
    if request.method == 'POST':
        form = ConfirmarPagamentoForm(request.POST, request.FILES, instance=negociacao, tipo_usuario=tipo_usuario)
        if form.is_valid():
            form.save()
            if tipo_usuario == 'E':
                enviar_email_template(negociacao.id_cooperativa.email, 
                                      'negociacao/pagamento_confirmado_empresa.html', 
                                      'Pagamento Confirmado', 
                                      context={ 'nome_empresa': negociacao.id_empresa.nome })
            else:
                enviar_email_template(negociacao.id_cooperativa.email, 
                                      'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')
                enviar_email_template(negociacao.id_empresa.email, 
                                      'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')

                atualiza_producoes(negociacao.pk)
                atualiza_preco_medio_residuo(negociacao.id_residuo.pk)

            return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))
        else:
            print(form.errors.as_data())

    return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))


def contestar_pagamento(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.method == 'POST':
        form = ContestarPagamentoForm(request.POST)
        if form.is_valid():
            # Antes de criar uma nova contestação, devemos fechar contestações de pagamento anteriores, caso existam
            ContestacaoPagamento.objects.filter(id_negociacao=negociacao, status='EE').update(status='A')
            
            form.save(id_negociacao=id_negociacao)
            enviar_email_template(negociacao.id_empresa.email, 'negociacao/pagamento_contestado.html', 'Pagamento de Negociação Contestado')
            return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))    
        else:
            print(form.errors.as_data())
    
    return redirect(reverse('negociacoes', kwargs={'email_usuario': email_usuario}))


def responder_contestacao_pagamento_empresa(request, email_usuario, id_negociacao, id_contestacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.method == 'POST':
        form = ResponderContestacaoPagamentoEmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            # Antes de criar uma nova contestação, devemos fechar contestações de pagamento anteriores, caso existam
            ContestacaoPagamento.objects.filter(id_negociacao=negociacao, status='EE').update(status='A')
            form.save(id_negociacao=id_negociacao)
            enviar_email_template(negociacao.id_cooperativa.email, 
                                  'negociacao/resposta_pagamento_contestado.html',
                                  'Resposta à Contestação de Pagamento', 
                                  context={'nome_empresa': negociacao.id_empresa.nome})
        
            return redirect(reverse('detalhes_negociacao', kwargs={'email_usuario': email_usuario, 'id_negociacao': id_negociacao}))    

    return redirect(reverse('detalhes_negociacao', kwargs={'email_usuario': email_usuario, 'id_negociacao': id_negociacao}))    


def responder_contestacao_pagamento_coop(request, email_usuario, id_negociacao, id_contestacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    contestacao = get_object_or_404(ContestacaoPagamento, pk=id_contestacao)
    if request.method == 'POST':
        form = ResponderContestacaoPagamentoCoopForm(request.POST, instance=contestacao)
        if form.is_valid():
            form.save(id_negociacao=id_negociacao)
            
            if form.cleaned_data['opcoes'] == 'confirmar':
                enviar_email_template(negociacao.id_cooperativa.email, 
                                      'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')
                enviar_email_template(negociacao.id_empresa.email, 
                                      'negociacao/negociacao_concluida.html', 
                                      'Negociação Concluída')
                
                atualiza_producoes(negociacao.pk)
                atualiza_preco_medio_residuo(negociacao.id_residuo.pk)

    return redirect(reverse('detalhes_negociacao', kwargs={'email_usuario': email_usuario, 'id_negociacao': id_negociacao}))    


@login_required
def detalhes_negociacao(request, email_usuario, id_negociacao):
    
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    contestacoes_preco = ContestacaoPreco.objects.filter(id_negociacao=id_negociacao).order_by('-pk')
    contestacoes_pgto = ContestacaoPagamento.objects.filter(id_negociacao=id_negociacao).order_by('-pk')
    catadores_elegiveis = NegociacaoPagaTrabalho.objects.filter(id_negociacao=negociacao)
    valores_a_receber = calcula_valor_a_receber(id_negociacao, catadores_elegiveis)

    contestar_preco_form = ContestarPrecoForm()
    responder_contestacao_preco_form = ResponderContestacaoPrecoForm()

    contestar_pagamento_form = ContestarPagamentoForm()
    responder_contestacao_pgto_empresa_form = ResponderContestacaoPagamentoEmpresaForm() 
    responder_contestacao_pgto_coop_form = ResponderContestacaoPagamentoCoopForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if 'contestar_preco' in action:
            contestar_preco_form = ContestarPrecoForm(request.POST)
            if contestar_preco_form.is_valid():
                contestar_preco_form.save()
                return redirect('detalhes_negociacao', email_usuario=email_usuario, id_negociacao=negociacao.pk)

    # sobrescreve para o template
    producoes_para_template = {}
    i = 0
    for obj in catadores_elegiveis:
        key_name = obj.id_catador.nome
        producoes_para_template[key_name] = {
        'quantidade': obj.quantidade,
        'receber': valores_a_receber[i]
    }
        i += 1

    context = {
        'negociacao': negociacao,
        'contestacoes_preco': contestacoes_preco,
        'contestacoes_pgto': contestacoes_pgto,
        'contestar_preco_form': contestar_preco_form,
        'responder_contestacao_preco_form': responder_contestacao_preco_form,
        'confirmar_pagamento_pos_contest_form': responder_contestacao_pgto_coop_form,
        'contestar_pagamento_form': contestar_pagamento_form, 
        'responder_contestacao_pgto_empresa_form': responder_contestacao_pgto_empresa_form,
        'responder_contestacao_pgto_coop_form': responder_contestacao_pgto_coop_form,
        'producoes_individuais': producoes_para_template,        
    }

    return render(request, 'negociacao/detalhes_negociacao.html', context)


@login_required
def comprovante_negociacao(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.user != negociacao.id_cooperativa and request.user.pk != email_usuario:
        return HttpResponse("Acesso negado.", status=403)

    file_object = negociacao.comprovante
    if not file_object:
        return HttpResponse("Comprovante não anexado a esta negociação.", status=404)
    
    try:
        original_filename = Path(file_object.name).name
        download_filename = f"comprovante_{id_negociacao}_{original_filename}"
        response = FileResponse(
            file_object.open('rb'),
            content_type=file_object.file.content_type if hasattr(file_object.file, 'content_type') else 'application/octet-stream',
            as_attachment=True
        )
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        return response

    except FileNotFoundError:
        return HttpResponse("Arquivo não encontrado.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao processar o arquivo: {e}", status=500)
    

@login_required
def comprovante_contestacao(request, email_usuario, id_contestacao):
    contestacao = ContestacaoPagamento.objects.get(pk=id_contestacao)
    file_object = contestacao.comprovante
    if not file_object:
        return HttpResponse("Comprovante não anexado a esta negociação.", status=404)
    
    try:
        original_filename = Path(file_object.name).name
        download_filename = f"comprovante_{id_contestacao}_{original_filename}"
        response = FileResponse(
            file_object.open('rb'),
            content_type=file_object.file.content_type if hasattr(file_object.file, 'content_type') else 'application/octet-stream',
            as_attachment=True
        )
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        return response

    except FileNotFoundError:
        return HttpResponse("Arquivo não encontrado.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao processar o arquivo: {e}", status=500)