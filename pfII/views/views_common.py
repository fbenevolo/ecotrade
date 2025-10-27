from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Usuario, Negociacao, Producao, Demanda
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

            print(usuario)
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
        return redirect(reverse('dashboard', kwargs={'email_usuario': request.user.pk}))
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)    
    titulo = 'Dashboard '

    outras_infos = {} 

    if usuario.tipo_usuario == 'CO':
        negociacoes = Negociacao.objects.filter(id_cooperativa=usuario.pk, status='C')
        titulo += 'da Cooperativa'
    elif usuario.tipo_usuario == 'CA':
        negociacoes = Negociacao.objects.filter(id_cooperativa=usuario.pk, status='C')
        titulo += 'do Catador'
    
        outras_infos['rendimento_total'] = get_rendimento_total_catador(usuario, negociacoes)
    
    else:
        negociacoes = Negociacao.objects.filter(id_empresa=usuario.pk, status='C')
        titulo += 'da Empresa'

        contagem_cooperativas_unicas = negociacoes.values('id_cooperativa').distinct().count()
        outras_infos['cooperativas_unicas'] = contagem_cooperativas_unicas
    

    volume_total_residuos = sum(negociacao.quantidade for negociacao in negociacoes)
    negociacoes_ativas = len([negociacao for negociacao in negociacoes if negociacao.status == 'A'])

    context = {
        'usuario': usuario,
        'email_usuario': request.user.email,
        'titulo_dashboard': titulo,
        'volume_total_residuos': volume_total_residuos,
        'negociacoes_ativas': negociacoes_ativas,
        'outras_infos': outras_infos
    }

    return render(request, 'dashboard.html', context)


@login_required
def historico(request, email_usuario):
    if request.user.email != email_usuario:
        return redirect(reverse('historico', kwargs={'email_usuario': request.user.pk}))
    
    usuario = request.user
    if usuario.tipo_usuario == 'E':
        negociacoes_concluidas = Negociacao.objects.filter(id_empresa=usuario.pk, status='C').order_by()
    else:
        negociacoes_concluidas = Negociacao.objects.filter(id_cooperativa=usuario.pk, status='C')

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
    if request.user.email != email_usuario:
        return redirect(reverse('rendimentos', kwargs={'email_usuario': request.user.pk}))
    
    usuario = get_object_or_404(Usuario, pk=email_usuario)

    context = {
        'usuario': usuario,
        'email_usuario': request.user.email
    }

    return render(request, 'rendimentos.html', context)