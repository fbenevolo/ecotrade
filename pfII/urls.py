"""
URL configuration for pfII project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import (views_common, views_producao, 
                    views_demanda, views_negociacao, 
                    views_admin)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

password_reset_patterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='register/password_reset.html',
        email_template_name ='email/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done')), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='register/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='register/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='register/password_reset_complete.html'), name='password_reset_complete'),
]

gestao_usuarios = [
    path('dashboard/<str:email_usuario>/desativar_conta', views_common.desativar_conta, name='desativar_conta'),
    path('dashboard/<str:email_usuario>/excluir_conta', views_common.excluir_conta, name='excluir_conta'),
    path('dashboard/<str:email_usuario>/aceitar_desativacao', views_admin.aceitar_desativacao, name='aceitar_desativacao'),
    path('dashboard/<str:email_usuario>/recusar_desativacao', views_admin.recusar_desativacao, name='recusar_desativacao'),
    path('dashboard/<str:email_usuario>/aceitar_exclusao', views_admin.aceitar_exclusao, name='aceitar_exclusao'),
    path('dashboard/<str:email_usuario>/recusar_exclusao', views_admin.recusar_exclusao, name='recusar_exclusao'),
    path('dashboard/<str:email_usuario>/reativar_conta', views_admin.reativar_conta, name='reativar_conta')
]

# específico para exibir os resultados de seleção de produção de demandas
ajax_api = [
    path('api/demanda/preparar/<int:id_demanda>/', views_demanda.preparar_atendimento_ajax, name='preparar_atendimento_ajax')
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views_common.home_view, name='home'),
    path('cadastro/', views_common.cadastro_view, name='cadastro'),
    path('login/', views_common.login_view, name='login'),
    path('logout/', views_common.logout_view, name='logout'),
    path('aprovacao_usuario', views_common.aprovacao_usuario, name='aprovacao_usuario'),
    path('dashboard/<str:email_usuario>/', views_common.dashboard, name='dashboard'),
    path('dashboard/<str:email_usuario>/gestao_usuarios', views_admin.gestao_usuarios, name='gestao_usuarios'),

    path('dashboard/<str:email_usuario>/producoes', views_producao.producoes, name='producoes'),

    path('dashboard/<str:email_usuario>/demandas', views_demanda.demandas, name='demandas'),
    path('dashboard/<str:email_usuario>/negociacoes', views_negociacao.negociacoes, name='negociacoes'),
    path('dashboard/<str:email_usuario>/negociacoes/detalhes_negociacao/<int:id_negociacao>', views_negociacao.detalhes_negociacao, name='detalhes_negociacao'),
    path('dashboard/<str:email_usuario>/negociacoes/comprovante/<int:id_negociacao>', views_negociacao.comprovante, name='visualizar_comprovante'),
    path('dashboard/<str:email_usuario>/historico', views_common.historico, name='historico'),
    path('dashboard/<str:email_usuario>/rendimentos', views_common.rendimentos, name='rendimentos'),
    path('dashboard/<str:email_usuario>/configuracoes', views_common.configuracoes, name='configuracoes'),
]

urlpatterns += password_reset_patterns
urlpatterns += gestao_usuarios
urlpatterns += ajax_api