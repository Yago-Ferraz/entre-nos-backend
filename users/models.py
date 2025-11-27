from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from users.managers import UserManager
from django.core.validators import MaxValueValidator, MinValueValidator


# Validador de telefone
only_digits_validator = RegexValidator(
    regex=r'^\d{10,15}$',
    message="O número deve conter apenas dígitos (entre 10 e 15)."
)

# Validador de documento (CPF ou CNPJ)
document_validator = RegexValidator(
    regex=r'^\d{11}|\d{14}$',
    message="Informe um CPF (11 dígitos) ou CNPJ (14 dígitos) válido."
)

# Tipos de usuário
class Cliente(models.IntegerChoices):
    CONSUMIDOR = 1, 'consumidor'
    EMPRESA = 2, 'empresa'

# Categorias para empresas
class CategoriaChoices(models.IntegerChoices):
    VESTUARIO = 1, 'Vestuário'
    ALIMENTACAO = 2, 'Alimentação'
    TECNOLOGIA = 3, 'Tecnologia'
    ESPORTES = 4, 'Esportes'

# Model base de usuário
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    name = models.CharField(max_length=150)
    phone = models.CharField(
        max_length=15,
        validators=[only_digits_validator],
        blank=True,
        null=True
    )
    password = models.CharField(max_length=128)
    usertype = models.IntegerField(choices=Cliente.choices, default=Cliente.CONSUMIDOR)
    documento = models.CharField(
        max_length=14,
        validators=[document_validator],
        blank=True,
        null=True,
        help_text="CPF (11 dígitos) ou CNPJ (14 dígitos)"
    )
    objects = UserManager()

    # Configuração do Django Auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        if self.name and self.username != self.name:
            self.username = self.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_usertype_display()})"

# Model específico para empresas
class Empresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empresa')
    
    categoria = models.IntegerField(choices=CategoriaChoices.choices, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    meta = models.IntegerField(default=1000)
    avaliacao = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    def __str__(self):
        return f"{self.user.name} - {self.get_categoria_display() if self.categoria else 'Sem categoria'}"

class FotoEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='fotos_empresa/')

    def __str__(self):
        return f"Foto da {self.empresa.user.name}"  
    

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # grava automaticamente ao criar
    updated_at = models.DateTimeField(auto_now=True)      # atualiza sempre que salvar
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated"
    )

    class Meta:
        abstract = True