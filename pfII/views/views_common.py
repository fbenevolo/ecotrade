from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from ..models import Usuario, Negociacao, NegociacaoPagaTrabalho, Producao, Demanda
from ..forms.forms_common import SignUpForm, LoginForm
from ..forms.forms_usuario import AlterarUsuarioForm
from ..utils import get_rendimento_total_catador


def home_view(request):
    return render(request, 'home.html')


def cadastro_view(request):
    if request.method == 'GET':
        cadastro_form = SignUpForm()
    else:
        cadastro_form = SignUpForm(request.POST)
        if cadastro_form.is_valid():
            try:
                cadastro_form.save()
                return redirect(reverse('aprovacao_usuario'))  
            except ValidationError as e:
                cadastro_form.add_error(None, f'Erro de validação: {e.messages}')
            except ValueError as e:#
                cadastro_form.add_error(None, "Erro ao salvar o usuário: " + str(e))
        else:
            print('Formulário inválido. Erros detalhados:')
            print(cadastro_form.errors.as_data()) 
            cadastro_form.add_error(None, "Dados inválidos — verifique os campos.")

    context = {
        'cadastro_form': cadastro_form
    }

    return render(request, 'register/cadastro.html', context)


def aprovacao_usuario(request):
    return render(request, 'gestao_usuarios/modal_aprovacao_usuario.html')


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = Usuario.objects.get(email=form.get_user())
            if usuario.status == 'A':
                login(request, usuario)
                return redirect(next_url)
            elif usuario.status == 'D':
                return render(request, 'gestao_usuarios/modal_usuario_desativado.html')
            elif usuario.status == 'EA':
                if usuario.tipo_usuario == 'CA':
                    messages.warning(request, 'Sua conta deve ser aprovada por sua cooperativa.')
                else:
                    messages.warning(request, 'Sua conta deve ser aprovada por um administrador do sistema')

        else:
            messages.error(request, "Credenciais inválidas. Verifique seu email/senha.")
    else:
        form = LoginForm(request)

    context = {
        'login_form': form,
        'next': next_url
    }

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))

@login_required
def configuracoes(request, email_usuario):
    usuario = get_object_or_404(Usuario, pk=email_usuario)
    if request.method == 'POST':
        form = AlterarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados alterados com sucesso!')
            return redirect(reverse('configuracoes', kwargs={'email_usuario': request.user.pk}))
    else:
        form = AlterarUsuarioForm(instance=usuario)

    context = {
        'form': form,
        'usuario': usuario,
        'email_usuario': request.user.email
    }

    return render(request, 'configuracoes.html', context)


@login_required
def dashboard(request, email_usuario):
    if request.user.email != email_usuario:
        # Usando request.user.pk aqui, assumindo que é o mesmo que email_usuario
        return redirect(reverse('dashboard', kwargs={'email_usuario': request.user.pk}))
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)    
    outras_infos = {} 

    if usuario.tipo_usuario == 'CO':
        negociacoes_concluidas = Negociacao.objects.filter(id_cooperativa=usuario.pk, status='C')
        negociacoes_ativas_qs = Negociacao.objects.filter(id_cooperativa=usuario.pk).exclude(status__in=['C', 'CA'])

        outras_infos['count_catadores'] = request.user.catadores.count()
    
    elif usuario.tipo_usuario == 'CA':
        cooperativa_pk = usuario.cooperativa_associada.pk if usuario.cooperativa_associada else None
        negociacoes_concluidas = Negociacao.objects.filter(id_cooperativa=cooperativa_pk, status='C')
        negociacoes_ativas_qs = Negociacao.objects.filter(id_cooperativa=cooperativa_pk).exclude(status__in=['C', 'CA'])

        outras_infos['rendimento_total'] = 0
        n_paga_t = NegociacaoPagaTrabalho.objects.filter(id_negociacao__status='C', id_catador=request.user.tipo_usuario)
        for n in n_paga_t:
             outras_infos['rendimento_total'] += n.quantidade * n.id_negociacao.preco
    else: 
        negociacoes_concluidas = Negociacao.objects.filter(id_empresa=usuario.pk, status='C')
        negociacoes_ativas_qs = Negociacao.objects.filter(id_empresa=usuario.pk).exclude(status__in=['C', 'CA'])
        
        contagem_cooperativas_unicas = negociacoes_concluidas.values('id_cooperativa').distinct().count()
        outras_infos['cooperativas_unicas'] = contagem_cooperativas_unicas
    
    volume_por_residuo_qs = negociacoes_concluidas.values('id_residuo__tipo').annotate(total_volume=Sum('quantidade')).order_by()
    volume_por_residuo_dict = { item['id_residuo__tipo']: item['total_volume'] for item in volume_por_residuo_qs }
    volumes_list = list(volume_por_residuo_dict.values())
    max_volume = max(volumes_list) if volumes_list else 1 # Define 1 para evitar divisão por zero se vazio


    negociacoes_por_mes_qs = negociacoes_concluidas.annotate(mes=TruncMonth('data_conclusao')).values('mes').annotate(total_negociacoes=Count('pk')).order_by('mes')
    negociacoes_por_mes_dict = { item['mes']: item['total_negociacoes']  for item in negociacoes_por_mes_qs if item['mes'] is not None }
    contagens_list = list(negociacoes_por_mes_dict.values())
    max_negociacoes_mes = max(contagens_list) if contagens_list else 1

    volume_total_residuos = negociacoes_concluidas.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    negociacoes_ativas = negociacoes_ativas_qs.count()

    context = {
        'usuario': usuario,
        'email_usuario': request.user.email,
        'volume_total_residuos': volume_total_residuos,
        'negociacoes_ativas': negociacoes_ativas,
        'volume_por_residuo': volume_por_residuo_dict, 
        'max_volume': max_volume,
        'negociacoes_por_mes': negociacoes_por_mes_dict,
        'max_negociacoes_mes': max_negociacoes_mes,
        'outras_infos': outras_infos
    }

    return render(request, 'dashboard.html', context)


@login_required
def historico(request, email_usuario):
    if request.user.email != email_usuario:
        return redirect(reverse('historico', kwargs={'email_usuario': request.user.pk}))
    
    usuario = request.user
    if request.user.tipo_usuario == 'E':
        negociacoes_concluidas = Negociacao.objects.filter(id_empresa=request.user.pk, status__in=('C', 'CA')).order_by()
    elif request.user.tipo_usuario == 'CO':
        negociacoes_concluidas = Negociacao.objects.filter(id_cooperativa=request.user.pk, status__in=('C', 'CA'))
    else:
        negociacoes_concluidas = Negociacao.objects.filter(id_cooperativa=request.user.cooperativa_associada, status__in=('C', 'CA'))

    context = {
        'negociacoes_concluidas': negociacoes_concluidas
    }

    return render(request, 'historico.html', context)


@login_required
def desativar_conta(request, email_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=email_usuario)
        usuario.status = 'D'
        usuario.save()
        logout(request)
        messages.success(request, 'Sua conta foi desativada com sucesso.')
        return redirect(reverse('home'))
    return redirect(reverse('configuracoes', kwargs={'email_usuario': request.user.pk}))


@login_required
def rendimentos(request, email_usuario):

    # rendimentos de negociação concluídas
    rendimentos = NegociacaoPagaTrabalho.objects.filter(id_catador=request.user.pk, id_negociacao__status='C').order_by('-id_negociacao__data_conclusao')
    total_recebido = sum([rendimento.quantidade * rendimento.id_negociacao.preco for rendimento in rendimentos]) if rendimentos else 0

    hoje = timezone.now()
    primeiro_dia_do_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    rendimentos_mes_atual = rendimentos.filter(
    id_negociacao__data_conclusao__gte=primeiro_dia_do_mes)

    resultado_total_mes = rendimentos_mes_atual.aggregate(
    soma_total_mes=Sum('quantidade'))

    soma_mes_atual = resultado_total_mes['soma_total_mes'] if resultado_total_mes['soma_total_mes'] is not None else 0

    # total de rendimento mensal
    rendimentos_por_mes = rendimentos.annotate(mes=TruncMonth('id_negociacao__data_conclusao')).values('mes').annotate(soma_quantidades=Sum('quantidade'))

    context = {
        'rendimentos': rendimentos,
        'total_recebido': total_recebido,
        'rendimento_total_mes_atual': soma_mes_atual
    }

    return render(request, 'rendimentos.html', context)