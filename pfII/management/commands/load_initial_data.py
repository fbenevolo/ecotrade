from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from pfII.models import Residuo, CoopDetemResiduo, Demanda, Producao
from datetime import datetime

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Cria dados iniciais do sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Populando banco com dados de teste...'))
        
        # criando usuários
        coop_email = 'coop@exemplo.com'
        empresa_email = 'empresa@exemplo.com'
        try:
            if not Usuario.objects.filter(email=coop_email).exists():
                cooperativa = Usuario.objects.create_user(
                    email=coop_email, 
                    password='postgres',
                    nome='Cooperativa Alfa',
                    tipo_usuario='CO',
                    status='A',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Usuário {cooperativa.email} criado.'))
            else:
                cooperativa = Usuario.objects.get(email=coop_email)
                
            if not Usuario.objects.filter(email=empresa_email).exists():
                empresa = Usuario.objects.create_user(
                    email=empresa_email, 
                    password='postgres',
                    nome='Empresa Beta S.A.',
                    tipo_usuario='E',
                    status='A',
                    cnpj='12.345.678/0001-90',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Usuário {empresa.email} criado.'))
            else:
                empresa = Usuario.objects.get(email=empresa_email)

            catador_email = 'catador@exemplo.com'
            if not Usuario.objects.filter(email=catador_email).exists():
                catador = Usuario.objects.create_user(
                    email=catador_email, 
                    password='postgres',
                    nome='Felipe',
                    tipo_usuario='CA',
                    cooperativa_associada=Usuario.objects.get(email=coop_email),
                    status='A',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Usuário {catador.email} criado.'))
            else:
                empresa = Usuario.objects.get(email=empresa_email)

        except IntegrityError:
            self.stdout.write(self.style.ERROR('Erro de integridade: Usuários já existem ou dados inválidos.'))
            return # Sai do script em caso de erro
        
    
        # criando produções para uma cooperativa
        try:
            cooperativa = Usuario.objects.get(email=coop_email)
            plastico = Residuo.objects.get(tipo='plastico')
            papel = Residuo.objects.get(tipo='papel')

            if not CoopDetemResiduo.objects.filter(id_cooperativa=cooperativa, id_residuo=plastico).exists():
                residuo1 = CoopDetemResiduo.objects.create(
                    id_cooperativa=cooperativa,
                    id_residuo=plastico,
                    quantidade=15
                )
                self.stdout.write(f'CoopDetemResiduo {residuo1} criado para cooperativa {coop_email}')
            else:
                residuo1 = CoopDetemResiduo.objects.filter(id_cooperativa=cooperativa, id_residuo=plastico).first()

            if not CoopDetemResiduo.objects.filter(id_cooperativa=cooperativa, id_residuo=papel).exists():
                residuo2 = CoopDetemResiduo.objects.create(
                    id_cooperativa=cooperativa,
                    id_residuo=papel,
                    quantidade=20
                )
                self.stdout.write(f'CoopDetemResiduo {residuo2} criado para cooperativa {coop_email}')
            else:
                residuo2 = CoopDetemResiduo.objects.filter(id_cooperativa=cooperativa, id_residuo=papel).first()
        except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro na criação de CoopDetemResiduo: {e}'))
                return
        
        
        # criando duas produções de catador
        try:
            cooperativa = Usuario.objects.get(email=coop_email)
            catador = Usuario.objects.get(email=catador_email)
            plastico = Residuo.objects.get(tipo='plastico')
            papel = Residuo.objects.get(tipo='papel')

            producao1_existe = Producao.objects.filter(id_cooperativa=cooperativa,
                                                       id_catador=catador,
                                                       id_residuo=plastico)
            producao2_existe = Producao.objects.filter(id_cooperativa=cooperativa,
                                                       id_catador=catador,
                                                       id_residuo=papel)
            if not producao1_existe:
                producao1 = Producao.objects.create(id_cooperativa=cooperativa,
                                                       id_catador=catador,
                                                       id_residuo=plastico,
                                                       data=str(datetime.now().date()),
                                                       producao=15)
                self.stdout.write(f'Produção {producao1} criada para cooperativas {coop_email}')
            if not producao2_existe:
                producao2 = Producao.objects.create(id_cooperativa=cooperativa,
                                                       id_catador=catador,
                                                       id_residuo=papel,
                                                       data=str(datetime.now().date()),
                                                       producao=20)
                self.stdout.write(f'Produção {producao2} criada para cooperativas {coop_email}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na criação de produções: {e}'))
            return
        
        
        # criando uma demanda para uma empresa
        try:
            empresa = Usuario.objects.get(email=empresa_email)
            plastico = Residuo.objects.get(tipo='plastico')

            if not Demanda.objects.filter(id_empresa=empresa, id_residuo=plastico).exists():
                demanda = Demanda.objects.create(   
                    id_empresa=empresa,
                    id_residuo=plastico,
                    quantidade=3,
                    status='EA'
                )   
                self.stdout.write(f'Demanda {demanda} criadas para empresa {empresa_email}')
            else:
                demanda = Demanda.objects.filter(id_empresa=empresa, id_residuo=plastico).first()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na criação de demanda: {e}'))
            return

            