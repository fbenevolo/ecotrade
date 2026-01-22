"""
URL configuration for ecotrade project.

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
                    views_catador, views_demanda, views_negociacao, 
                    views_admin)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from django.conf import settings
from django.conf.urls.static import static

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
    path('dashboard/<str:email_usuario>/desativar_conta', views_admin.desativar_conta, name='desativar_conta'),
    path('dashboard/<str:email_usuario>/aceitar_desativacao', views_admin.aceitar_desativacao, name='aceitar_desativacao'),
    path('dashboard/<str:email_usuario>/recusar_desativacao', views_admin.recusar_desativacao, name='recusar_desativacao'),
    path('dashboard/<str:email_usuario>/reativar_conta', views_admin.reativar_conta, name='reativar_conta')
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views_common.home_view, name='home'),
    
    path('cadastro/', views_common.cadastro_view, name='cadastro'),
    path('login/', views_common.login_view, name='login'),
    path('logout/', views_common.logout_view, name='logout'),

    # URLs de usuário
    path('aprovacao_usuario/', views_common.aprovacao_usuario, name='aprovacao_usuario'),
    path('dashboard/<str:email_usuario>/gestao_usuarios', views_admin.gestao_usuarios, name='gestao_usuarios'),
    
    # URLs de gerenciamento de catador
    path('dashboard/<str:email_usuario>/catadores/', views_catador.catadores, name='catadores'),
    path('dashboard/<str:email_usuario>/catadores/aprovar/<str:email_catador>', views_catador.aprovar_conta_catador, name='aprovar_catador'),

    path('dashboard/<str:email_usuario>/producoes', views_producao.producoes, name='producoes'),
    path('dashboard/<str:email_usuario>/producoes/adicionar', views_producao.cadastrar_producao, name='cadastrar_producao'),
    path('dashboard/<str:email_usuario>/producoes/alterar/<int:id_producao>>', views_producao.alterar_producao, name='alterar_producao'),
    path('dashboard/<str:email_usuario>/producoes/remover/<int:id_producao>>', views_producao.remover_producao, name='remover_producao'),

    # URLs de demanda
    path('dashboard/<str:email_usuario>/demandas', views_demanda.demandas, name='demandas'),
    path('dashboard/<str:email_usuario>/demandas/cadastrar', views_demanda.cadastrar_demanda, name='cadastrar_demanda'),
    path('dashboard/<str:email_usuario>/demandas/alterar/<int:id_demanda>', views_demanda.alterar_demanda, name='alterar_demanda'),
    path('dashboard/<str:email_usuario>/demandas/excluir/<int:id_demanda>', views_demanda.excluir_demanda, name='excluir_demanda'),
    path('dashboard/<str:email_usuario>/demandas/cadastrar_atendimento/<int:id_demanda>', views_demanda.cadastrar_atendimento_demanda, name='cadastrar_atendimento_demanda'),
    path('api/demanda/preparar/<int:id_demanda>/', views_demanda.preparar_atendimento_demanda, name='preparar_atendimento_ajax'),

    # URLs de negociação
    path('dashboard/<str:email_usuario>/negociacoes', views_negociacao.negociacoes, name='negociacoes'),
    path('dashboard/<str:email_usuario>/negociacoes/detalhes_negociacao/<int:id_negociacao>', views_negociacao.detalhes_negociacao, name='detalhes_negociacao'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/contestar_preco/', views_negociacao.contestar_preco, name='contestar_preco'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/responder_contestacao/<int:id_contestacao>', views_negociacao.responder_contestacao_preco, name='responder_contestacao_preco'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/confirmar_coleta', views_negociacao.confirmar_coleta, name='confirmar_coleta'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/confirmar_entrega', views_negociacao.confirmar_entrega, name='confirmar_entrega'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/confirmar_pagamento', views_negociacao.confirmar_pagamento, name='confirmar_pagamento'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/contestar_pagamento', views_negociacao.contestar_pagamento, name='contestar_pagamento'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/responder_contestar_pagamento_empresa/<int:id_contestacao>', views_negociacao.responder_contestacao_pagamento_empresa, name='responder_contestacao_pagamento_empresa'),
    path('dashboard/<str:email_usuario>/negociacoes/<int:id_negociacao>/responder_contestar_pagamento_coop/<int:id_contestacao>', views_negociacao.responder_contestacao_pagamento_coop, name='responder_contestacao_pagamento_coop'),

    path('dashboard/<str:email_usuario>/negociacoes/comprovante/<int:id_negociacao>', views_negociacao.comprovante_negociacao, name='visualizar_comprovante_negociacao'),        
    path('dashboard/<str:email_usuario>/negociacoes/detalhes_negociacao/comprovante/<int:id_contestacao>', views_negociacao.comprovante_contestacao, name='visualizar_comprovante_contestacao'),        

    # URLs de fluxos do site
    path('dashboard/<str:email_usuario>/', views_common.dashboard, name='dashboard'),
    path('dashboard/<str:email_usuario>/historico', views_common.historico, name='historico'),
    path('dashboard/<str:email_usuario>/rendimentos', views_common.rendimentos, name='rendimentos'),
    path('dashboard/<str:email_usuario>/configuracoes', views_common.configuracoes, name='configuracoes'),
]

urlpatterns += password_reset_patterns
urlpatterns += gestao_usuarios

# ESTA CONFIGURAÇÃO SÓ É NECESSÁRIA E DEVE SER USADA EM AMBIENTE DE DESENVOLVIMENTO (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)