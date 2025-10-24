
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from users.managers import UserManager

only_digits_validator = RegexValidator(
    regex=r'^\d{10,15}$',
    message="O número deve conter apenas dígitos (entre 10 e 15)."
)
class cliente(models.IntegerChoices):
    CONSUMIDOR = 1, 'consumidor'
    EMPRESA = 2, 'empresa'

class categoria_choices(models.IntegerChoices):
    VESTUARIO = 1, 'Vestuário'
    ALIMENTACAO = 2, 'Alimentação'
    TECNOLOGIA = 3, 'Tecnologia'
    ESPORTES = 4, 'Esportes'
    
    

class User(AbstractUser):
    email = models.EmailField(unique=True)  
    username = None  
    name = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=14, blank=True, null=True)  # só empresas
    categoria = models.IntegerField(choices=categoria_choices.choices, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    phone = models.CharField(
        max_length=15,
        validators=[only_digits_validator],
        blank=True,
        null=True,
    )
    usertype = models.IntegerField(choices=cliente.choices, default=cliente.CONSUMIDOR)

    objects = UserManager()
     
    # Configuração do Django Auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        # Sincroniza username com name
        if self.name and self.username != self.name:
            self.username = self.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_usertype_display()})"
    

class Foto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='fotos/')