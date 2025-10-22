from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Negociacao
from ..forms.forms_negociacao import (ConfirmarNegociacaoForm, 
                                      ContestarPrecoForm,
                                      ConfirmarColetaForm, 
                                      ConfirmarEntregaForm,
                                      ConfirmarPagamentoForm
                                      )
from ..utils import seleciona_producoes, calcula_valor_a_receber

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

    
    if usuario.tipo_usuario == 'E':
        negociacoes = Negociacao.objects.filter(id_empresa=usuario.pk).exclude(status='C')
    else:
        negociacoes = Negociacao.objects.filter(id_cooperativa=usuario.pk).exclude(status='C')

    if request.method == 'POST':
        action = request.POST.get('action')
        if 'confirmar_negociacao' in action:
            confirmar_negociacao_form = ConfirmarNegociacaoForm(request.POST)
            if confirmar_negociacao_form.is_valid():
                confirmar_negociacao_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
        elif 'contestar_preco' in action:
            contestar_preco_form = ContestarPrecoForm(request.POST)
            if contestar_preco_form.is_valid():
                contestar_preco_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
        elif 'confirmar_coleta' in action:
            confirmar_coleta_form = ConfirmarColetaForm(request.POST)
            if confirmar_coleta_form.is_valid():
                confirmar_coleta_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
        elif 'confirmar_entrega' in action:
            confirmar_entrega_form = ConfirmarEntregaForm(request.POST)
            if confirmar_entrega_form.is_valid():
                confirmar_entrega_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
        elif 'confirmar_pagamento' in action:
            confirmar_pagamento_form = ConfirmarPagamentoForm(request.POST, request.FILES, tipo_usuario=request.user.tipo_usuario)
            if confirmar_pagamento_form.is_valid():
                confirmar_pagamento_form.save()
                return redirect(reverse('negociacoes', kwargs={'email_usuario': request.user.pk}))
            else:
                print('Nao valido')
                print(confirmar_pagamento_form.errors.as_data())


    context = {
        'negociacoes': negociacoes,
        'confirmar_negociacao_form': confirmar_negociacao_form,
        'contestar_preco_form': contestar_preco_form,
        'confirmar_coleta_form': confirmar_coleta_form,
        'confirmar_entrega_form': confirmar_entrega_form,
        'confirmar_pagamento_form': confirmar_pagamento_form
    }

    return render(request, 'negociacao/negociacoes.html', context)


@login_required
def detalhes_negociacao(request, email_usuario, id_negociacao):
    
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    catadores_elegiveis = seleciona_producoes(negociacao.demanda_associada.pk)
    valores_a_receber = calcula_valor_a_receber(id_negociacao, catadores_elegiveis)

    # sobrescreve para ser elegivel para template
    producoes_para_template = {}
    i = 0
    for producao_obj, quantidade in catadores_elegiveis.items():
        # Use the name or ID as the key, and put the entire object into the value
        key_name = producao_obj.id_catador.nome
        producoes_para_template[key_name] = {
        'producao': producao_obj,
        'quantidade': quantidade,
        'receber': valores_a_receber[i]
    }
        i += 1

    context = {
        'negociacao': negociacao,
        'catadores_envolvidos': seleciona_producoes(negociacao.demanda_associada.pk),
        'producoes_individuais': producoes_para_template,        
    }

    return render(request, 'negociacao/detalhes_negociacao.html', context)


@login_required
def comprovante(request, email_usuario, id_negociacao):
    negociacao = get_object_or_404(Negociacao, pk=id_negociacao)
    if request.user != negociacao.id_cooperativa and request.user.pk != email_usuario:
        return HttpResponse("Acesso negado.", status=403)

    file_object = negociacao.comprovante
    
    try:
        # Garante que o arquivo esteja aberto
        file_object.open('rb') 
        
        # Lê os primeiros 4 bytes para checar o tipo
        header = file_object.read(4) 
        file_object.close() 

        # 3. Define MIME type e nome do arquivo
        mime_type = 'application/octet-stream'
        filename = f"comprovante_negociacao_{id_negociacao}.bin"
        
        # Lógica de MIME Type baseada no cabeçalho
        if header == b'\x89PNG':
            mime_type = 'image/png'
            filename = f"comprovante_{id_negociacao}.png"
        elif header[:3] == b'\xff\xd8\xff': # Assinatura JPEG/JPG
            mime_type = 'image/jpeg'
            filename = f"comprovante_{id_negociacao}.jpg"
        
        # 4. Lê o arquivo INTEIRO novamente para o corpo da resposta
        # NOTA: O read(4) moveu o ponteiro. Reabra ou mova o ponteiro.
        file_object.open('rb') # Reabre o arquivo
        file_data = file_object.read()
        file_object.close()

        # 5. Cria a resposta HTTP
        response = HttpResponse(file_data, content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

    except FileNotFoundError:
        return HttpResponse("Arquivo não encontrado no servidor.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao processar o arquivo: {e}", status=500)