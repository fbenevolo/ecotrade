from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O email deve ser informado")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        # busca pelo USERNAME_FIELD do model (normalmente 'email' no seu caso)
        return self.get(**{self.model.USERNAME_FIELD: username})


class Usuario(AbstractBaseUser, PermissionsMixin):
    OPCOES_STATUS = (
        ('A', 'Ativo'),
        ('EA', 'Esperando Aprovação'),
        ('D', 'Desativado'),
        ('EAD', 'Esperando Aprovação para Desativação'),
    ) 

    OPCOES_TIPO_USUARIO = (
        ('CO', 'Cooperativa'),
        ('CA', 'Catador'),
        ('E', 'Empresa'),
    )

    # Campos de Autenticação OBRIGATÓRIOS (estamos adicionando-os ao AbstractBasesUser que o Django usa)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(primary_key=True)
    nome = models.CharField()
    tipo_usuario = models.CharField(choices=OPCOES_TIPO_USUARIO, default='CO')
    status = models.CharField(choices=OPCOES_STATUS, default='A')
    cnpj = models.CharField(null=True, blank=True)
    cooperativa_associada = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='catadores',
    )

    USERNAME_FIELD = 'email'  # Campo usado para login (será o username)
    REQUIRED_FIELDS = ['nome']

    objects = UsuarioManager()

    def clean(self):
        """
        Valida os campos:
        - cnpj, se tipo_usuario == 'E'
        - cooperativa, se tipo_usuario == 'CA'
        """
        super().clean()

        errors = {}
        if self.tipo_usuario == 'E' and not self.cnpj:
            errors['cnpj'] = 'O campo CNPJ é obrigatório para o usuário do tipo Empresa'
        if self.tipo_usuario == 'CA' and not self.cooperativa_associada:
            errors['cooperativa_associada'] = 'O campo "cooperativa associada" é obrigatório para o usuário do tipo Catador'

        if errors:
            raise ValidationError(errors)
        
    def save(self, *args, **kwargs):
        try:
            self.full_clean()  # Usar full_clean() para validações
            super().save(*args, **kwargs)
        except Exception as e:
            print(f'Erro as salvar usuário: {e}')


class Residuo(models.Model):
    OPCOES_RESIDUO = (
        ('plastico', 'Plástico'),
        ('papel', 'Papel'),
        ('papelao', 'Papelão'),
        ('vidro', 'Vidro'),
        ('metais', 'Metais'),
    )

    tipo = models.CharField(primary_key=True, choices=OPCOES_RESIDUO)
    preco_medio = models.FloatField(default=0.0)


class Producao(models.Model):
    OPCOES_PRODUCAO = (
        ('l', 'Livre'),
        ('a', 'Alocada em Negociação'),
        ('z', 'Zerada')
    )


    id_cooperativa = models.ForeignKey('Usuario', 
                                       on_delete=models.SET_NULL, 
                                       null=True,
                                       related_name='catador_associado')
    id_catador = models.ForeignKey('Usuario', 
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='cooperativa_associado')
    id_residuo = models.ForeignKey('Residuo', on_delete=models.CASCADE)
    id_negociacao = models.ForeignKey('Negociacao', 
                                      null=True,
                                      on_delete=models.SET_NULL)
    status = models.CharField(choices=OPCOES_PRODUCAO, default='l')
    data = models.DateField()
    producao = models.FloatField()


class Demanda(models.Model):
    id_empresa = models.ForeignKey('Usuario', 
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='detentor_demanda')
    id_residuo = models.ForeignKey('Residuo', on_delete=models.CASCADE)
    quantidade = models.FloatField()


class Negociacao(models.Model):
    OPCOES_STATUS = (
        ('EA', 'Em Andamento'),
        ('ACC', 'Aguardando Confirmação da Cooperativa'),
        ('ACE', 'Aguardando Confirmação da Empresa'),
        ('AC', 'Aguardando Coleta'),
        ('ET', 'Em Transporte'),
        ('ACPE', 'Aguardando Confirmação de Pagamento Empresa'),
        ('ACPC', 'Aguardando Confirmação de Pagamento Coooperativa'),
        ('C', 'Concluída'),
        ('CA', 'Cancelada'),
        ('PC', 'Pagamento Contestado'),
    )

    id_empresa = models.ForeignKey('Usuario', 
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name='empresa')
    id_cooperativa = models.ForeignKey('Usuario', 
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True,
                                       related_name='cooperativa')
    id_residuo = models.ForeignKey('Residuo', 
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)
    quantidade = models.FloatField()
    preco = models.FloatField()
    confirmacao_preco_empresa = models.BooleanField(default=False)
    confirmacao_preco_cooperativa = models.BooleanField(default=False)
    status = models.CharField(choices=OPCOES_STATUS, max_length=4)
    data_coleta = models.DateField(blank=True, null=True)
    data_entrega = models.DateField(blank=True, null=True)
    data_conclusao = models.DateField(blank=True, null=True)
    confirmacao_pgto_empresa = models.BooleanField(default=False)
    confirmacao_pgto_coop = models.BooleanField(default=False)
    comprovante = models.FileField(upload_to='comprovantes/', null=True, blank=True)


class ContestacaoPreco(models.Model):
    OPCOES_STATUS = (
        ('ACE', 'Aguardando Confirmação da Empresa'), 
	    ('ACC', 'Aguardando Confirmação da Cooperativa'),
	    ('DE', 'Declinada pela Empresa'),
	    ('DC', 'Declinada pela Cooperativa'),
        ('A', 'Aceita'),
    )

    OPCOES_CONTESTADOR = (
        ('E', 'Empresa'),
        ('CO', 'Cooperativa'),
    )

    id_negociacao = models.ForeignKey('Negociacao', 
                                      on_delete=models.CASCADE, 
                                      related_name='contestacoes_preco')
    justificativa = models.TextField()
    preco_proposto = models.FloatField()
    status = models.CharField(choices=OPCOES_STATUS)
    contestador = models.CharField(choices=OPCOES_CONTESTADOR)


class ContestacaoPagamento(models.Model):
    OPCOES_STATUS = (
        ('EE', 'Em Espera'), 
        ('A', 'Aceita'),
    )

    OPCOES_USUARIO = (
        ('E', 'Empresa'),
        ('CO', 'Cooperativa'),
    )

    id_negociacao = models.ForeignKey('Negociacao', 
                                      on_delete=models.CASCADE, 
                                      related_name='contestacoes_pgto')
    justificativa = models.TextField()
    status = models.CharField(choices=OPCOES_STATUS)
    usuario = models.CharField(choices=OPCOES_USUARIO)
    comprovante = models.FileField(upload_to='comprovantes/', null=True)


class NegociacaoPagaTrabalho(models.Model):
    id_producao = models.ForeignKey('Producao', 
                                    on_delete=models.SET_NULL,
                                    null=True)
    id_negociacao = models.ForeignKey('Negociacao', 
                                      on_delete=models.SET_NULL,
                                      null=True)
    id_catador = models.ForeignKey('Usuario',
                                    on_delete=models.CASCADE,
                                    null=True)
    
    quantidade = models.FloatField()